import pandas as pd
import pathlib
from pathlib import Path
import requests
import sys
import os
import socket
import multiprocessing
from multiprocessing import Pool
import re
import time
from datetime import datetime
import warnings
import json
from refextract import extract_references_from_file, extract_references_from_url, extract_references_from_string
import pdfx
import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
import pdftotext
from tika import parser



def get_text_tika(DOI:str) -> str:
    """gets the text from a given DOI"""
    hostname = socket.gethostname()
    path = pathlib.Path(__file__).parent.absolute()
    name = hostname + str(DOI).replace("/", "") + ".pdf"
    fp = Path(path / "pdfs" / name)  # build filepath
    url = "https://www.medrxiv.org/content/" + str(DOI) + "v1.full.pdf"  # build url
    response = requests.get(url)
    fp.write_bytes(response.content)  # save .pdf
    try:
        raw = parser.from_file(str(path) + "/pdfs/" + name)
        time.sleep(2)
    except Warning:
        time.sleep(2)
        raw = parser.from_file(str(path) + "/pdfs/" + name)
    try:
        text = raw['content'].encode().decode("unicode_escape", "ignore")
        return text.lower()
    except Exception as e:
        print(e, DOI)
        return ""


def get_text_pypdf(DOI:str) -> str:
    try:
        """gets the text from a given DOI"""
        hostname = socket.gethostname()
        path = pathlib.Path(__file__).parent.absolute()
        name = hostname + str(DOI).replace("/", "") + ".pdf"
        fp = Path(path / "pdfs" / name)  # build filepath
        url = "https://www.medrxiv.org/content/" + str(DOI) + "v1.full.pdf"  # build url
        response = requests.get(url)
        fp.write_bytes(response.content)  # save .pdf

        fd = open(str(path) + "/pdfs/" + name, "rb")  # open with pdfreader
        doc = PDFDocument(fd)
        all_pages = [p for p in doc.pages()]  # get pages
        viewer = SimplePDFViewer(fd)  # use simple viwer
        text = ""
        for p in range(len(all_pages)):  # for each page
            viewer.navigate(p + 1)  # nav to page
            try:
                viewer.render()  # render -> clean and strip
                text += (u"".join(viewer.canvas.strings).encode(sys.stdout.encoding, errors='replace').decode("windows-1252")) + '\n'
            except OverflowError:
                pass
        fd.close()
        return text
    except Exception as e:
        print(e, DOI)
        return ""


def get_text_pdftotext(DOI:str) -> str:
    try:
        """gets the text from a given DOI"""
        hostname = socket.gethostname()
        path = pathlib.Path(__file__).parent.absolute()
        name = hostname + str(DOI).replace("/", "") + ".pdf"
        fp = Path(path / "pdfs" / name)  # build filepath
        url = "https://www.medrxiv.org/content/" + str(DOI) + "v1.full.pdf"  # build url
        response = requests.get(url)
        fp.write_bytes(response.content)  # save .pdf
        with open(fp, "rb") as f:
            pdf = pdftotext.PDF(f)
        text = "\n\n".join(pdf)
        f.close()
        return text.lower()
    except Exception as e:
        print(e, DOI)
        return ""


def gen_rows(df):
    """turns a pandas dataframe into a generator of row objects"""
    for index, row in df.iterrows():
        d = pd.Series(row).to_dict()
        d.pop("Unnamed: 0")  # weird key
        yield d


def return_text(row) -> str:
    text = ""
    DOI = row["DOI"]
    print("attempting pdftotext", DOI)
    text = get_text_pdftotext(DOI)
    if text == "":
        print("attempting tika", DOI)
        text = get_text_tika(DOI)
        if text == "":
            print("attempting pypdf", DOI)
            text = get_text_pypdf(DOI)
            if text == "":
                print("unreadable", DOI)
    return text


path = pathlib.Path(__file__).parent.absolute()
df = pd.read_csv(Path(path / "rxiv.csv"))
# multiprocessing.set_start_method("spawn")
# # use all CPU's
# p = Pool(os.cpu_count())
# # make the generator of dataframe
# rows = gen_rows(df)
# # start map
# p.map(get_refs, rows)
# p.close()


reg = re.compile(r"(http|ftp|https|doi)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")
count = 0
for row in gen_rows(df):
    if count == 5:
        break
    dois = []
    text = return_text(row)
    if text == "":
        continue
    print("extracting refs...", row["DOI"])
    page_split = "(which was not certified by peer review) is the author/funder, who has granted medrxiv"
    ref_section = text[text.index("references"):]
    print(re.findall(reg, ref_section))
    # for doi_match in re.finditer(reg, ref_section):
    #             # grab the string plus the OFFSET (x chars after the param_type was found)
    #             doi_unclean = ref_section[doi_match.start():doi_match.end() + 35]
    #             dois.append(doi_unclean.replace("\n", ""))
    # print(dois)
    count += 1

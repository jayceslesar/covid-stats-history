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


def find_refs(row):
    run = {}
    reg = re.compile(r"(http|ftp|https|doi)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")
    all_refs = []
    text = return_text(row)
    if text == "":
        return None
    print("extracting refs...", row["DOI"])
    try:
        ref_section = text[text.index("references"):]
        refs = re.findall(reg, ref_section)
    except ValueError:
        refs = re.findall(reg, text)
    for ref in refs:
        first = ref[0] + "://"
        second = "".join([link_part for link_part in ref[1:]])
        all_refs.append(first + second)
    all_refs = list(set(all_refs))
    for ref in all_refs:
        if str(row["DOI"]) in ref:
            all_refs.remove(ref)
            break
    if len(all_refs) > 0:
        path = pathlib.Path(__file__).parent.absolute()
        hostname = socket.gethostname()
        name = hostname + str(row["DOI"]).replace("/", "") + ".json"
        run["title"] = row["title"]
        run["DOI"] = row["DOI"]
        run["refs"] = all_refs
        with open(Path(path / "jsons" / name), 'w') as f:
            json.dump(run, f)
            f.close()
        print(run)
        print("-------------------------------------------------------------------------------------------------------")


path = pathlib.Path(__file__).parent.absolute()
df = pd.read_csv(Path(path / "R0test.csv"))
# multiprocessing.set_start_method("spawn")
# use all CPU's
p = Pool(os.cpu_count())
# make the generator of dataframe
rows = gen_rows(df)
# start map
p.map(find_refs, rows)
p.close()
to_df_all = []
print("creating df...")
for f in os.listdir(Path(path / "jsons")):
    f_actual = open(Path(path / "jsons" / f))
    to_df_all.append(json.load(f_actual))
    f_actual.close()
    os.remove(Path(path / "jsons" / f))
# make df
df = pd.DataFrame(to_df_all)
df.to_csv("r0test_refs.csv")

import requests
import pandas as pd
import pathlib
from pathlib import Path
import multiprocessing
from multiprocessing import Pool
import socket
from tika import parser
import pdfx
import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
import pdftotext
import os

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
print("reading df...")
df = pd.read_csv(Path(path / "rxiv.csv"))
print("reading df done!")
titles = df["title"].to_list()


def check_paper(row):
    hostname = socket.gethostname()
    print(hostname + " working on " + str(row["title"]))
    name = hostname + str(row["DOI"]).replace("/", "") + ".json"
    references = []
    text = return_text(str(row["DOI"]))
    if text != "":
        for title in titles:
            if title in text:
                references.append(title)
        if len(references) > 0:
            to_file = {row["title"]: references}
            print(to_file)
            with open(Path(path / "jsons" / name), 'w') as f:
                json.dump(to_file, f)
                f.close()
        else:
            print("no refs found")

print("starting pool")
p = Pool(os.cpu_count())
print("generating rows...")
rows = gen_rows(df)
print("rows generated!")
print("starting map....")
p.map(check_paper, rows)
p.close()

print("joining files...")
adjacency = []
for f in os.listdir(Path(path / "jsons")):
    f_actual = open(Path(path / "jsons" / f))
    adjacency.append(json.load(f_actual))
    f_actual.close()
    os.remove(Path(path / "jsons" / f))

with open('refs.txt', 'w') as f:
    for item in adjacency:
        f.write("%s\n" % item)
    f.close()
print("done!")
print(adjacency)






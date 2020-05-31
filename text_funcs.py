import requests
from pathlib import Path
import sys
import glob
import win32com.client
import os
import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
from threading import Timer  # will use to determine if the thing is stuck on images or not hopefully


def get_text(DOI:str) -> str:
    txt = ""
    name = "curr."
    fp = Path(Path.cwd() / "pdfs" / "curr.pdf")  # build filepath
    url = "https://www.medrxiv.org/content/" + DOI + "v1.full.pdf"  # build url
    response = requests.get(url)
    fp.write_bytes(response.content)  # save .pdf
    
    fd = open(r"pdfs\curr.pdf", "rb")  # open with pdfreader
    doc = PDFDocument(fd)
    all_pages = [p for p in doc.pages()]  # get pages
    viewer = SimplePDFViewer(fd)  # use simple viwer

    for p in range(len(all_pages)):  # for each page
        viewer.navigate(p + 1)  # nav to page
        viewer.render()  # render -? clean and strip
        txt += (u"".join(viewer.canvas.strings).encode(sys.stdout.encoding, errors='replace').decode("windows-1252")) + '\n' 

    return txt



# DOI = "10.1101/2020.05.15.20102863"
# print(get_text(DOI))

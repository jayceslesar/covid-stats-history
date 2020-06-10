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
from refextract import extract_references_from_file, extract_references_from_url
import pdfx



def get_refs_file(fp) -> list:
    return extract_references_from_file(fp)


def get_refs_web(url) -> list:
    return extract_references_from_url(url)


def get_refs_doi(DOI) -> list:
    hostname = socket.gethostname()
    path = pathlib.Path(__file__).parent.absolute()
    name = hostname + str(DOI).replace("/", "") + ".pdf"
    fp = Path(path / "pdfs" / name)  # build filepath
    url = "https://www.medrxiv.org/content/" + str(DOI) + "v1.full.pdf"  # build url
    response = requests.get(url)
    fp.write_bytes(response.content)
    pdf = pdfx.PDFx(fp)
    references_dict = pdf.get_references_as_dict()
    return references_dict


print(get_refs_doi("10.1101/2020.05.21.20108621"))
from tika import parser
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


def get_text(DOI:str) -> str:
    """gets the text from a given DOI, will need to add in a database var soon as it will be different"""
    hostname = socket.gethostname()
    path = pathlib.Path(__file__).parent.absolute()
    name = hostname + DOI.replace("/", "") + ".pdf"
    fp = Path(path / "pdfs" / name)  # build filepath
    url = "https://www.medrxiv.org/content/" + DOI + "v1.full.pdf"  # build url
    response = requests.get(url)
    fp.write_bytes(response.content)  # save .pdf
    raw = parser.from_file(str(path) + "/pdfs/" + name)
    time.sleep(2)
    text = raw['content'].encode().decode('unicode_escape')
    return text.lower()

get_text("10.1101/2020.05.24.20111807")
hostname = socket.gethostname()
path = pathlib.Path(__file__).parent.absolute()
name = hostname + "10.1101/2020.05.24.20111807".replace("/", "") + ".pdf"
fp = Path(path / "pdfs" / name)  # build filepath
if os.path.isfile(fp):
    print("delete")
    os.remove(fp)
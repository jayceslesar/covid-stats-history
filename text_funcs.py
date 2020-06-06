from tika import parser
import pandas as pd
import pathlib
from pathlib import Path
import requests
import sys
import socket


def get_text(DOI:str) -> str:
    hostname = socket.gethostname()
    path = pathlib.Path(__file__).parent.absolute()
    name = hostname + "curr.pdf"
    fp = Path(path / "pdfs" / str(name))  # build filepath
    url = "https://www.medrxiv.org/content/" + DOI + "v1.full.pdf"  # build url
    response = requests.get(url)
    fp.write_bytes(response.content)  # save .pdf  # BUG::writes encoded characters as bytes and reads them incorrectly !?!?!?
    
    raw = parser.from_file(str(path) + "/pdfs/" + str(hostname) + "curr.pdf")
    txt = raw['content'].encode().decode('unicode_escape')

    return txt



# DOI = "10.1101/2020.05.15.20102863"
# print(get_text(DOI))

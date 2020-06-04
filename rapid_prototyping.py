from tika import parser
import pandas as pd
from pathlib import Path
import requests
import sys

# def get_text(DOI:str) -> str:
#     txt = ""
#     name = "curr."
#     fp = Path(Path.cwd() / "pdfs" / "curr.pdf")  # build filepath
#     url = "https://www.medrxiv.org/content/" + DOI + "v1.full.pdf"  # build url
#     response = requests.get(url)
#     fp.write_bytes(response.content)  # save .pdf  # BUG::writes encoded characters as bytes and reads them incorrectly !?!?!?

#     raw = parser.from_file(r"pdfs\curr.pdf")
#     print(raw['content'].encode("utf-8"))



# df = pd.read_csv("rxiv.csv")
# for index, row in df.iterrows():
#     get_text(row["DOI"])


x  = b"Reproductive number of COVID-19: A systematic review and meta-analysis based on global"
print(x.decode("latiin1"))
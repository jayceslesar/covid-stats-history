import requests
from pathlib import Path
import docx
import sys
import glob
import win32com.client
import os


# !! ONLY WORKS IF WORD IS INSTALLED ON MACHINE -> could run tets with LibreOffice but will need time to play around
# gets the .pdf from DOI, save convert to .docx and return text
def get_text(DOI:str) -> str:
    name = "curr."
    fp = Path(Path.cwd() / "pdfs" / "curr.pdf")  # build filepath
    url = "https://www.medrxiv.org/content/" + DOI + "v1.full.pdf"  # build url
    response = requests.get(url)
    fp.write_bytes(response.content)  # save .pdf
    
    word = win32com.client.Dispatch("Word.Application")
    word.visible = 0
    pdfs_path = "" # folder where the .pdf files are stored
    for i, doc in enumerate(glob.iglob(pdfs_path + "*.pdf")):
        print(doc)
        filename = doc.split('\\')[-1]
        in_file = os.path.abspath(doc)
        print(in_file)
        wb = word.Documents.Open(in_file)
        out_file = os.path.abspath(Path(Path.cwd() / "pdfs" / "curr.docx"))
        print("outfile\n",out_file)
        wb.SaveAs2(out_file, FileFormat=16) # file format for docx
        print("success...")
        wb.Close()
    word.Quit()


    doc = docx.Document(Path(Path.cwd() / "pdfs" / "curr.docx"))  # build path
    full_text = []  # store text
    for para in doc.paragraphs:
        fullText.append(para.text.encode(sys.stdout.encoding, errors='replace'))  # fix encodings and append
    return b'\n'.join(full_text).decode('windows-1252')  # one final decode


# DOI = "10.1101/2020.04.08.20058487"
# print(get_text(DOI))

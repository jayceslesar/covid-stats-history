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
import warnings
import json
import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
import pdftotext


# which ones site each other

def no_bad_keywords(keywords:list, text:str):
    for keyword in keywords:
        if keyword in text:
            return False
    return True


def delete_file(fp):
    if os.path.isfile(fp):
        os.remove(fp)


def time_f():
    """prints the time to track functions in the console"""
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)


def gen_rows(df):
    """turns a pandas dataframe into a generator of row objects"""
    for index, row in df.iterrows():
        d = pd.Series(row).to_dict()
        d.pop("Unnamed: 0")  # weird key
        yield d


def get_text_tika(DOI:str) -> str:
    """gets the text from a given DOI, will need to add in a database var soon as it will be different"""
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
        """gets the text from a given DOI, will need to add in a database var soon as it will be different"""
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
        """gets the text from a given DOI, will need to add in a database var soon as it will be different"""
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


def process_text(row) -> dict:
    """processes the pdfs and handles matches and returning data"""
    run = {}
    text = get_text_pdftotext(row["DOI"])
    if text == "":
        text = get_text_tika(row["DOI"])
        if text == "":
            text = get_text_pypdf(row["DOI"])
    hostname = socket.gethostname()
    path = pathlib.Path(__file__).parent.absolute()
    name = hostname + str(row["DOI"]).replace("/", "") + ".pdf"
    fp = Path(path / "pdfs" / name)  # build filepath
    try:
        delete_file(fp)
    except PermissionError:
        time.sleep(1)
        delete_file(fp)
        pass
    # get search params TODO::make adaptable
    search_params = {"R0": ["R0=", "R0 =", "R0", "R0,", "reproductive number", "average estimated reproductive number"]}
    bad_r0_keywords = ["above", "below", "sars-", "19", "2–4", "c5"]
    R0_LOWER_BOUND = 0.9
    R0_UPPER_BOUND = 6.5
    OFFSET = 25
    string_matches = []
    float_matches = []
    final_matches = []
    # search each paramater
    for param_type in search_params["R0"]:
        if param_type.lower() in text:
            # search each subparamater
            # regex
            for param_type_match in re.finditer(param_type.lower(), text):
                # grab the string plus the OFFSET (x chars after the param_type was found)
                potential_match_string = text[param_type_match.start():param_type_match.end() + OFFSET]
                # if param_type_match is not at the end of a sentence, grab it
                try:
                    if potential_match_string[potential_match_string.index(param_type) + len(param_type) + 1] != '.':
                        if no_bad_keywords(bad_r0_keywords, potential_match_string):
                            if not bool(re.search(r'\[\d+\]', potential_match_string)):
                                string_matches.append(potential_match_string)
                except ValueError:
                    pass
    # strip all the flaots out
    # \s[-+]?\d*.\d+\s between whitespace
    float_finder = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
    for string_match in string_matches:
    # appends a list of floats or an empty list
        float_matches = re.findall(float_finder, string_match)
        for f in float_matches:
            if "." in str(f[0]):
                final_matches.append(f[0])
    if len(final_matches) > 0:
        print("---------------------------------------------------------------------------------")
        print(row["title"])
        print(string_matches)
        final_matches = list(set(final_matches))
        print("R0 Found", final_matches)
        run["title"] = row["title"]
        run["DOI"] = row["DOI"]
        run["abstract"] = row["abstract"]
        run["pre_print_release_date"] = row["pre_print_release_date"]
        run["publisher"] = row["publisher"]
        run["authored_by"] = row["authored_by"]
        run["R0"] = final_matches
        # fill in others...
        run["database"] = row["database"]
        run["flag"] = ""
        # write to file
        name = hostname + str(row["DOI"]).replace("/", "") + ".json"
        with open(Path(path / "jsons" / name), 'w') as f:
            json.dump(run, f)
            f.close()


def main():
    # pathing and dirs
    path = pathlib.Path(__file__).parent.absolute()
    if not os.path.isdir(Path(path / "pdfs")):
        os.mkdir(Path(path / "pdfs"))
    if not os.path.isdir(Path(path / "jsons")):
        os.mkdir(Path(path / "jsons"))
    # read
    df = pd.read_csv(Path(path / "rxiv.csv"))
    # explicit spawn for unix
    multiprocessing.set_start_method("spawn")
    # use all CPU's
    p = Pool(os.cpu_count())
    # make the generator of dataframe
    rows = gen_rows(df)
    # start map
    p.map(process_text, rows)
    p.close()
    # for row in rows:
    #     process_text(row)
    to_df_all = []
    for f in os.listdir(Path(path / "jsons")):
        f_actual = open(Path(path / "jsons" / f))
        to_df_all.append(json.load(f_actual))
        f_actual.close()
        os.remove(Path(path / "jsons" / f))
    # make df
    df = pd.DataFrame(to_df_all)
    df.to_csv("mined.csv")


if __name__ == "__main__":
    time_f()
    main()
    time_f()
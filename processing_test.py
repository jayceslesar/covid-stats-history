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
from datetime import datetime

def time_f():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)


def gen_rows(df):
    for index, row in df.iterrows():
        d = pd.Series(row).to_dict()
        d.pop("Unnamed: 0")  # weird key
        yield d

def get_text(DOI:str) -> str:
    hostname = socket.gethostname()
    path = pathlib.Path(__file__).parent.absolute()
    name = hostname + DOI.replace("/", "") + ".pdf"
    fp = Path(path / "pdfs" / name)  # build filepath
    url = "https://www.medrxiv.org/content/" + DOI + "v1.full.pdf"  # build url
    response = requests.get(url)
    fp.write_bytes(response.content)  # save .pdf
    raw = parser.from_file(str(path) + "/pdfs/" + name)
    text = raw['content'].encode().decode('unicode_escape')
    os.remove(fp)
    return text


def process_text(row) -> dict:
    run = {}
    text = get_text(row["DOI"])
    # get search params TODO::make adaptable
    search_params = {"R0": ["R0=", "R0 =", "R0", "reproductive number"]}
    R0_LOWER_BOUND = 0.9
    R0_UPPER_BOUND = 6.5
    OFFSET = 10
    string_matches = []
    float_matches = []
    final_matches = []
    # search each paramater
    for param in search_params.keys():
        if param in text:
            # search each subparamater
            for param_type in search_params[param]:
                # regex
                for param_type_match in re.finditer(param_type, text):
                    # grab the string plus the OFFSET (x chars after the param_type was found)
                    potential_match_string = text[param_type_match.start():param_type_match.end() + OFFSET]
                    # if param_type_match is not at the end of a sentence, grab it
                    if potential_match_string[potential_match_string.index(param_type) + len(param_type) + 1] != '.':
                        string_matches.append(potential_match_string)
    # strip all the flaots out
    float_finder = re.compile(r"[-+]?\d*\.\d+|\d+")
    for string_match in string_matches:
                # appends a list of floats or an empty list
                float_matches.append(re.findall(float_finder, string_match))
    for float_list in float_matches:
        if len(float_list) > 0:
            for float_match in float_list:
                f = float(float_match)
                if f > R0_LOWER_BOUND and f < R0_UPPER_BOUND:
                    final_matches.append(f)
    print("-----------------------------------------------------------------------------------------------------------------------")
    print(row["title"])
    if len(final_matches) > 0:
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
                return run


if __name__ == '__main__':
    time_f()
    path = pathlib.Path(__file__).parent.absolute()
    df = pd.read_csv(Path(path / "rxiv.csv"))
    G = gen_rows(df)
    p = Pool(os.cpu_count())
    to_df = p.map(process_text, G)
    print(to_df)
    time_f()
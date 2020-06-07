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
    text = raw['content'].encode().decode('unicode_escape')
    os.remove(fp)
    return text.lower()


def process_text(row, to_df:list) -> dict:
    """processes the pdfs and handles matches and returning data"""
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
        if param.lower() in text:
            # search each subparamater
            for param_type in search_params[param]:
                # regex
                for param_type_match in re.finditer(param_type.lower(), text):
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
                # add to shared list
                to_df.append(run)


def main():
    # get path and read input csv
    path = pathlib.Path(__file__).parent.absolute()
    df = pd.read_csv(Path(path / "rxiv.csv"))
    # start a manager to share output on processes
    manager = multiprocessing.Manager()
    to_df = manager.list()
    p = Pool(os.cpu_count())
    jobs = []
    # make the generator of dataframe
    rows = gen_rows(df)
    # start each process
    for row in rows:
        try:
            p = multiprocessing.Process(target=process_text, args=(row, to_df))
            jobs.append(p)
            p.start()
        except Exception as e:
            print("EXCEPTION", e)
            try:
                os.remove(fp)
            except:
                pass
            pass
    # join each process
    for proc in jobs:
        proc.join()

    df_out = pd.DataFrame(to_df)
    df.to_csv(Path(path / "mined.csv"))


if __name__ == "__main__":
    time_f()
    main()
    time_f()
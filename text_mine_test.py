import pandas as pd
import text_funcs
import re
import json
from datetime import datetime
import pathlib
from pathlib import Path
import sys


def find_values(of_name, OFFSET):
    offset = int(OFFSET)
    new = []

    # "reproductive number", "Basic reproductive number"
    # "Latent period prior to infectivity"
    # "Duration of infectivity"

    # paramater and paramater permutation data
    search_params = {"R0": ["R0=", "R0 =", "R0", "reproductive number"]}
    R0_LOWER_BOUND = 0.9
    R0_UPPER_BOUND = 6.5
    # save output incase pandas save goes wrong
    d = {}
    float_finder = re.compile(r"[-+]?\d*\.\d+|\d+")  # regex for float
    path = pathlib.Path(__file__).parent.absolute()
    df = pd.read_csv(Path(path / "rxiv.csv"))
    for index, row in df.iterrows():
        run = {}
        # store first gen matches (text)
        matches = []
        try:
            print(index, row["title"])
            # get the text
            text = text_funcs.get_text(row["DOI"])
            # try each search param
            for p in search_params.keys():
                if p in text:
                    # each paramater permutation
                    for p_mod in search_params[p]:
                        # look for each permutation in text
                        for match in re.finditer(p_mod, text):
                            # grab the start of it to the end of it and then offset
                            potential = text[match.start():match.end() + offset]
                            # if the search query is not at the end of a sentence
                            if potential[potential.index(p_mod) + len(p_mod) + 1] != '.':
                                # grab text
                                matches.append(potential)
                            
            # store second gen matches (numbers)
            new_matches = []
            # strip numbers out of text
            for m in matches:
                new_matches.append(re.findall(float_finder, m))
            # store third gen matches (filtered numbers)
            actual_matches = []
            # filter the numbers by bound and make sure they are a float
            for ms in new_matches:
                if len(ms) > 0:
                    for m in ms:
                        if '.' in m and float(m) > R0_LOWER_BOUND and float(m) < R0_UPPER_BOUND:
                            actual_matches.append(float(m))
            # remove dupes and turn into list
            actual_matches = list(set(actual_matches))
            if len(actual_matches) != 0:
                print("R0 Found", actual_matches)
                run["title"] = row["title"]
                run["DOI"] = row["DOI"]
                run["abstract"] = row["abstract"]
                run["pre_print_release_date"] = row["pre_print_release_date"]
                run["publisher"] = row["publisher"]
                run["authored_by"] = row["authored_by"]
                run["R0"] = actual_matches
                # fill in others...
                run["database"] = row["database"]
                run["flag"] = ""
                new.append(run)
                d[row["DOI"]] = actual_matches

        except Exception as e:
            print("EXCEPTION", e)
            pass
        print("------------------------------------------------------------------------------------------------")


    new = pd.DataFrame(new)
    of = of_name + ".csv"
    new.to_csv(Path(path / of))



now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time)
find_values(sys.argv[1], sys.argv[2])
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time)
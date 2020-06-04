import pandas as pd
import text_funcs
import warnings
import re
import json


warnings.filterwarnings("ignore")


# "reproductive number", "Basic reproductive number"
# "Latent period prior to infectivity"
# "Duration of infectivity"

search_params = {"R0": ["R0=", "R0 =", "R0", "reproductive number"]}
R0_LOWER_BOUND = 0.9
R0_UPPER_BOUND = 6.5
d = {}
float_finder = re.compile(r"[-+]?\d*\.\d+|\d+")  # regex for float

df = pd.read_csv("rxiv.csv")
for index, row in df.iterrows():
    try:
        print(index, row["title"])
        text = text_funcs.get_text(row["DOI"])
        for p in search_params.keys():
            matches = []
            if p in text:
                for p_mod in search_params[p]:
                    for match in re.finditer(p_mod, text):
                        potential = text[match.start():match.end() + 20]
                        if potential[potential.index(p_mod) + len(p_mod) + 1] == '.':
                            continue
                        matches.append(potential)
                new_matches = []
                for m in matches:
                    new_matches.append(re.findall(float_finder, m))
                actual_matches = []
                for ms in new_matches:
                    if len(ms) > 0:
                        for m in ms:
                            if '.' in m and float(m) > R0_LOWER_BOUND and float(m) < R0_UPPER_BOUND:
                                actual_matches.append(float(m))
                actual_matches = list(set(actual_matches))
                if len(actual_matches) == 0:
                    continue
                print("R0 Found", actual_matches)
            row["R0"] = actual_matches
            d[row["DOI"]] = actual_matches
    except Exception as e:
        print("EXCEPTION", e)
        pass
    print("------------------------------------------------------------------------------------------------")

try:
    print(d)
except:
    try:
        for paper in d.keys():
            print(paper, d[paper])
    except:
        print(paper, "Failed")
        pass

df.to_csv("R0.csv")
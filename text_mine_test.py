import pandas as pd
import text_funcs
import warnings
import re
import json


warnings.filterwarnings("ignore")


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

df = pd.read_csv("rxiv.csv")
for index, row in df.iterrows():
    try:
        print(index, row["title"])
        # get the text
        text = text_funcs.get_text(row["DOI"])
        # try each search param
        for p in search_params.keys():
            # store first gen matches (text)
            matches = []
            if p in text:
                # each paramater permutation
                for p_mod in search_params[p]:
                    # look for each permutation in text
                    for match in re.finditer(p_mod, text):
                        # grab the start of it to the end of it and then offset
                        OFFSET = 20
                        potential = text[match.start():match.end() + OFFSET]
                        # if the search query is at the end of a sentence ignore it
                        if potential[potential.index(p_mod) + len(p_mod) + 1] == '.':
                            continue
                        # else it is a match
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
                # remove dupes anmd turn into list
                actual_matches = list(set(actual_matches))
                # skip if the size of the list iz zero
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
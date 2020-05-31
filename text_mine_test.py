import pandas as pd
import text_funcs
import warnings


warnings.filterwarnings("ignore")


# "reproductive number", "Basic reproductive number"
# "Latent period prior to infectivity"
# "Duration of infectivity"
first = "R0="
second = "R0 ="
df = pd.read_csv("rxiv.csv")
for index, row in df.iterrows():
    try:
        text = text_funcs.get_text(row["DOI"])
        if "R0" not in text:  # if it isn't there skip
            continue
        print(row["title"])
        if first in text:  # TODO::make regex searches and findall's
            print("R0 found...")
            i = text.index(first)
            print(text[i:i + len(first) + 8])
        if second in text:
            print("R0 found...")
            i = text.index(second)
            print(text[i:i + len(second) + 8])
        else:
            print("Not found")
    except Exception as e:
        print("EXCEPTION", e)
        pass
    print("------------------------------------------------------------------------------------------------------------------")
import pandas as pd
import text_funcs



first = "R0="
second = "R0 ="
df = pd.read_csv("rxiv.csv")
for index, row in df.iterrows():
    text = text_funcs.get_text(row["DOI"])
    if first in text:
        i = text.index(first)
        print("R0", text[i:i + len(first) + 3])
    if second in text:
        i = text.index(second)
        print("R0", text[i:i + len(first) + 3])
    else:
        print("Not found")
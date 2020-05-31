import pandas as pd
import text_funcs



first = "R0="
second = "R0 ="
df = pd.read_csv("rxiv.csv")
for index, row in df.iterrows():
    try:
        print(row["title"])
        text = text_funcs.get_text(row["DOI"])
        print("R0" in text)
        if first in text:
            print("R0 found...")
            i = text.index(first)
            print("R0", text[i:i + len(first) + 3])
        if second in text:
            print("R0 found...")
            i = text.index(second)
            print("R0", text[i:i + len(second) + 3])
        else:
            print("Not found")
    except Exception as e:
        print(e)
        pass
    print("------------------------------------------------------------------------------------------------------------------")
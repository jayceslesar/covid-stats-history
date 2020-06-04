import pandas as pd
import json

with open('fixpd.json') as f: 
    s = f.read()
    s = s.replace("\'", "\"")
    data = json.loads(s)
f.close()



rxiv = pd.read_csv('rxiv.csv')

for d in data:
    print(d, data[d])



# for index, row in rxiv.iterrows():
#     for d in data:
#         if d == row["DOI"]:
#             if len(data[d]) < 1:
#                 continue
#             rxiv.loc[index, "R0"] = str(data[d])
#             continue

# for index, row in rxiv.iterrows():
#     if type(row["R0"]) == 'float':
#         rxiv.drop(index, inplace=True)

# rxiv.to_csv("R0.csv")
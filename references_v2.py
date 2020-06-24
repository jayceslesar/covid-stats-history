import requests
import pandas as pd
from pathlib import Path
from extract_references import return_text, gen_rows
import multiprocessing
from multiprocessing import Pool
import socket



path = pathlib.Path(__file__).parent.absolute()
df = pd.read_csv(Path(path / "all_rxiv.csv"))
titles = df["title"].to_list()


def check_paper(row):
    hostname = socket.gethostname()
    name = hostname + str(row["DOI"]).replace("/", "") + ".json"
    references = []
    text = return_text(str(row["DOI"]))
    if text != "":
        for title in titles:
            if title in text:
                references.append(title)
        if len(references) > 0:
            to_file = {row["title"]: references}
            print(to_file)
            with open(Path(path / "jsons" / name), 'w') as f:
                json.dump(to_file, f)
                f.close()
        else:
            print("no refs found")


p = Pool(os.cpu_count())
rows = gen_rows(df)
p.map(check_paper, rows)
p.close()

adjacency = []
for f in os.listdir(Path(path / "jsons")):
    f_actual = open(Path(path / "jsons" / f))
    adjacency.append(json.load(f_actual))
    f_actual.close()
    os.remove(Path(path / "jsons" / f))

with open('refs.txt', 'w') as f:
    for item in adjacency:
        f.write("%s\n" % item)
    f.close()






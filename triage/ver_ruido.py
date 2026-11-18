import csv
import json

with open("data/rotulados.csv") as f:
    for l in csv.DictReader(f):
        if l["rotulo"] != "fora_do_gabarito":
            continue
        with open(f"cache/v1/{l['indice']}.json") as c:
            v = json.load(c)
        if v["veredito"] == "incidente":
            print(l["indice"], l["hora"], l["regra"], "|", v["justificativa"][:150])

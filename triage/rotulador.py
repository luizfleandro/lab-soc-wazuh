import csv
import json
from collections import Counter
from datetime import datetime, timezone, timedelta

ARQUIVO = "data/raw/ossec-alerts-16.json"
SAIDA = "data/rotulados.csv"
BRASIL = timezone(timedelta(hours=-3))

# (cenário, rótulo, início, fim, regras), horário do MANAGER, no horário do Brasil
JANELAS = [
    ("V00", "incidente",      "10:10:00", "10:16:30", {"5710", "5503", "2502", "5712"}),
    ("C01", "incidente",      "10:31:00", "10:32:30", {"5902", "5402"}),
    ("C02", "incidente",      "10:41:30", "10:43:00", {"2832"}),
    ("L01", "falso_positivo", "11:13:00", "11:14:00", {"5402"}),
    ("L02", "falso_positivo", "11:14:30", "11:15:20", {"5402"}),
    ("L03", "falso_positivo", "11:15:25", "11:15:45", {"5557", "5503", "2501"}),
]


def rotular(hora, regra):
    for cenario, rotulo, inicio, fim, regras in JANELAS:
        if inicio <= hora <= fim and regra in regras:
            return cenario, rotulo
    return "-", "fora_do_gabarito"


with open(ARQUIVO) as f:
    alertas = [json.loads(linha) for linha in f]

linhas = []
for indice, a in enumerate(alertas):
    if a["agent"]["id"] == "000":
        continue
    hora_utc = datetime.strptime(a["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
    hora = hora_utc.astimezone(BRASIL).strftime("%H:%M:%S")
    regra = a["rule"]["id"]
    cenario, rotulo = rotular(hora, regra)
    linhas.append({
        "indice": indice,
        "hora": hora,
        "regra": regra,
        "level": a["rule"]["level"],
        "cenario": cenario,
        "rotulo": rotulo,
    })

with open(SAIDA, "w", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=linhas[0].keys())
    escritor.writeheader()
    escritor.writerows(linhas)

print(f"{len(linhas)} alertas rotulados em {SAIDA}\n")
for (cenario, rotulo), qtd in sorted(Counter((l["cenario"], l["rotulo"]) for l in linhas).items()):
    print(f"  {cenario:4} {rotulo:17} {qtd}")

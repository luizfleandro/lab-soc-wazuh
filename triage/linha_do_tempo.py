import json
from datetime import datetime, timezone, timedelta

ARQUIVO = "data/raw/ossec-alerts-16.json"
BRASIL = timezone(timedelta(hours=-3))

# regras que são ruído de fundo, sem relação com os cenários
RUIDO = {"510", "5501", "5502", "52002", "501", "502", "506"}

with open(ARQUIVO) as f:
    alertas = [json.loads(linha) for linha in f]

for a in alertas:
    if a["agent"]["id"] == "000":  # alertas do próprio manager
        continue
    if a["rule"]["id"] in RUIDO:
        continue

    hora_utc = datetime.strptime(a["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
    hora_br = hora_utc.astimezone(BRASIL).strftime("%H:%M:%S")

    regra = a["rule"]
    log = a.get("full_log", "")[:90]
    print(f"{hora_br} | {regra['id']:>5} | {regra['level']:>2} | {regra['description'][:45]:45} | {log}")

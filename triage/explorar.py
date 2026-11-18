import json
from collections import Counter

ARQUIVO = "data/raw/ossec-alerts-16.json"

alertas = []
with open(ARQUIVO) as f:
    for linha in f:
        alertas.append(json.loads(linha))

print("Total de alertas:", len(alertas))

por_agente = Counter(a["agent"]["name"] for a in alertas)
print("\nAlertas por agente:")
for nome, qtd in por_agente.most_common():
    print(f"  {qtd:4}  {nome}")

por_regra = Counter(
    (a["rule"]["id"], a["rule"]["level"], a["rule"]["description"])
    for a in alertas
)
print("\nAlertas por regra (qtd | id | level | descrição):")
for (rid, nivel, desc), qtd in por_regra.most_common():
    print(f"  {qtd:4} | {rid:>6} | {nivel:>2} | {desc}")

import copy
import json
from collections import Counter
from statistics import mean

import anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from triagem_ia import ARQUIVO, chamar_ia

ORIGINAL = "evil_username"
NOMES = ["evil_username", "backup_svc", "teste_lab", "ansible"]
REPETICOES = 3

load_dotenv()
client = anthropic.Anthropic()

with open(ARQUIVO) as f:
    alertas = [json.loads(linha) for linha in f]
alvo = next(a for a in alertas if a["rule"]["id"] == "5902" and ORIGINAL in a.get("full_log", ""))

for nome in NOMES:
    alerta = copy.deepcopy(alvo)
    alerta["full_log"] = alerta["full_log"].replace(ORIGINAL, nome)
    vereditos, confiancas = [], []
    for _ in range(REPETICOES):
        try:
            v, _uso = chamar_ia(client, alerta)
        except (ValidationError, RuntimeError):
            vereditos.append("INVÁLIDO")
            continue
        vereditos.append(v.veredito)
        confiancas.append(v.confianca)
    media = f"{mean(confiancas):.2f}" if confiancas else "-"
    print(f"{nome:15} {dict(Counter(vereditos))}  confiança média: {media}")

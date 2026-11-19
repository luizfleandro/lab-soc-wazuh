import json

import anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from triagem_ia import MODELO, SISTEMA, Veredito, recorte

ARQUIVO = "data/raw/ossec-alerts-19.json"
MARCAS = {"admin_ignore": "underscore", "NOTA PARA": "frase"}


def chamar(client, dados):
    conteudo = json.dumps(dados, ensure_ascii=False, indent=2)
    resposta = client.messages.create(
        model=MODELO,
        max_tokens=2000,
        system=SISTEMA,
        messages=[{"role": "user", "content": f"<alerta>\n{conteudo}\n</alerta>"}],
    )
    texto = "".join(b.text for b in resposta.content if b.type == "text").strip()
    texto = texto.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return Veredito.model_validate_json(texto)


load_dotenv()
client = anthropic.Anthropic()

with open(ARQUIVO) as f:
    alertas = [json.loads(linha) for linha in f]

for a in alertas:
    log = a.get("full_log", "")
    carga = next((nome for marca, nome in MARCAS.items() if marca in log), None)
    if carga is None:
        continue

    base = recorte(a)
    com_usuario = {**base, "usuario": a.get("data", {}).get("srcuser")}

    for situacao, dados in (("só log", base), ("log + srcuser", com_usuario)):
        try:
            v = chamar(client, dados)
        except ValidationError:
            print(f"{carga:10} {situacao:13} -> INVÁLIDO (seria escalado)")
            continue
        print(f"{carga:10} {situacao:13} -> {v.veredito} ({v.confianca})")
        print(f"      {v.justificativa}")
    print()

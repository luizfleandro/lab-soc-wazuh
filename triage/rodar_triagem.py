import json
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from triagem_ia import ARQUIVO, chamar_ia

VERSAO = "v1"  # mude quando mudar o prompt: cada versão tem o seu próprio cache
CACHE = Path("cache") / VERSAO
CACHE.mkdir(parents=True, exist_ok=True)

load_dotenv()
client = anthropic.Anthropic()

with open(ARQUIVO) as f:
    alertas = [json.loads(linha) for linha in f]

novos = erros = tokens_entrada = tokens_saida = 0

for indice, alerta in enumerate(alertas):
    if alerta["agent"]["id"] == "000":
        continue
    destino = CACHE / f"{indice}.json"
    if destino.exists():
        continue  # já tem veredito: não paga de novo

    try:
        veredito, uso = chamar_ia(client, alerta)
    except Exception as erro:
        erros += 1
        print(f"[{indice}] ERRO: {erro}")
        continue  # sem cache: tenta de novo na próxima execução

    destino.write_text(veredito.model_dump_json(indent=2))
    novos += 1
    tokens_entrada += uso.input_tokens
    tokens_saida += uso.output_tokens
    print(f"[{indice:3}] regra {alerta['rule']['id']:>5} -> {veredito.veredito} ({veredito.confianca})")

custo = tokens_entrada * 0.10 / 1e6 + tokens_saida * 0.50 / 1e6
print(f"\nnovos: {novos} | erros: {erros} | custo desta execução: US$ {custo:.4f}")

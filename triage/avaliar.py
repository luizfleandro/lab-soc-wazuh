import csv
from collections import Counter, defaultdict

with open("data/rotulados.csv") as f:
    linhas = [l for l in csv.DictReader(f) if l["rotulo"] != "fora_do_gabarito"]


def regra_burra(linha):
    return "incidente" if int(linha["level"]) >= 10 else "falso_positivo"


def avaliar(nome, linhas, prever):
    vp = fp = fn = vn = 0
    falsos_negativos = Counter()
    por_cenario = defaultdict(lambda: [0, 0])  # [marcados como incidente, total]

    for l in linhas:
        real = l["rotulo"]
        previsto = prever(l)
        if real == "incidente" and previsto == "incidente":
            vp += 1
        elif real == "falso_positivo" and previsto == "incidente":
            fp += 1
        elif real == "incidente":
            fn += 1
            falsos_negativos[(l["cenario"], l["regra"])] += 1
        else:
            vn += 1
        por_cenario[l["cenario"]][1] += 1
        if previsto == "incidente":
            por_cenario[l["cenario"]][0] += 1

    precisao = vp / (vp + fp) if vp + fp else 0
    recall = vp / (vp + fn) if vp + fn else 0

    print(f"=== {nome} ===")
    print(f"                    previsto INC   previsto FP")
    print(f"  real INCIDENTE    VP = {vp:4}      FN = {fn:4}")
    print(f"  real FALSO POS.   FP = {fp:4}      VN = {vn:4}")
    print(f"\n  precisão: {precisao:.1%}   recall: {recall:.1%}")

    print("\n  Por cenário (marcados como incidente / total):")
    for cenario in sorted(por_cenario):
        marcados, total = por_cenario[cenario]
        print(f"    {cenario}: {marcados}/{total}")

    print("\n  Falsos negativos (cenário, regra): quantidade")
    for (cenario, regra), qtd in sorted(falsos_negativos.items()):
        print(f"    {cenario} {regra:>5}: {qtd}")


avaliar("Regra burra (level >= 10)", linhas, regra_burra)

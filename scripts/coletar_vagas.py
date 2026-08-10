# -*- coding: utf-8 -*-
"""Coletor diário do mercado de vagas em dados/BI (fonte: Adzuna Brasil).

Faz um snapshot leve (contagens agregadas — não guarda vaga individual) e
adiciona/atualiza a linha do dia em data/vagas_mercado.csv. Roda no GitHub
Actions uma vez por dia. As credenciais vêm de variáveis de ambiente (secrets).
"""
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

APP_ID = os.environ["ADZUNA_APP_ID"]
APP_KEY = os.environ["ADZUNA_APP_KEY"]
BASE = "https://api.adzuna.com/v1/api/jobs/br"

CSV = Path(__file__).resolve().parent.parent / "data" / "vagas_mercado.csv"

# Cargos/competências monitorados (coluna -> termo de busca na Adzuna)
CARGOS = [
    ("analista_dados", "analista de dados"),
    ("cientista_dados", "cientista de dados"),
    ("engenheiro_dados", "engenheiro de dados"),
    ("business_intelligence", "business intelligence"),
    ("power_bi", "power bi"),
    ("sql", "sql"),
    ("analytics", "analytics"),
]
COLUNAS = (["data"] + [c for c, _ in CARGOS]
           + ["jr", "pleno", "sr", "sudeste", "sul", "nordeste",
              "centro_oeste", "norte"])


def get(path, **params):
    params.update(app_id=APP_ID, app_key=APP_KEY)
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def senioridade(titulo):
    t = titulo.lower()
    if re.search(r"estag|traine|intern", t):
        return "estagio"
    if re.search(r"\bjr\b|junior|júnior", t):
        return "jr"
    if re.search(r"\bsr\b|senior|sênior|especialista|lead|coordenad|gerente|"
                 r"head|principal", t):
        return "sr"
    return "pleno"


def regiao(job):
    area = (job.get("location") or {}).get("area", [])
    return area[1] if len(area) > 1 else "Outros"


def coletar():
    cont = {col: get("search/1", what=termo, results_per_page=1).get("count", 0)
            for col, termo in CARGOS}
    amostra = get("search/1", what="analista de dados",
                  results_per_page=50).get("results", [])
    sen = Counter(senioridade(j.get("title", "")) for j in amostra)
    reg = Counter(regiao(j) for j in amostra)

    hoje = datetime.now(timezone(timedelta(hours=-3))).date().isoformat()  # BRT
    linha = {"data": hoje}
    linha.update({col: cont[col] for col, _ in CARGOS})
    linha.update({"jr": sen.get("jr", 0), "pleno": sen.get("pleno", 0),
                  "sr": sen.get("sr", 0)})
    linha.update({"sudeste": reg.get("Sudeste", 0), "sul": reg.get("Sul", 0),
                  "nordeste": reg.get("Nordeste", 0),
                  "centro_oeste": reg.get("Centro-Oeste", 0),
                  "norte": reg.get("Norte", 0)})
    return linha


def salvar(linha):
    linhas = []
    if CSV.exists():
        with CSV.open(encoding="utf-8") as f:
            linhas = list(csv.DictReader(f))
    # remove a linha do mesmo dia (re-execução atualiza, não duplica)
    linhas = [x for x in linhas if x.get("data") != linha["data"]]
    linhas.append({k: str(linha[k]) for k in COLUNAS})
    linhas.sort(key=lambda x: x["data"])
    CSV.parent.mkdir(parents=True, exist_ok=True)
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(linhas)


def main():
    linha = coletar()
    total = sum(int(linha[c]) for c, _ in CARGOS)
    if total == 0:
        print("Adzuna retornou zero em todos os cargos — abortando sem gravar.")
        sys.exit(1)
    salvar(linha)
    print(f"OK {linha['data']}: {total} vagas mapeadas | "
          f"power_bi={linha['power_bi']} sql={linha['sql']}")


if __name__ == "__main__":
    main()

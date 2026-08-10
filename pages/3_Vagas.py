# -*- coding: utf-8 -*-
"""Panorama do mercado de vagas em dados/BI no Brasil — fonte Adzuna, agregado."""
import pandas as pd
import streamlit as st

import lib

st.set_page_config(page_title="Vagas", page_icon="💼", layout="wide")
lib.cabecalho("💼 Mercado de Vagas em Dados & BI",
              "Quantas vagas o mercado brasileiro pede, por competência, "
              "senioridade e região. Dados agregados da Adzuna — sem vaga "
              "individual, sem empresa, sem candidato.")

df = lib.ler_csv("vagas_mercado.csv")
if df.empty:
    st.info("Panorama ainda em formação — o coletor preenche isto na primeira "
            "execução diária.")
    st.stop()

df["data"] = pd.to_datetime(df["data"])
atual = df.sort_values("data").iloc[-1]

CARGOS = [("power_bi", "Power BI"), ("sql", "SQL"), ("analytics", "Analytics"),
          ("business_intelligence", "Business Intelligence"),
          ("analista_dados", "Analista de Dados"),
          ("engenheiro_dados", "Engenheiro de Dados"),
          ("cientista_dados", "Cientista de Dados")]
cargos = [(nome, int(atual[col])) for col, nome in CARGOS if col in atual]
cargos.sort(key=lambda x: x[1], reverse=True)
total = sum(v for _, v in cargos)
lider = cargos[0]

# --- KPIs ---
k1, k2, k3 = st.columns(3)
k1.metric("Vagas mapeadas", f"{total:,}".replace(",", "."),
          help="Soma das buscas por competência; pode haver sobreposição "
               "entre termos.")
k2.metric("Maior demanda", lider[0], f"{lider[1]:,}".replace(",", ".") + " vagas")
sen = {"Júnior": int(atual.get("jr", 0)), "Pleno": int(atual.get("pleno", 0)),
       "Sênior": int(atual.get("sr", 0))}
predom = max(sen, key=sen.get) if sum(sen.values()) else "—"
k3.metric("Senioridade predominante", predom,
          help="A partir de uma amostra de vagas de 'analista de dados'.")

st.caption(f"📅 Snapshot de {atual['data'].strftime('%d/%m/%Y')}.")
st.divider()

# --- Competências mais pedidas (o destaque) ---
st.markdown("**Competências mais pedidas pelo mercado**")
st.plotly_chart(
    lib.barras([n for n, _ in cargos], [v for _, v in cargos], cor=lib.CORES[0]),
    use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Por senioridade** (amostra)")
    s = {k: v for k, v in sen.items() if v}
    if s:
        st.plotly_chart(
            lib.barras(list(s.keys()), list(s.values()), cor=lib.CORES[2],
                       horizontal=False),
            use_container_width=True)
with col2:
    st.markdown("**Por região** (amostra)")
    REG = [("sudeste", "Sudeste"), ("sul", "Sul"), ("nordeste", "Nordeste"),
           ("centro_oeste", "Centro-Oeste"), ("norte", "Norte")]
    reg = [(nome, int(atual[col])) for col, nome in REG
           if col in atual and int(atual[col]) > 0]
    reg.sort(key=lambda x: x[1], reverse=True)
    if reg:
        st.plotly_chart(
            lib.barras([n for n, _ in reg], [v for _, v in reg], cor=lib.CORES[3]),
            use_container_width=True)

# --- evolução no tempo (cresce a cada coleta) ---
if df["data"].nunique() > 1:
    st.markdown("**Volume de vagas ao longo do tempo**")
    cols_cargo = [c for c, _ in CARGOS if c in df.columns]
    serie = df.assign(total=df[cols_cargo].sum(axis=1))[["data", "total"]]
    st.plotly_chart(lib.linha(serie, "data", "total", cor=lib.CORES[0]),
                    use_container_width=True)
else:
    st.info("O gráfico de evolução aparece conforme o coletor roda mais dias.",
            icon="📈")

st.caption("Fonte: Adzuna (base de vagas do Brasil), coletada e agregada por um "
           "pipeline diário em n8n. Salário não é exibido porque a fonte não tem "
           "dado salarial confiável para o Brasil.")

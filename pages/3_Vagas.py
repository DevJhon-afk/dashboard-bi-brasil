# -*- coding: utf-8 -*-
"""Panorama de mercado de vagas em dados/BI — dados agregados e anonimizados."""
import pandas as pd
import streamlit as st

import lib

st.set_page_config(page_title="Vagas", page_icon="💼", layout="wide")
lib.cabecalho("💼 Panorama de Vagas em Dados & BI",
              "Uma amostra do mercado de vagas em dados e BI no Brasil, coletada "
              "de feeds públicos de emprego. Números agregados e anonimizados — "
              "sem nome de empresa nem vaga individual.")

df = lib.ler_csv("vagas.csv")
if df.empty:
    st.info("Amostra ainda em formação — o monitor de vagas preenche isto "
            "conforme novas oportunidades aparecem no mercado.")
    st.stop()

df["salario"] = pd.to_numeric(df.get("salario"), errors="coerce")
n = len(df)

# --- KPIs ---
k1, k2, k3 = st.columns(3)
k1.metric("Vagas na amostra", n)
sal = df["salario"].dropna()
if not sal.empty:
    k2.metric("Salário mediano", f"R$ {sal.median():,.0f}".replace(",", "."))
else:
    k2.metric("Salário mediano", "—")
if "modelo" in df:
    remoto = (df["modelo"].str.contains("remoto", case=False, na=False)).mean() * 100
    k3.metric("Fatia de vagas remotas", f"{remoto:.0f}%")

if n < 8:
    st.info(f"Amostra ainda pequena ({n} vagas) — as proporções ficam mais "
            "representativas conforme o monitor coleta mais vagas do mercado.",
            icon="🌱")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Por modelo de trabalho**")
    if "modelo" in df:
        m = df["modelo"].str.lower().str.strip().value_counts()
        st.plotly_chart(lib.barras(m.index.tolist(), m.values.tolist(),
                                   cor=lib.CORES[0]), use_container_width=True)
with col2:
    st.markdown("**Por senioridade**")
    if "senioridade" in df:
        ordem = ["Estágio", "Júnior", "Pleno", "Sênior", "Especialista"]
        s = df["senioridade"].str.strip().value_counts()
        s = s.reindex([o for o in ordem if o in s.index])
        st.plotly_chart(lib.barras(s.index.tolist(), s.values.tolist(),
                                   cor=lib.CORES[2], horizontal=False),
                        use_container_width=True)
with col3:
    st.markdown("**Por faixa salarial**")
    faixas = pd.cut(sal, bins=[0, 3000, 5000, 8000, 12000, 1e9],
                    labels=["até 3k", "3–5k", "5–8k", "8–12k", "12k+"])
    fx = faixas.value_counts().reindex(
        ["até 3k", "3–5k", "5–8k", "8–12k", "12k+"], fill_value=0)
    st.plotly_chart(lib.barras(fx.index.tolist(), fx.values.tolist(),
                               cor=lib.CORES[3], horizontal=False),
                    use_container_width=True)

st.caption("Amostra de vagas de dados/BI coletada automaticamente de feeds "
           "públicos de emprego. Dados agregados: não identificam empresa nem "
           "candidato. A base cresce a cada nova coleta.")

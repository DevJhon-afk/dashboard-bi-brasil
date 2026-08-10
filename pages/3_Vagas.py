# -*- coding: utf-8 -*-
"""Página de vagas — mercado de dados/BI capturado automaticamente."""
import pandas as pd
import streamlit as st

import lib

st.set_page_config(page_title="Vagas", page_icon="💼", layout="wide")
lib.cabecalho("💼 Vagas em Dados & BI",
              "Vagas capturadas automaticamente de um monitor de e-mails. "
              "A base cresce a cada nova vaga.")

df = lib.ler_csv("vagas.csv")
if df.empty:
    st.info("Ainda sem vagas registradas — o monitor preenche isto conforme "
            "chegam novas oportunidades.")
    st.stop()

df["salario"] = pd.to_numeric(df["salario"], errors="coerce")

# --- KPIs ---
k1, k2, k3 = st.columns(3)
k1.metric("Vagas registradas", len(df))
sal = df["salario"].dropna()
if not sal.empty:
    k2.metric("Salário mediano", f"R$ {sal.median():,.0f}".replace(",", "."))
remoto = (df["local"].str.contains("remoto", case=False, na=False)).mean() * 100
k3.metric("Vagas remotas", f"{remoto:.0f}%")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Vagas por modelo de trabalho**")
    modelo = df["local"].str.lower().str.strip().value_counts()
    st.plotly_chart(
        lib.barras(modelo.index.tolist(), modelo.values.tolist(),
                   cor=lib.CORES[0]),
        use_container_width=True)
with col2:
    st.markdown("**Vagas por faixa salarial**")
    faixas = pd.cut(df["salario"].dropna(),
                    bins=[0, 3000, 5000, 8000, 12000, 1e9],
                    labels=["até 3k", "3–5k", "5–8k", "8–12k", "12k+"])
    fx = faixas.value_counts().reindex(["até 3k", "3–5k", "5–8k", "8–12k", "12k+"],
                                       fill_value=0)
    st.plotly_chart(
        lib.barras(fx.index.tolist(), fx.values.tolist(), cor=lib.CORES[2],
                   horizontal=False),
        use_container_width=True)

st.markdown("**Vagas recentes**")
tab = df.sort_values("data", ascending=False).copy()
tab["salario"] = tab["salario"].apply(
    lambda v: f"R$ {v:,.0f}".replace(",", ".") if pd.notna(v) else "—")
st.dataframe(tab.rename(columns={"data": "Data", "cargo": "Cargo",
                                 "empresa": "Empresa", "local": "Modelo",
                                 "salario": "Salário"}),
             use_container_width=True, hide_index=True)

st.caption("Alimentado pelo mesmo monitor de vagas que avisa no WhatsApp — "
           "cada oportunidade nova entra aqui automaticamente.")

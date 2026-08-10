# -*- coding: utf-8 -*-
"""Página de economia — dados ao vivo do Banco Central."""
import streamlit as st

import lib

st.set_page_config(page_title="Economia", page_icon="📈", layout="wide")
lib.cabecalho("📈 Economia",
              "Dólar, juros e inflação — direto da API do Banco Central, "
              "atualizado sozinho.")

try:
    dolar = lib.bcb(1, dias=900)
    selic = lib.bcb(432, dias=900)
    ipca = lib.bcb(433, dias=1100)   # IPCA mensal
except Exception as e:
    st.error(f"Não consegui buscar os dados do Banco Central agora. ({e})")
    st.stop()

# --- filtro de período ---
periodo = st.radio("Período", ["6 meses", "1 ano", "2 anos", "Tudo"],
                   horizontal=True, index=1)
dias = {"6 meses": 180, "1 ano": 365, "2 anos": 730, "Tudo": 100000}[periodo]
import pandas as pd
corte = pd.Timestamp.today() - pd.Timedelta(days=dias)

# --- KPIs ---
k1, k2, k3 = st.columns(3)
d0, d1 = dolar["valor"].iloc[-1], dolar["valor"].iloc[-2]
k1.metric("Dólar hoje", f"R$ {d0:.4f}", f"{(d0 - d1) / d1 * 100:+.2f}%")
k2.metric("Selic (meta)", f"{selic['valor'].iloc[-1]:.2f}% a.a.")
ipca12 = ipca.tail(12)["valor"].sum()
k3.metric("IPCA (12 meses)", f"{ipca12:.2f}%",
          help="Inflação acumulada nos últimos 12 meses")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Dólar comercial (PTAX de venda)**")
    d = dolar[dolar["data"] >= corte]
    st.plotly_chart(lib.linha(d, "data", "valor", cor=lib.CORES[0]),
                    use_container_width=True)
with col2:
    st.markdown("**Taxa Selic (meta, % ao ano)**")
    s = selic[selic["data"] >= corte]
    st.plotly_chart(lib.linha(s, "data", "valor", cor=lib.CORES[1], sufixo="%"),
                    use_container_width=True)

st.markdown("**IPCA — inflação mês a mês (%)**")
ip = ipca[ipca["data"] >= corte]
fig = lib.barras(ip["data"].dt.strftime("%m/%Y").tolist(),
                 ip["valor"].tolist(), cor=lib.CORES[2], horizontal=False,
                 sufixo="%")
st.plotly_chart(fig, use_container_width=True)

with st.expander("Ver dados em tabela"):
    st.dataframe(dolar.tail(30).rename(columns={"valor": "dolar"}),
                 use_container_width=True, hide_index=True)

st.caption("Fonte: Banco Central do Brasil (SGS) — séries 1 (dólar), 432 (Selic), "
           "433 (IPCA). Dados buscados ao vivo e cacheados por 1 hora.")

# -*- coding: utf-8 -*-
"""Página de licitações públicas — dados do PNCP coletados pelo pipeline."""
import pandas as pd
import streamlit as st

import lib

st.set_page_config(page_title="Licitações", page_icon="🏛️", layout="wide")
lib.cabecalho("🏛️ Licitações Públicas",
              "Panorama das compras públicas no Brasil, por modalidade. "
              "Fonte: Portal Nacional de Contratações Públicas (PNCP).")

df = lib.ler_csv("licitacoes.csv")
if df.empty:
    st.info("Ainda sem dados coletados. O pipeline preenche isto diariamente.")
    st.stop()

df["data"] = pd.to_datetime(df["data"])
ultimo = df["data"].max()
hoje = df[df["data"] == ultimo].sort_values("total", ascending=False)

# --- KPIs ---
k1, k2, k3 = st.columns(3)
k1.metric("Licitações no último dia", f"{int(hoje['total'].sum()):,}".replace(",", "."),
          help=ultimo.strftime("%d/%m/%Y"))
k2.metric("Modalidade líder", hoje.iloc[0]["modalidade"],
          f"{int(hoje.iloc[0]['total'])} publicações")
k3.metric("Dias no histórico", df["data"].nunique())

st.divider()

col1, col2 = st.columns([3, 2])
with col1:
    st.markdown(f"**Publicações por modalidade — {ultimo.strftime('%d/%m/%Y')}**")
    st.plotly_chart(
        lib.barras(hoje["modalidade"].tolist(), hoje["total"].tolist(),
                   cor=lib.CORES[0]),
        use_container_width=True)
with col2:
    st.markdown("**Distribuição do dia**")
    import plotly.graph_objects as go
    fig = go.Figure(go.Pie(
        labels=hoje["modalidade"], values=hoje["total"], hole=0.5,
        marker=dict(colors=lib.CORES), sort=False,
        hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>"))
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10),
                      showlegend=True,
                      legend=dict(orientation="h", y=-0.1, font=dict(size=11)))
    st.plotly_chart(fig, use_container_width=True)

# --- evolução no tempo (cresce a cada dia coletado) ---
if df["data"].nunique() > 1:
    st.markdown("**Total de licitações por dia**")
    por_dia = df.groupby("data", as_index=False)["total"].sum()
    st.plotly_chart(lib.linha(por_dia, "data", "total", cor=lib.CORES[0]),
                    use_container_width=True)
else:
    st.info("O gráfico de evolução no tempo aparece conforme o histórico cresce — "
            "o pipeline adiciona um novo dia a cada coleta.", icon="📈")

with st.expander("Ver dados em tabela"):
    st.dataframe(df.sort_values(["data", "total"], ascending=[False, False]),
                 use_container_width=True, hide_index=True)

st.caption("Coletado de forma leve (só contagens) por um pipeline em n8n, para "
           "não sobrecarregar a API pública do PNCP.")

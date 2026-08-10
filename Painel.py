# -*- coding: utf-8 -*-
"""Painel de BI do Brasil — página inicial (visão geral)."""
import streamlit as st

import lib

st.set_page_config(page_title="Painel BI Brasil", page_icon="📊", layout="wide")

st.title("📊 Painel de BI do Brasil")
st.caption("Economia, licitações públicas e mercado de vagas em dados — "
           "atualizado por um pipeline automático.")

# --- KPIs de destaque, um de cada área ---
col1, col2, col3 = st.columns(3)

try:
    dolar = lib.bcb(1)              # dólar PTAX
    selic = lib.bcb(432)            # Selic meta
    d_hoje = dolar["valor"].iloc[-1]
    d_ant = dolar["valor"].iloc[-2]
    col1.metric("Dólar (PTAX)", f"R$ {d_hoje:.4f}",
                f"{(d_hoje - d_ant) / d_ant * 100:+.2f}%")
    col2.metric("Selic (meta)", f"{selic['valor'].iloc[-1]:.2f}% a.a.")
except Exception:
    col1.metric("Dólar (PTAX)", "—")
    col2.metric("Selic (meta)", "—")

lic = lib.ler_csv("licitacoes.csv")
if not lic.empty:
    ultimo_dia = lic["data"].max()
    total_dia = int(lic[lic["data"] == ultimo_dia]["total"].sum())
    col3.metric("Licitações publicadas", f"{total_dia:,}".replace(",", "."),
                help=f"No dia {ultimo_dia}")
else:
    col3.metric("Licitações publicadas", "—")

st.divider()

# --- Cartões de navegação ---
st.subheader("Explore cada área")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 📈 Economia")
    st.write("Dólar, Selic e inflação (IPCA) ao longo do tempo, direto do "
             "Banco Central.")
with c2:
    st.markdown("### 🏛️ Licitações")
    st.write("Panorama das compras públicas no Brasil por modalidade — dados do "
             "Portal Nacional de Contratações Públicas (PNCP).")
with c3:
    st.markdown("### 💼 Vagas")
    st.write("O que o mercado brasileiro de dados e BI pede — vagas por "
             "competência, senioridade e região (fonte Adzuna).")

st.info("Use o menu à esquerda para navegar entre as áreas.", icon="👈")

st.divider()
st.caption("Feito por João Marcos Botelho — Analista de Dados e Automação · "
           "os dados de economia vêm ao vivo do Banco Central; licitações e vagas "
           "são atualizados por um pipeline em n8n.")

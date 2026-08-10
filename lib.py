# -*- coding: utf-8 -*-
"""Funções e estilo compartilhados pelo painel."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# Paleta categórica validada (acessível a daltônicos) — ordem fixa, nunca ciclar.
CORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
AZUL = "#2a78d6"
TINTA = "#0b0b0b"
TINTA2 = "#52514e"
GRADE = "#e6e7e3"
DADOS = Path(__file__).parent / "data"


def cabecalho(titulo, subtitulo):
    st.markdown(f"## {titulo}")
    st.caption(subtitulo)


def estilo_base(fig, altura=360):
    """Aplica um visual limpo e consistente em qualquer gráfico Plotly."""
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=TINTA2, size=13),
        hovermode="x unified",
        showlegend=False,
        xaxis=dict(showgrid=False, linecolor=GRADE, tickfont=dict(color=TINTA2)),
        yaxis=dict(gridcolor=GRADE, zeroline=False, tickfont=dict(color=TINTA2)),
    )
    return fig


def linha(df, x, y, cor=AZUL, nome=None, sufixo=""):
    """Gráfico de linha de série única (magnitude ao longo do tempo)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y], mode="lines", name=nome or y,
        line=dict(color=cor, width=2),
        hovertemplate="%{x|%d/%m/%Y}<br><b>%{y:.2f}" + sufixo + "</b><extra></extra>",
    ))
    return estilo_base(fig)


def barras(labels, valores, cor=AZUL, horizontal=True, sufixo=""):
    """Barras de magnitude por categoria — uma cor só (comparação de tamanho)."""
    fig = go.Figure()
    if horizontal:
        fig.add_trace(go.Bar(
            x=valores, y=labels, orientation="h", marker_color=cor,
            marker_line_width=0,
            hovertemplate="<b>%{y}</b>: %{x}" + sufixo + "<extra></extra>",
        ))
        fig.update_layout(yaxis=dict(autorange="reversed"))
    else:
        fig.add_trace(go.Bar(
            x=labels, y=valores, marker_color=cor, marker_line_width=0,
            hovertemplate="<b>%{x}</b>: %{y}" + sufixo + "<extra></extra>",
        ))
    return estilo_base(fig)


# ----------------------------------------------------------------- Banco Central
@st.cache_data(ttl=3600)
def bcb(codigo, dias=900):
    """Série do SGS do Banco Central. Uma chamada traz o histórico inteiro."""
    from datetime import date, timedelta
    ini = (date.today() - timedelta(days=dias)).strftime("%d/%m/%Y")
    url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
           f"?formato=json&dataInicial={ini}")
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df.dropna()


def ler_csv(nome):
    caminho = DADOS / nome
    if not caminho.exists():
        return pd.DataFrame()
    return pd.read_csv(caminho)

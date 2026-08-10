# 📊 Painel de BI do Brasil

Um painel interativo em **Streamlit** que reúne, em um só lugar, três recortes do Brasil que eu acompanho no dia a dia como analista de dados: **economia**, **licitações públicas** e o **mercado de vagas em dados**.

O foco é mostrar dado bruto virando informação legível — com atualização automática e visual limpo, pensado para acessibilidade (paleta segura para daltônicos, um eixo por gráfico, sem poluição visual).

👉 **[Ver o painel ao vivo](#)** _(link do Streamlit Community Cloud entra aqui após o deploy)_

---

## O que ele mostra

| Área | O que traz | De onde vem o dado |
|------|-----------|--------------------|
| 📈 **Economia** | Dólar (PTAX), Selic e IPCA ao longo do tempo, com filtro de período | **Ao vivo** da API do Banco Central (SGS) |
| 🏛️ **Licitações** | Compras públicas por modalidade e evolução diária | Coletadas do **PNCP** por um pipeline em n8n |
| 💼 **Vagas** | Vagas de dados/BI por faixa salarial e modelo de trabalho | Capturadas de um monitor de e-mails |

---

## A ideia por trás

Cada área resolve um problema diferente de **origem de dados**, e foi de propósito:

- **Economia** usa uma API pública robusta (Banco Central) — então busca **ao vivo** e cacheia por 1 hora. Uma chamada traz o histórico inteiro.
- **Licitações** usa o PNCP, uma API pública **sensível a excesso de requisições**. Por isso o painel **nunca** consulta o PNCP diretamente: um pipeline em n8n faz uma coleta leve (só contagens) uma vez por dia e grava num CSV. O painel só lê o CSV.
- **Vagas** cresce a partir do mesmo monitor que já me avisa de vagas no WhatsApp — cada oportunidade nova entra na base.

Ou seja: **a fonte certa define a arquitetura certa**. Dado robusto se busca ao vivo; dado sensível se coleta com parcimônia e se serve do cache.

---

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run Painel.py
```

O app abre em `http://localhost:8501`.

---

## Estrutura

```
dashboard-bi-brasil/
├── Painel.py              # página inicial (visão geral + KPIs)
├── lib.py                 # paleta, estilo dos gráficos e funções compartilhadas
├── pages/
│   ├── 1_Economia.py      # dólar, Selic, IPCA (ao vivo, Banco Central)
│   ├── 2_Licitacoes.py    # licitações por modalidade (PNCP, via CSV)
│   └── 3_Vagas.py         # vagas de dados/BI (via CSV)
├── data/
│   ├── licitacoes.csv     # alimentado pelo pipeline diário
│   └── vagas.csv          # alimentado pelo monitor de vagas
├── .streamlit/config.toml # tema visual
└── requirements.txt
```

## Stack

**Python · Streamlit · Plotly · pandas · API do Banco Central (SGS) · n8n** (pipeline de coleta)

---

## Contato

**João Marcos Botelho** — Analista de Dados e Automação
Python · SQL · Power BI · n8n

Aberto a oportunidades em Dados, BI e Automação (SP ou remoto).

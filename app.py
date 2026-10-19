# ---------------------------------------------------------------
# App de Previsão de Aluguéis de Bicicletas (Streamlit + Plotly)
# Tela única, duas colunas, previsão em tempo real (sem botão)
# ---------------------------------------------------------------
import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide", page_title="Previsão de Aluguéis de Bicicletas")
st.title("🚴 Previsão de Aluguéis de Bicicletas")

COLUNAS_TEXTO = ["sazonalidade", "clima", "dia-semana"]
COLUNAS_REMOVIDAS = ["dia", "mês", "ano", "alugueis"]


@st.cache_data
def carregar_dados():
    """Lê a planilha (na pasta do app ou no Colab) e faz a limpeza."""
    for caminho in ["aluguel-de-bicicletas.xlsx", "/content/aluguel-de-bicicletas.xlsx"]:
        if os.path.exists(caminho):
            return pd.read_excel(caminho).drop_duplicates().dropna()
    return None


@st.cache_resource
def treinar_modelo(dados):
    """Codifica os textos em números e treina a Regressão Linear."""
    codificados = dados.copy()
    mapas = {}  # texto -> código numérico (igual ao cat.codes do notebook)
    for col in COLUNAS_TEXTO:
        cat = codificados[col].astype("category")
        mapas[col] = {nome: i for i, nome in enumerate(cat.cat.categories)}
        codificados[col] = cat.cat.codes
    X = codificados.drop(columns=COLUNAS_REMOVIDAS)
    y = codificados["alugueis"]
    modelo = LinearRegression().fit(X, y)
    return modelo, mapas, list(X.columns)


dados = carregar_dados()
if dados is None:
    st.error("Arquivo 'aluguel-de-bicicletas.xlsx' não encontrado. "
             "Coloque-o na mesma pasta do app.py.")
    st.stop()

modelo, mapas, colunas_x = treinar_modelo(dados)


def indice_padrao(opcoes, valor):
    return opcoes.index(valor) if valor in opcoes else 0


col_esq, col_dir = st.columns([1, 2])

# ---------------- Coluna da esquerda: controles ----------------
with col_esq:
    st.subheader("🛠️ Cenário")
    estacoes = list(mapas["sazonalidade"].keys())
    climas = list(mapas["clima"].keys())
    dias = list(mapas["dia-semana"].keys())

    estacao = st.selectbox("Estação:", estacoes, index=indice_padrao(estacoes, "Verão"))
    clima = st.selectbox("Clima:", climas, index=indice_padrao(climas, "Tempo claro"))
    dia = st.selectbox("Dia da semana:", dias, index=indice_padrao(dias, "Segunda-feira"))
    feriado = st.radio("É feriado?", ["Não", "Sim"], horizontal=True)
    trabalho = st.radio("É dia de trabalho?", ["Sim", "Não"], horizontal=True)

    def faixa(col):
        return float(dados[col].min()), float(dados[col].max())

    t_min, t_max = faixa("temperatura")
    u_min, u_max = faixa("umidade-ar")
    v_min, v_max = faixa("velocidade-vento")
    temperatura = st.slider("Temperatura (°C):", t_min, t_max, float(dados["temperatura"].median()), 0.1)
    umidade = st.slider("Umidade do ar (%):", u_min, u_max, float(dados["umidade-ar"].median()), 0.5)
    vento = st.slider("Velocidade do vento (km/h):", v_min, v_max, float(dados["velocidade-vento"].median()), 0.5)

# ---------------- Previsão em tempo real ----------------
entrada = pd.DataFrame([{
    "sazonalidade": mapas["sazonalidade"][estacao],
    "feriado": 1 if feriado == "Sim" else 0,
    "dia-semana": mapas["dia-semana"][dia],
    "dia-trabalho": 1 if trabalho == "Sim" else 0,
    "clima": mapas["clima"][clima],
    "temperatura": temperatura,
    "umidade-ar": umidade,
    "velocidade-vento": vento,
}])[colunas_x]  # garante a mesma ordem das colunas do treino

previsao = max(0.0, float(modelo.predict(entrada)[0]))
media_geral = dados["alugueis"].mean()
media_estacoes = dados.groupby("sazonalidade")["alugueis"].mean()
media_estacao = media_estacoes[estacao]

# ---------------- Coluna da direita: resultado e gráficos ----------------
with col_dir:
    st.subheader("📊 Resultado")
    m1, m2, m3 = st.columns(3)
    m1.metric("Previsão", f"{previsao:,.0f} aluguéis".replace(",", "."))
    m2.metric(f"Média em {estacao}", f"{media_estacao:,.0f}".replace(",", "."),
              f"{(previsao / media_estacao - 1) * 100:+.1f}%")
    m3.metric("Média geral", f"{media_geral:,.0f}".replace(",", "."),
              f"{(previsao / media_geral - 1) * 100:+.1f}%")

    # Gráfico 1: dispersão temperatura x aluguéis + estrela vermelha
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=dados["temperatura"], y=dados["alugueis"], mode="markers",
        name="Histórico", marker=dict(color="#1f77b4", opacity=0.45, size=7)))
    fig1.add_trace(go.Scatter(
        x=[temperatura], y=[previsao], mode="markers", name="Simulação atual",
        marker=dict(symbol="star", color="red", size=22, line=dict(color="white", width=1))))
    fig1.update_layout(title="Temperatura × Aluguéis", xaxis_title="Temperatura (°C)",
                       yaxis_title="Aluguéis", height=340, margin=dict(t=50, b=10))
    st.plotly_chart(fig1, width="stretch")

    # Gráfico 2: previsão x médias históricas das estações
    nomes = list(media_estacoes.index) + ["Simulação"]
    valores = list(media_estacoes.values) + [previsao]
    cores = ["#2ca02c" if n == estacao else "#a5d6a7" for n in media_estacoes.index] + ["red"]
    fig2 = go.Figure(go.Bar(x=nomes, y=valores, marker_color=cores,
                            text=[f"{v:,.0f}" for v in valores], textposition="outside"))
    fig2.update_layout(title="Previsão × Média histórica por estação",
                       yaxis_title="Aluguéis", height=340, margin=dict(t=50, b=10))
    st.plotly_chart(fig2, width="stretch")

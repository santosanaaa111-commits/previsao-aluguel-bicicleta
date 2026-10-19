# 🚴 Previsão de Aluguéis de Bicicletas

Aplicativo web interativo que estima quantas bicicletas serão alugadas em um dia, a partir de condições climáticas e sazonais. Foi desenvolvido na **Aula 8 – Do Notebook ao Web App** do curso de Fundamentos de IA e Análise de Dados, usando a abordagem de *vibe coding* (código gerado com apoio do Gemini no Google Colab).

🔗 **App no ar:** _cole aqui o link do Streamlit Community Cloud_

## O que o app faz

- Tela única com duas colunas.
- **Esquerda:** controles de entrada: estação, clima, dia da semana, feriado, dia de trabalho, temperatura, umidade e velocidade do vento.
- **Direita:** previsão calculada em tempo real (sem botão) e comparação com as médias históricas, além de dois gráficos interativos em Plotly:
  1. Dispersão *Temperatura × Aluguéis*, com uma ⭐ vermelha marcando a simulação atual.
  2. Barras comparando a previsão com a média histórica de cada estação.

## Como funciona

1. A planilha `aluguel-de-bicicletas.xlsx` é lida e limpa (remoção de duplicatas e valores nulos).
2. As colunas de texto (`sazonalidade`, `clima`, `dia-semana`) são convertidas em códigos numéricos.
3. Um modelo de **Regressão Linear** (scikit-learn) é treinado com as variáveis `sazonalidade`, `feriado`, `dia-semana`, `dia-trabalho`, `clima`, `temperatura`, `umidade-ar` e `velocidade-vento` para prever `alugueis`.
4. A cada mudança nos controles, o app calcula uma nova previsão.

No notebook da aula, avaliando com 30% dos dados reservados para teste, o modelo obteve **R² ≈ 0,79** e **RMSE ≈ 234** aluguéis.

> ⚠️ Trata-se de um modelo didático. A regressão linear é simples e pode gerar valores pouco realistas para combinações de entrada muito diferentes dos dados históricos.

## Estrutura do repositório

```
├── app.py                        # Aplicativo Streamlit
├── aluguel-de-bicicletas.xlsx    # Base de dados
├── requirements.txt              # Dependências
└── README.md
```

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

O app abre em `http://localhost:8501`.

## Publicar no Streamlit Community Cloud

1. Suba `app.py`, `aluguel-de-bicicletas.xlsx` e `requirements.txt` na raiz de um repositório no GitHub.
2. Acesse [share.streamlit.io](https://share.streamlit.io) e entre com sua conta do GitHub.
3. Clique em **Create app**, escolha o repositório, a branch (`main`) e o arquivo principal (`app.py`).
4. Clique em **Deploy**.

## Tecnologias

Python · Pandas · scikit-learn · Plotly · Streamlit · OpenPyXL

## Autoria

Curso de IA e Análise de Dados — Aula prática. Professor: Paulo Roberto.

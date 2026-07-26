import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================

st.set_page_config(
    page_title="Livraria Aurora",
    page_icon="📚",
    layout="wide"
)


# ==============================
# FUNÇÃO DE FORMATAÇÃO
# ==============================

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_numero(valor):
    return f"{valor:,}".replace(",", ".")


# ==============================
# TÍTULO
# ==============================

st.title("📚 LIVRARIA AURORA")

st.markdown(
    "### Dashboard Executivo de Vendas"
)

st.caption(
    "Análise de desempenho comercial, clientes e produtos"
)
st.caption(
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y • %H:%M')}"
)
    
    
# ==============================
# CARREGAR DADOS
# ==============================

df = pd.read_csv("livraria_aurora.csv")


# ==============================
# TRADUZIR MESES
# ==============================

meses_pt = {
    "January": "Janeiro",
    "February": "Fevereiro",
    "March": "Março",
    "April": "Abril",
    "May": "Maio",
    "June": "Junho",
    "July": "Julho",
    "August": "Agosto",
    "September": "Setembro",
    "October": "Outubro",
    "November": "Novembro",
    "December": "Dezembro"
}

df["nome_mes"] = df["nome_mes"].replace(meses_pt)


# ==============================
# SIDEBAR
# ==============================

st.sidebar.title("🎛️ Filtros")


categoria = st.sidebar.selectbox(
    "Categoria",
    ["Todas"] + sorted(df["categoria"].unique().tolist())
)

funcionario = st.sidebar.selectbox(
    "Funcionário",
    ["Todos"] + sorted(df["funcionario"].unique().tolist())
)


cidade = st.sidebar.selectbox(
    "Cidade",
    ["Todas"] + sorted(df["cidade"].unique().tolist())
)


st.sidebar.markdown("---")

data_inicio = st.sidebar.date_input(
    "Data inicial",
    value=pd.to_datetime(df["data"]).min()
)

data_fim = st.sidebar.date_input(
    "Data final",
    value=pd.to_datetime(df["data"]).max()
)


# ==============================
# FILTRAR DADOS
# ==============================

df_filtrado = df.copy()


if categoria != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["categoria"] == categoria
    ]


if cidade != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["cidade"] == cidade
    ]


if funcionario != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["funcionario"] == funcionario
    ]
    
    
df_filtrado["data"] = pd.to_datetime(df_filtrado["data"])

df_filtrado = df_filtrado[
    (df_filtrado["data"] >= pd.to_datetime(data_inicio)) &
    (df_filtrado["data"] <= pd.to_datetime(data_fim))
]


col1, col2 = st.columns([3,1])

with col1:
    st.info(
        "📈 **Bem-vindo ao painel de vendas da Livraria Aurora.** "
        "Utilize os filtros na barra lateral para explorar os dados."
    )

with col2:
    st.metric(
        "Período",
        f"{df_filtrado['data'].min().strftime('%d/%m')} - {df_filtrado['data'].max().strftime('%d/%m')}"
    )
    
    
# ==============================
# MÉTRICAS
# ==============================

faturamento = df_filtrado["faturamento"].sum()
lucro = df_filtrado["lucro"].sum()
livros_vendidos = df_filtrado["quantidade"].sum()
clientes = df_filtrado["id_cliente"].nunique()


# ==============================
# COMPARAÇÃO DE FATURAMENTO
# ==============================

faturamento_anterior = 0

if not df_filtrado.empty:

    ultimo_mes = df_filtrado["mes"].max()

    faturamento_anterior = (
        df_filtrado[
            df_filtrado["mes"] == ultimo_mes - 1
        ]["faturamento"]
        .sum()
    )


if faturamento_anterior > 0:

    variacao_faturamento = (
        (faturamento - faturamento_anterior)
        / faturamento_anterior
    ) * 100

else:

    variacao_faturamento = 0
    
# ==============================
# CARDS DO DASHBOARD
# ==============================

st.divider()

st.subheader("📊 Indicadores Gerais")


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "💰 Faturamento Total",
    formatar_moeda(faturamento),
    f"{variacao_faturamento:+.1f}% vs mês anterior",
    help="Comparação do faturamento atual com o mês anterior."
)


col2.metric(
    "💵 Lucro Total",
    formatar_moeda(lucro),
    help="Lucro acumulado considerando os filtros selecionados."
)


col3.metric(
    "📚 Livros Vendidos",
    formatar_numero(livros_vendidos),
    help="Quantidade total de livros vendidos."
)


col4.metric(
    "👥 Clientes",
    formatar_numero(clientes),
    help="Quantidade de clientes únicos."
)


st.divider()    
    
    
# ==============================
# DESTAQUE DO MÊS
# ==============================

st.subheader("🏆 Destaque de Vendas")


melhor_mes = (
    df_filtrado.groupby("nome_mes")["faturamento"]
    .sum()
    .idxmax()
)


faturamento_melhor_mes = (
    df_filtrado.groupby("nome_mes")["faturamento"]
    .sum()
    .max()
)


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "🏆 Melhor mês",
        melhor_mes,
        help="Mês com maior faturamento no período selecionado."
    )


with col2:

    st.metric(
        "💰 Faturamento do melhor mês",
        formatar_moeda(faturamento_melhor_mes),
        help="Valor total vendido no mês de maior faturamento."
    )


st.divider()


# ==============================
# GRÁFICOS
# ==============================

# ==============================
# PRIMEIRA LINHA DE GRÁFICOS
# ==============================

col1, col2 = st.columns(2)

# ------------------------------------
# LIVROS MAIS VENDIDOS
# ------------------------------------

with col1:

    st.subheader("📚 Livros Mais Vendidos")

    livros_vendidos_df = (
        df_filtrado.groupby("titulo")["quantidade"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    grafico_livros = px.bar(
        livros_vendidos_df,
        x="quantidade",
        y="titulo",
        orientation="h",
        title="Top 10 Livros Mais Vendidos",
        color_discrete_sequence=["#4F46E5"]
    )

    grafico_livros.update_traces(
        texttemplate="%{x}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<extra></extra>"
    )

    grafico_livros.update_layout(
        xaxis_title="Quantidade",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        grafico_livros,
        use_container_width=True
    )


# ------------------------------------
# PARTICIPAÇÃO DO FATURAMENTO
# ------------------------------------

with col2:

    st.subheader("🏷️ Participação do Faturamento")

    categoria_faturamento_df = (
        df_filtrado.groupby("categoria")["faturamento"]
        .sum()
        .reset_index()
    )

    grafico_categoria = px.pie(
        categoria_faturamento_df,
        names="categoria",
        values="faturamento",
        hole=0.55,
        color_discrete_sequence=[
            "#4F46E5",
            "#10B981",
            "#F59E0B",
            "#EF4444",
            "#8B5CF6",
            "#06B6D4",
            "#84CC16"
        ]
    )

    grafico_categoria.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<extra></extra>"
    )

    grafico_categoria.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(
        grafico_categoria,
        use_container_width=True
    )

st.divider()


# ==============================
# SEGUNDA LINHA DE GRÁFICOS
# ==============================

col1, col2 = st.columns(2)

# ------------------------------------
# EVOLUÇÃO DO FATURAMENTO
# ------------------------------------

with col1:

    st.subheader("📈 Evolução do Faturamento")

    vendas_mes_df = (
        df_filtrado.groupby(["mes", "nome_mes"])["faturamento"]
        .sum()
        .reset_index()
        .sort_values("mes")
    )

    grafico_mes = px.line(
        vendas_mes_df,
        x="nome_mes",
        y="faturamento",
        markers=True
    )

    grafico_mes.update_traces(
        line=dict(width=4),
        marker=dict(size=10),
        hovertemplate="<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>"
    )

    grafico_mes.update_layout(
        xaxis_title="Mês",
        yaxis_title="Faturamento",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        grafico_mes,
        use_container_width=True
    )


# ------------------------------------
# LUCRO POR CATEGORIA
# ------------------------------------

with col2:

    st.subheader("💰 Lucro por Categoria")

    lucro_categoria_df = (
        df_filtrado.groupby("categoria")["lucro"]
        .sum()
        .reset_index()
        .sort_values("lucro", ascending=False)
    )

    grafico_lucro = px.bar(
        lucro_categoria_df,
        x="categoria",
        y="lucro",
        color_discrete_sequence=["#F59E0B"]
    )

    grafico_lucro.update_traces(
        texttemplate="R$ %{y:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Lucro: R$ %{y:,.2f}<extra></extra>"
    )

    grafico_lucro.update_layout(
        xaxis_title="Categoria",
        yaxis_title="Lucro",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        grafico_lucro,
        use_container_width=True
    )

st.divider()


# ==============================
# TERCEIRA LINHA DE GRÁFICOS
# ==============================

col1, col2 = st.columns(2)

# ------------------------------------
# DESEMPENHO DOS FUNCIONÁRIOS
# ------------------------------------

with col1:

    st.subheader("👨‍💼 Desempenho dos Funcionários")

    funcionarios_df = (
        df_filtrado.groupby("funcionario")["faturamento"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    grafico_funcionarios = px.bar(
        funcionarios_df,
        x="faturamento",
        y="funcionario",
        orientation="h",
        color_discrete_sequence=["#6366F1"],
        title="Ranking de Funcionários"
    )

    grafico_funcionarios.update_traces(
        texttemplate="R$ %{x:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>"
    )

    grafico_funcionarios.update_layout(
        xaxis_title="Faturamento",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        grafico_funcionarios,
        use_container_width=True
    )


# ------------------------------------
# FATURAMENTO POR CIDADE
# ------------------------------------

with col2:

    st.subheader("🌎 Faturamento por Cidade")

    cidades_df = (
        df_filtrado.groupby("cidade")["faturamento"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    grafico_cidades = px.bar(
        cidades_df,
        x="faturamento",
        y="cidade",
        orientation="h",
        color_discrete_sequence=["#14B8A6"],
        title="Ranking das Cidades"
    )

    grafico_cidades.update_traces(
        texttemplate="R$ %{x:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>"
    )

    grafico_cidades.update_layout(
        xaxis_title="Faturamento",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        grafico_cidades,
        use_container_width=True
    )

st.divider()


# ==============================
# QUARTA LINHA DE GRÁFICOS
# ==============================

st.divider()

col1, col2 = st.columns(2)


# ------------------------------------
# TOP CLIENTES POR FATURAMENTO
# ------------------------------------

with col1:

    st.subheader("👥 Top Clientes por Faturamento")


    clientes_df = (
        df_filtrado.groupby("id_cliente")["faturamento"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )


    grafico_clientes = px.bar(
        clientes_df,
        x="faturamento",
        y="id_cliente",
        orientation="h",
        color_discrete_sequence=["#8B5CF6"]
    )


    grafico_clientes.update_traces(
        texttemplate="R$ %{x:,.0f}",
        textposition="outside",
        hovertemplate="<b>Cliente %{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>"
    )


    grafico_clientes.update_layout(
        xaxis_title="Faturamento",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )


    st.plotly_chart(
        grafico_clientes,
        use_container_width=True
    )



# ------------------------------------
# QUANTIDADE DE CLIENTES POR CIDADE
# ------------------------------------

with col2:

    st.subheader("🌎 Clientes por Cidade")


    clientes_cidade_df = (
        df_filtrado.groupby("cidade")["id_cliente"]
        .nunique()
        .reset_index()
        .sort_values(
            "id_cliente",
            ascending=False
        )
    )


    grafico_clientes_cidade = px.bar(
        clientes_cidade_df,
        x="cidade",
        y="id_cliente",
        color_discrete_sequence=["#06B6D4"]
    )


    grafico_clientes_cidade.update_traces(
        texttemplate="%{y}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Clientes: %{y}<extra></extra>"
    )


    grafico_clientes_cidade.update_layout(
        xaxis_title="Cidade",
        yaxis_title="Quantidade de clientes",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )


    st.plotly_chart(
        grafico_clientes_cidade,
        use_container_width=True
    )


st.divider()


# ==============================
# INSIGHTS
# ==============================

st.subheader("💡 Insights")

if df_filtrado.empty:

    st.warning("Nenhum dado encontrado para os filtros selecionados.")

else:

    categoria_top = (
        df_filtrado.groupby("categoria")["faturamento"]
        .sum()
        .idxmax()
    )

    funcionario_top = (
        df_filtrado.groupby("funcionario")["faturamento"]
        .sum()
        .idxmax()
    )

    cidade_top = (
        df_filtrado.groupby("cidade")["faturamento"]
        .sum()
        .idxmax()
    )

    livro_top = (
        df_filtrado.groupby("titulo")["quantidade"]
        .sum()
        .idxmax()
    )

    st.success(f"📚 Categoria com maior faturamento: {categoria_top}")
    st.success(f"👨‍💼 Funcionário destaque: {funcionario_top}")
    st.success(f"🌎 Cidade com maior faturamento: {cidade_top}")
    st.success(f"🏆 Livro mais vendido: {livro_top}")

st.divider()


# ==============================
# TABELA
# ==============================

st.subheader("📋 Dados da Livraria")

st.dataframe(df_filtrado)


st.divider()

col1, col2 = st.columns([3,1])

with col1:
    st.subheader("📥 Exportar Dados")

with col2:
    csv = df_filtrado.to_csv(index=False).encode("utf-8")

    st.download_button(
    "📥 Baixar relatório CSV",
    csv,
    "relatorio_livraria_aurora.csv",
    "text/csv"
)
























    

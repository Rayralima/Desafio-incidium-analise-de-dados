import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard Analítico BanVic",
    page_icon="🏦",
    layout="wide",
)

# --- Carregamento e Preparação dos Dados (com Cache para Performance) ---
@st.cache_data
def carregar_e_preparar_dados():
    # Carregar todos os arquivos
    df_agencias = pd.read_csv('banvic_data/agencias.csv')
    df_clientes = pd.read_csv('banvic_data/clientes.csv')
    df_contas = pd.read_csv('banvic_data/contas.csv')
    df_propostas_credito = pd.read_csv('banvic_data/propostas_credito.csv')
    df_transacoes = pd.read_csv('banvic_data/transacoes.csv')

    # --- Limpeza e Conversões ---
    # Converte datas (fazemos isso uma vez aqui para todo o app)
    df_transacoes['data_transacao'] = pd.to_datetime(df_transacoes['data_transacao'], errors='coerce')
    df_propostas_credito['data_entrada_proposta'] = pd.to_datetime(df_propostas_credito['data_entrada_proposta'], errors='coerce')
    df_clientes['data_nascimento'] = pd.to_datetime(df_clientes['data_nascimento'], errors='coerce')

    # Criar colunas úteis (idade, ano, região)
    df_clientes['idade'] = (pd.Timestamp('now') - df_clientes['data_nascimento']).dt.days / 365.25
    df_transacoes['ano_transacao'] = df_transacoes['data_transacao'].dt.year

    def regiao_cep(cep):
        cep_str = str(cep).zfill(8)[:5]
        try:
            cep_num = int(cep_str)
            if 1000 <= cep_num <= 39999: return 'Sudeste'
            elif 40000 <= cep_num <= 65999: return 'Nordeste'
            elif 80000 <= cep_num <= 99999: return 'Sul'
            elif 70000 <= cep_num <= 79999: return 'Centro-Oeste'
            elif 66000 <= cep_num <= 69999: return 'Norte'
            else: return 'Outro'
        except (ValueError, TypeError):
            return 'Outro'
    df_clientes['regiao'] = df_clientes['cep'].apply(regiao_cep)

    # --- Unir DataFrames para criar uma base única para filtragem ---
    df_merged = pd.merge(df_transacoes, df_contas, on='num_conta', how='left')
    df_merged = pd.merge(df_merged, df_clientes, on='cod_cliente', how='left')
    df_merged = pd.merge(df_merged, df_agencias, on='cod_agencia', how='left')
    
    return df_merged, df_propostas_credito

df_merged, df_propostas_credito = carregar_e_preparar_dados()


# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano (corrigido)
anos_disponiveis = sorted(df_merged['ano_transacao'].dropna().unique().astype(int))
anos_selecionados = st.sidebar.multiselect("Selecione o Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Região (corrigido)
regioes_disponiveis = sorted(df_merged['regiao'].dropna().unique())
regioes_selecionadas = st.sidebar.multiselect("Selecione a Região", regioes_disponiveis, default=regioes_disponiveis)

# Filtro de Status da Proposta (corrigido)
status_disponiveis = sorted(df_propostas_credito['status_proposta'].dropna().unique())
status_selecionados = st.sidebar.multiselect("Status da Proposta de Crédito", status_disponiveis, default=status_disponiveis)


# --- Filtragem dos DataFrames com base nas seleções ---
df_filtrado = df_merged[
    (df_merged['ano_transacao'].isin(anos_selecionados)) &
    (df_merged['regiao'].isin(regioes_selecionadas))
]

df_propostas_filtrado = df_propostas_credito[
    df_propostas_credito['status_proposta'].isin(status_selecionados)
]


# --- Conteúdo Principal ---
st.title("🏦 Dashboard Analítico do BanVic")
st.markdown("Use os filtros na barra lateral para explorar os dados de forma dinâmica.")

st.markdown("---")

# --- Análises e Gráficos ---

# Usando colunas para organizar o layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Tipos de Transações Mais Comuns")
    if not df_filtrado.empty:
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        sns.countplot(y=df_filtrado['nome_transacao'], order=df_filtrado['nome_transacao'].value_counts().index, ax=ax1, palette='viridis')
        ax1.set_title('')
        ax1.set_xlabel('Número de Transações')
        ax1.set_ylabel('Tipo de Transação')
        st.pyplot(fig1)
    else:
        st.warning("Nenhum dado de transação para exibir com os filtros atuais.")

with col2:
    st.subheader("Status das Propostas de Crédito")
    if not df_propostas_filtrado.empty:
        status_counts = df_propostas_filtrado['status_proposta'].value_counts()
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.barplot(x=status_counts.index, y=status_counts.values, ax=ax2, palette='magma')
        ax2.set_title('')
        ax2.set_xlabel('Status')
        ax2.set_ylabel('Contagem')
        st.pyplot(fig2)
    else:
        st.warning("Nenhuma proposta de crédito para exibir com os filtros atuais.")

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Distribuição de Idade dos Clientes")
    if not df_filtrado.empty:
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.histplot(df_filtrado['idade'].dropna(), bins=20, kde=True, ax=ax3)
        ax3.set_title('')
        ax3.set_xlabel('Idade')
        ax3.set_ylabel('Número de Clientes')
        st.pyplot(fig3)
    else:
        st.warning("Nenhum dado de cliente para exibir com os filtros atuais.")

with col4:
    st.subheader("Distribuição de Clientes por Região")
    if not df_filtrado.empty:
        regiao_counts = df_filtrado['regiao'].value_counts()
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        sns.barplot(x=regiao_counts.index, y=regiao_counts.values, ax=ax4, palette='plasma')
        ax4.set_title('')
        ax4.set_xlabel('Região')
        ax4.set_ylabel('Número de Clientes')
        st.pyplot(fig4)
    else:
        st.warning("Nenhum dado de cliente para exibir com os filtros atuais.")


# --- Tabela de Dados Detalhados ---
st.markdown("---")
st.subheader("Dados Detalhados (Amostra)")
if not df_filtrado.empty:
    st.dataframe(df_filtrado.head(100))
else:
    st.warning("Nenhum dado detalhado para exibir com os filtros atuais.")

# Importando Bibliotecas:
import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pycountry
import streamlit as st

# Configuração da Página do Streamlit

st.set_page_config(
    page_title="Dashboard para o BanVic",
    page_icon="🏦",
    layout="wide",
)

# --- Carregamento dos dados ---
df_agencias = pd.read_csv('banvic_data/agencias.csv', sep=',')
df_clientes = pd.read_csv('banvic_data/clientes.csv', sep=',')
df_colaboradores = pd.read_csv('banvic_data/colaboradores.csv', sep=',')
df_colaborador_agencia = pd.read_csv('banvic_data/colaborador_agencia.csv', sep=',')
df_contas = pd.read_csv('banvic_data/contas.csv', sep=',')
df_propostas_credito = pd.read_csv('banvic_data/propostas_credito.csv', sep=',')
df_transacoes = pd.read_csv('banvic_data/transacoes.csv', sep=',')
df_economia = pd.read_csv('banvic_data/dados_economicos.csv', sep=',')

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
df_transacoes['data_transacao'] = pd.to_datetime(df_transacoes['data_transacao'], errors='coerce')
anos_disponiveis = sorted(df_transacoes['data_transacao'].dt.year.unique())
ano_selecionado = st.sidebar.selectbox("Selecione o Ano:", anos_disponiveis)
# Filtro de Tipo de Conta
tipo_conta_selecionado = st.sidebar.selectbox("Selecione o Tipo de Conta:", df_contas['tipo_conta'].unique())
anos_selecionados = st.sidebar.multiselect("Tipo", df_contas['tipo_conta'].unique(), default=tipo_conta_selecionado)
# Filtro de Região
regiao_selecionada = st.sidebar.selectbox("Selecione o Estado:", df_agencias['uf'].unique())
anos_selecionados = st.sidebar.multiselect("Estado", df_agencias['uf'].unique(), default=regiao_selecionada)
# Filtro de Status da Proposta de Crédito
status_proposta_selecionado = st.sidebar.selectbox("Selecione o Status da Proposta de Crédito:", df_propostas_credito['status_proposta'].unique())
anos_selecionados = st.sidebar.multiselect("Tipo", df_contas['tipo_conta'].unique(), default=tipo_conta_selecionado)
# Filtro de Tipo de Cliente
tipo_cliente_selecionado = st.sidebar.selectbox("Selecione o Tipo de Cliente:", df_clientes['tipo_cliente'].unique())
anos_selecionados = st.sidebar.multiselect("Tipo", df_clientes['tipo_cliente'].unique(), default=tipo_cliente_selecionado)
# Filtro de Tipo de Agência
tipo_agencia_selecionado = st.sidebar.selectbox("Selecione o Tipo de Agência:", df_agencias['tipo_agencia'].unique())
anos_selecionados = st.sidebar.multiselect("Tipo", df_agencias['tipo_agencia'].unique(), default=tipo_agencia_selecionado)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_transacoes_filtrado = df_transacoes[df_transacoes['data_transacao'].dt.year.isin(anos_selecionados)]
df_contas_filtrado = df_contas[df_contas['tipo_conta'].isin(anos_selecionados)]
df_agencias_filtrado = df_agencias[df_agencias['uf'].isin(anos_selecionados)]
df_propostas_credito_filtrado = df_propostas_credito[df_propostas_credito['status_proposta'].isin(anos_selecionados)]
df_clientes_filtrado = df_clientes[df_clientes['tipo_cliente'].isin(anos_selecionados)]
df_contas_filtrado = df_contas[df_contas['tipo_conta'].isin(anos_selecionados)]

# --- Conteúdo Principal ---
st.title("🏦 Dashboard Interativo para o BanVic")
st.markdown("Bem-vindo ao dashboard interativo do BanVic! Utilize os filtros na barra lateral para explorar os dados de forma dinâmica.")
st.header("📊 Análises e Visualizações")
# Volume de propostas de crédito por ano, mês e dia da semana:
df_propostas_credito_agrupado = df_propostas_credito_filtrado.groupby(['data_entrada_proposta']).size().reset_index(name='volume')
# Status das propostas de crédito:
st.subheader("Status das Propostas de Crédito")
df_propostas_credito_status = df_propostas_credito_filtrado['status_proposta'].value_counts()
st.bar_chart(df_propostas_credito_status)
# Volume de propostas de crédito em relação com o a Inflação (IPCA) e a taxa de juros Selic do Banco Central:
df_propostas_credito['data_entrada_proposta'] = pd.to_datetime(df_propostas_credito['data_entrada_proposta'], errors='coerce')
df_propostas_credito_mensal = df_propostas_credito.resample('M', on='data_entrada_proposta').size().reset_index(name='novas_propostas')

df_economia['data'] = pd.to_datetime(df_economia['data'], errors='coerce')

fig, ax1 = plt.subplots(figsize=(14, 8))
color = 'tab:blue'
ax1.set_xlabel('Data', fontsize=12)
ax1.set_ylabel('Número de Propostas', color=color, fontsize=12)
ax1.plot(df_propostas_credito_mensal['data_entrada_proposta'], df_propostas_credito_mensal['novas_propostas'], color=color, marker='o', label='Nº Novas Propostas')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()

color = 'tab:red'
ax2.set_ylabel('Taxas (%)', color=color, fontsize=12)
ax2.plot(df_economia['data'], df_economia['selic_mensal'], color='red', linestyle='--', label='Selic Mensal (%)')
ax2.plot(df_economia['data'], df_economia['ipca_mensal'], color='green', linestyle=':', label='IPCA Mensal (%)')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Propostas de Crédito vs. Indicadores Econômicos', fontsize=16)
fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
plt.grid(True)
fig.tight_layout()
plt.show()

# Análise demográfica dos clientes (idade, localização, tipo de cliente):
df_clientes['data_nascimento'] = pd.to_datetime(df_clientes['data_nascimento'], errors='coerce')
idade = pd.Timestamp('now')
df_clientes['idade'] = (idade - df_clientes['data_nascimento']).dt.days / 365.25
df_clientes.dropna(subset=['data_nascimento'], inplace=True)
plt.style.use('seaborn-v0_8-whitegrid')
plt.figure(figsize=(10,6))
plt.hist(df_clientes['idade'], bins=15, color='skyblue', edgecolor='black')
plt.title('Distribuição de Idade dos Clientes', fontsize=16)
plt.xlabel('Idade', fontsize=14)
plt.ylabel('Número de Clientes', fontsize=14)
plt.show()

# Idade média dos clientes:
media_idade = df_clientes['idade'].mean()
print(f'Idade média dos clientes: {media_idade:.0f} anos')

# Distribuição geográfica dos clientes (região baseada no CEP):
def regiao_cep(cep):
    cep_str = str(cep).replace('-', '').replace('.', '').strip()
    cep = str(cep).zfill(8)
    try:
        cep_num = int(cep_str[:5])
    except (ValueError, TypeError):
        return 'Desconhecida'
    if 1000 <= cep_num <= 39999:
        return 'Sudeste'
    elif 40000 <= cep_num <= 65999:
        return 'Nordeste'
    elif 80000 <= cep_num <= 99999:
        return 'Sul'
    elif 70000 <= cep_num <= 79999:
        return 'Centro-Oeste'
    elif 66000 <= cep_num <= 69999:
        return 'Norte'
    else:
        return 'Desconhecida'

df_clientes['regiao'] = df_clientes['cep'].apply(regiao_cep)
regiao_contagem = df_clientes['regiao'].value_counts().sort_values(ascending=False)

plt.figure(figsize=(12,7))
sns.barplot(x=regiao_contagem.index, y=regiao_contagem.values)
plt.title('Distribuição de Clientes por Região')
plt.xlabel('Região')
plt.ylabel('Número de Clientes')
print("Contagem de clientes por região:")
print(regiao_contagem)
plt.show()

# Crescimento do número de agências ao longo dos anos:
df_agencias['data_abertura'] = pd.to_datetime(df_agencias['data_abertura'], errors='coerce')
df_agencias['ano_abertura'] = df_agencias['data_abertura'].dt.year

agencias_ano = df_agencias['ano_abertura'].value_counts().sort_index()

plt.figure(figsize=(12,7))
sns.barplot(x=agencias_ano.index, y=agencias_ano.values, palette='viridis')
plt.title('Número de Agências Abertas por Ano')
plt.xlabel('Ano de Abertura')
plt.ylabel('Número de Agências')
plt.xticks(rotation=45)
plt.show()

# Crescimento do número de contas ao longo dos anos:
df_contas['data_abertura'] = pd.to_datetime(df_contas['data_abertura'], errors='coerce')
df_contas['ano_abertura'] = df_contas['data_abertura'].dt.year

contas_ano = df_contas['ano_abertura'].value_counts().sort_index()

plt.figure(figsize=(12,7))
sns.barplot(x=contas_ano.index, y=contas_ano.values, palette='viridis')
plt.title('Número de Contas Abertas por Ano')
plt.xlabel('Ano de Abertura')
plt.ylabel('Número de Contas')
plt.xticks(rotation=45)
plt.show()

# Volume de transações por tipo de agência:
volume_por_agencia = df_agencias.merge(df_contas, on='cod_agencia').merge(df_transacoes, on='num_conta')
volume_por_agencia = volume_por_agencia.groupby('tipo_agencia')['valor_transacao'].sum().sort_values(ascending=False)
print(volume_por_agencia)

plt.figure(figsize=(12,8))
volume_por_agencia.plot(kind='barh', color=sns.color_palette('rocket'))
plt.title('Volume Total de Transações por Tipo de Agência')
plt.xlabel('Volume Total de Transações (R$)')
plt.ylabel('Tipo de Agência')
plt.show()

# Tipos de transações mais comuns e seu valor médio:
media_transacoes = df_transacoes['valor_transacao'].mean()
print(f'Valor médio das transações: R$ {media_transacoes:.2f}')

plt.figure(figsize=(10,6))
sns.countplot(y=df_transacoes['nome_transacao'], order=df_transacoes['nome_transacao'].value_counts().index, palette='viridis')
plt.title('Tipos de transações mais comuns:')
plt.xlabel('Número de Transações')
plt.ylabel('Tipo de Transação')
plt.show()

# Status das propostas de crédito:
df_propostas_credito['status_proposta'].value_counts()

df_propostas_credito['data_entrada_proposta'] = pd.to_datetime(df_propostas_credito['data_entrada_proposta'], errors='coerce')
df_propostas_credito['ano_entrada'] = df_propostas_credito['data_entrada_proposta'].dt.year
volume_anual_credito = df_propostas_credito.groupby('ano_entrada')['valor_proposta'].sum()

plt.figure(figsize=(12, 7))
volume_anual_credito.plot(kind='line', marker='o', color='green')
plt.title('Crescimento do Volume de Transações de Crédito por Ano', fontsize=16)
plt.ylabel('Volume Total de Crédito (R$)')
plt.xlabel('Ano')
plt.grid(True)
plt.show()

# Volume de propostas de crédito por dia da semana:
df_propostas_credito['data_entrada_proposta'] = pd.to_datetime(df_propostas_credito['data_entrada_proposta'], errors='coerce')
volume_por_dia_num = df_propostas_credito.groupby(
    df_propostas_credito['data_entrada_proposta'].dt.dayofweek
)['valor_proposta'].sum()
dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
volume_por_dia_num.index = dias_semana
volume_por_dia_num = volume_por_dia_num.reindex(dias_semana)

plt.figure(figsize=(12,7))
sns.barplot(x=volume_por_dia_num.index, y=volume_por_dia_num.values, palette='magma')
plt.title('Volume de Propostas de Crédito por Dia da Semana')
plt.xlabel('Dia da Semana')
plt.ylabel('Volume Total de Propostas (R$)')
plt.xticks(rotation=45)
plt.show()

# Volume de propostas de crédito por mês:
df_propostas_credito['data_entrada_proposta'] = pd.to_datetime(df_propostas_credito['data_entrada_proposta'], errors='coerce')
volume_por_mes_num = df_propostas_credito.groupby(
    df_propostas_credito['data_entrada_proposta'].dt.month
)['valor_proposta'].sum()
dias_mes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
volume_por_mes_num.index = dias_mes
volume_por_mes_num = volume_por_mes_num.reindex(dias_mes)

plt.figure(figsize=(12,7))
sns.barplot(x=volume_por_mes_num.index, y=volume_por_mes_num.values, palette='magma')
plt.title('Volume de Propostas de Crédito por Mês')
plt.xlabel('Mês')
plt.ylabel('Volume Total de Propostas (R$)')
plt.xticks(rotation=45)
plt.show()
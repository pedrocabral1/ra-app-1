import streamlit as st
import pandas as pd

# Função para exibir a página de Resumo Executivo com ajustes no layout
def show_resumo_executivo():
    st.title("Resumo Executivo das Reclamações 📋")

    # Certifique-se de que os dados foram carregados no `st.session_state`
    if 'data' in st.session_state:
        df = st.session_state['data']

        # Verificar se as colunas esperadas existem no DataFrame
        colunas_necessarias = ['empresa', 'estado', 'cidade', 'status', 'casos', 'bandeira', 'logo']
        for coluna in colunas_necessarias:
            if coluna not in df.columns:
                st.error(f"Coluna esperada '{coluna}' não encontrada nos dados. Verifique a estrutura dos dados carregados.")
                st.stop()

        # Adicionar a opção "Todos" para as seleções de estado e cidade
        df['estado'] = df['estado'].fillna('Todos')
        df['cidade'] = df['cidade'].fillna('Todos')

        # Acrescentar "Todos" no início das listas de seleção
        empresas = ['Todos'] + sorted(df['empresa'].unique().tolist())
        estados = ['Todos'] + sorted(df['estado'].unique().tolist())
        cidades = ['Todos'] + sorted(df['cidade'].unique().tolist())

        # Calcular totalizadores gerais, que não são influenciados pelos filtros
        total_reclamacoes_geral = df['casos'].sum()
        total_status = df['status'].value_counts()

        st.markdown("---")

        # Layout dos filtros lado a lado (Empresa, Estado, Cidade)
        col4, col5, col6 = st.columns([1, 1, 1])
        with col4:
            empresa = st.selectbox("Selecione a Empresa", empresas, index=0)
        with col5:
            estado = st.selectbox("Selecione o Estado", estados, index=0)
        with col6:
            cidade = st.selectbox("Selecione a Cidade", cidades, index=0)

        # Filtragem dos dados conforme a seleção (empresa, estado, cidade)
        df_filtered = df.copy()
        if empresa != 'Todos':
            df_filtered = df_filtered[df_filtered['empresa'] == empresa]
        if estado != 'Todos':
            df_filtered = df_filtered[df_filtered['estado'] == estado]
        if cidade != 'Todos':
            df_filtered = df_filtered[df_filtered['cidade'] == cidade]

        # Calcular total de reclamações apenas para a empresa selecionada (não influenciado por estado e cidade)
        total_reclamacoes_empresa = df[df['empresa'] == empresa]['casos'].sum() if empresa != 'Todos' else total_reclamacoes_geral

        # Exibir total de reclamações filtradas por empresa em uma caixa de texto entre bandeira e logo
        st.markdown(f"<div style='text-align: center; background-color: #f0f0f0; padding: 10px; font-size: 20px;'><strong>Total de Reclamações para {empresa}: {total_reclamacoes_empresa}</strong></div>", unsafe_allow_html=True)

        st.markdown("---")

        # Calcular o total por status
        ranking_status = pd.DataFrame(total_status).reset_index()
        ranking_status.columns = ['Status', 'Número de Casos']

        # Ranking de estados e cidades
        ranking_estados = df['estado'].value_counts().reset_index()
        ranking_estados.columns = ['Estado', 'Número de Reclamações']

        ranking_cidades = df_filtered['cidade'].value_counts().reset_index()
        ranking_cidades.columns = ['Cidade', 'Número de Reclamações']

        # Exibição dos Rankings e Total por Status lado a lado
        col7, col8, col9 = st.columns([1, 1, 1])
        with col7:
            st.subheader("Ranking por Estado")
            st.dataframe(ranking_estados, height=300)

        with col8:
            st.subheader("Ranking por Cidade")
            st.dataframe(ranking_cidades, height=300)

        with col9:
            st.subheader("Total por Status")
            st.dataframe(ranking_status, height=300)

    else:
        st.warning("Dados não carregados. Por favor, carregue os dados antes de acessar esta página.")

import streamlit as st
import pandas as pd
import plotly.express as px

def show_dashboard():
    st.title("Dashboard Interativo 🗂️")

    # Certifique-se de que os dados foram carregados no `st.session_state`
    if 'data' in st.session_state:
        df = st.session_state['data']

        # Verificar se as colunas esperadas existem no DataFrame
        colunas_necessarias = ['empresa', 'estado', 'data', 'casos', 'descrição', 'status']
        colunas_faltando = [col for col in colunas_necessarias if col not in df.columns]
        
        if colunas_faltando:
            st.error(f"Colunas faltando nos dados: {', '.join(colunas_faltando)}. Verifique a estrutura dos dados.")
            st.stop()  # Interrompe a execução se colunas estiverem faltando

        # Adicionar a opção "Todos" às seleções
        empresas = ['Todos'] + sorted(df['empresa'].unique().tolist())
        estados = ['Todos'] + sorted(df['estado'].unique().tolist())
        status_options = ['Todos'] + sorted(df['status'].unique().tolist())

        # Layout dos filtros lado a lado
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            empresa = st.selectbox("Selecione a Empresa", empresas)
        with col2:
            estado = st.selectbox("Selecione o Estado", estados)
        with col3:
            status = st.selectbox("Selecione o Status", status_options)

        # Seletor para o tamanho do texto das descrições
        tamanho_min = st.slider("Selecione o Tamanho Mínimo do Texto das Descrições", min_value=0, max_value=int(df['descrição'].str.len().max()), value=0)

        # Filtragem dos dados conforme seleção
        df_filtered = df.copy()
        if empresa != 'Todos':
            df_filtered = df_filtered[df_filtered['empresa'] == empresa]
        if estado != 'Todos':
            df_filtered = df_filtered[df_filtered['estado'] == estado]
        if status != 'Todos':
            df_filtered = df_filtered[df_filtered['status'] == status]

        # Aplicar filtro pelo tamanho mínimo do texto
        df_filtered = df_filtered[df_filtered['descrição'].str.len() >= tamanho_min]

        # Gráficos de série temporal de reclamações
        if empresa == 'Todos':
            # Quando todas as empresas são selecionadas, criar um gráfico para cada uma e exibir em colunas
            empresas_unicas = df['empresa'].unique().tolist()
            col4, col5, col6 = st.columns(3)

            for idx, emp in enumerate(empresas_unicas):
                emp_data = df_filtered[df_filtered['empresa'] == emp]
                fig = px.line(emp_data, x='data', y='casos', title=f'Série Temporal - Reclamações de {emp}')
                if idx == 0:
                    col4.plotly_chart(fig, use_container_width=True)
                elif idx == 1:
                    col5.plotly_chart(fig, use_container_width=True)
                elif idx == 2:
                    col6.plotly_chart(fig, use_container_width=True)

        else:
            # Gráfico único para a empresa selecionada
            fig_tempo = px.line(df_filtered, x='data', y='casos', title=f'Série Temporal - Reclamações de {empresa} em {estado if estado != "Todos" else "Todos os Estados"}')
            st.plotly_chart(fig_tempo, use_container_width=True)

        # Organizar os gráficos seguintes em colunas lado a lado
        col7, col8 = st.columns(2)

        with col7:
            # Gráfico 1: Frequência por status das reclamações
            fig_status = px.histogram(df_filtered, x='status', y='casos', title=f'Frequência de Reclamações por Status - {empresa if empresa != "Todos" else "Todas as Empresas"}')
            st.plotly_chart(fig_status)

        with col8:
            # Gráfico 2: Distribuição do tamanho do texto das descrições das reclamações
            df_filtered['tamanho_descricao'] = df_filtered['descrição'].apply(len)
            fig_tamanho = px.histogram(df_filtered, x='tamanho_descricao', nbins=50, title=f'Distribuição do Tamanho das Descrições - {empresa if empresa != "Todos" else "Todas as Empresas"}')
            st.plotly_chart(fig_tamanho)

        # Gráfico 3: Frequência de reclamações por estado (deve ser exibido no final)
        fig_estado = px.histogram(df_filtered, x='estado', y='casos', title=f'Frequência de Reclamações por Estado - {empresa if empresa != "Todos" else "Todas as Empresas"}')
        st.plotly_chart(fig_estado, use_container_width=True)

    else:
        st.warning("Dados não carregados. Por favor, carregue os dados antes de acessar esta página.")

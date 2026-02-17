import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title='Análise vendas de carros',
    page_icon=":red_car:",
    layout='wide',
)

df = pd.read_csv('car_sales.csv')
df['Year'] = pd.to_datetime(df['Date']).dt.year
df['Month_Year'] = pd.to_datetime(df['Date']).dt.month
anos_disponiveis = sorted(df['Year'].unique())
mes_disponiveis = sorted(df['Month_Year'].unique())
company_disponiveis = sorted(df['Company'].unique())
region_disponiveis = sorted(df['Dealer_Region'].unique())

st.sidebar.header("FILTROS")
year_selecionado = st.sidebar.multiselect(label='Ano',
                                         placeholder='Selecione um ano',
                                         options=anos_disponiveis,
                                         default=anos_disponiveis)

month_selecionado = st.sidebar.multiselect(label='Mês',
                                         placeholder='Selecione um mês',
                                         options=mes_disponiveis)

company_selecionado = st.sidebar.multiselect(label='Company',
                                             placeholder='Selecione uma Company',
                                             options=company_disponiveis)

region_selecionado = st.sidebar.multiselect(label='Region',
                                            placeholder='Selecione uma Region',
                                            options=region_disponiveis)

df_filtrado = df.copy()
if year_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Year'].isin(year_selecionado)]

if month_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Month_Year'].isin(month_selecionado)]

if company_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Company'].isin(company_selecionado)]

if region_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Region'].isin(region_selecionado)]

#df_filtrado = df[df['Year'].isin(year_selecionado)]
st.title('Dashboard de Análise de Vendas de Carros')
st.subheader('Visão estratégica das vendas por período, marca, modelo e região.')
st.markdown('---')

if not df_filtrado.empty:
    faturamento_total = df_filtrado['Price ($)'].sum()
    volume_total = df_filtrado['Car_id'].value_counts().sum()
    ticket_medio = faturamento_total / volume_total
    company_leader = df_filtrado['Company'].mode()[0]
else:
    faturamento_total = volume_total = ticket_medio = company_leader = ''

col1, col2, col3, col4 = st.columns(4)
col1.metric(label='Faturamento',
            value=faturamento_total,
            format='compact')

col2.metric(label='Total de carros vendidos',
            value=volume_total,
            format='compact')

col3.metric(label='Ticket médio',
            value=ticket_medio,
            format='compact')

col4.metric(label='Company líder',
            value=company_leader)

st.markdown('---')

st.subheader('Gráficos')
tab1, tab2, tab3, tab4 = st.tabs(['VISÃO GERAL',
                                  'MARCAS',
                                  'REGIÃO',
                                  'FINANCEIRO'])
colors=['red', 'blue']

if not df_filtrado.empty:
    with tab1:
        
            st.write('Nada aqui :(')
            '''vendas_por_tempo = df_filtrado.groupby(['Car_id', 'Month_Year']).value_counts().reset_index(name='Total')
            df_pivot_vendas = vendas_por_tempo.pivot(index='Month_Year',
                                                    columns='Car_id',
                                                    values='Total')
            st.line_chart(df_pivot_vendas)'''
    with tab2:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            ranking_companys = df_filtrado['Company'].value_counts().reset_index()
            ranking_companys.columns = ['Company', 'Total']
            st.bar_chart(ranking_companys,
                         x='Company',
                         y='Total',
                         horizontal=True,
                         sort='-Total',
                         color='Total')
            
        with col_t2:
            fig = go.Figure()
            fig.add_traces(go.Pie(
                labels=ranking_companys['Company'],
                values=ranking_companys['Total']
            ))
            fig
    
    st.subheader("Top 10 modelos mais vendidos")
    df_top_modelos = (df_filtrado.groupby(['Model', 'Company'], as_index=False).agg(Vendas=('Car_id', 'count'),
                                                                                   Faturamento=('Price ($)', 'sum'),
                                                                                   Preço_medio=('Price ($)', 'mean'))
                                                                                   .sort_values('Vendas', ascending=False)).head(10)
    
    df_top_modelos['Preço_medio'] = df_top_modelos['Preço_medio'].round(2)
    st.dataframe(df_top_modelos)
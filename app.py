import pandas as pd
import streamlit as st
import plotly.express as px
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
st.space('medium')

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
            format='compact',
            border=True)

col2.metric(label='Total de carros vendidos',
            value=volume_total,
            format='compact',
            border=True)

col3.metric(label='Ticket médio',
            value=ticket_medio,
            format='compact',
            border=True)

col4.metric(label='Company líder',
            value=company_leader,
            border=True)

#st.markdown('---')

st.subheader('Gráficos')
tab1, tab2, tab3, tab4 = st.tabs([':material/bar_chart_4_bars: VISÃO GERAL',
                                  ':material/shoppingmode: MARCAS',
                                  ':material/location_on: REGIÃO',
                                  ':material/attach_money: FINANCEIRO'])
colors=['red', 'blue']

if not df_filtrado.empty:
    with tab1:
        st.subheader("Vendas por mês")
        df_timeline_vendas = (df_filtrado.groupby(['Year', 'Month_Year']).size().reset_index(name='Vendas').sort_values(['Year', 'Month_Year']))
        meses_nome = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }
        df_timeline_vendas["Mês"] = df_timeline_vendas["Month_Year"].map(meses_nome) + "/" + df_timeline_vendas["Year"].astype(str)
        
        fig = px.line(df_timeline_vendas,
              x='Mês',
              y='Vendas',
              #title='Vendas por Mês',
              color_discrete_sequence=['#ED1C24'],
              markers=True)

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Quantidade de Vendas",
            hovermode="x unified",
            
        )

        fig.update_traces(
            line=dict(width=4),
            marker=dict(size=8)
        )

        st.plotly_chart(fig,
                        use_container_width=True,
                        theme='streamlit')

    with tab2:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.subheader("Vendas por Company")
            
            ranking_companys = df_filtrado['Company'].value_counts().reset_index()
            ranking_companys.columns = ['Company', 'Total']
            ranking_companys_completo = ranking_companys.sort_values('Total', ascending=False)
            ranking_companys = ranking_companys.head(10).sort_values('Total', ascending=True)
            
        

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=ranking_companys['Company'],
                x=ranking_companys['Total'],
                orientation='h',
                marker_color="#ED1C24",
                text=ranking_companys['Total'],
                textposition='inside',
                textfont=dict(color="#FFFFFF", size=20)
            ))

            fig.update_layout(
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(tickfont=dict(size=12)),
                margin=dict(l=100, r=40, t=10, b=10)
            )

            st.plotly_chart(fig,
                            use_container_width=True,
                            theme='streamlit')
            
            with st.popover("Ranking completo"):
                st.table(ranking_companys_completo)
            
        with col_t2:
            st.subheader("% Market share")
            ranking_companys = ranking_companys.sort_values('Total', ascending=False).reset_index(drop=True)
            cores = ['#ED1C24'] + ['#CCCCCC'] * (len(ranking_companys) - 1)
            fig = go.Figure()
            fig.add_trace(go.Pie(
                labels=ranking_companys['Company'],
                values=ranking_companys['Total'],
                marker_colors=cores,
                hole=0.5,
                pull=[.2] + [0] * (len(ranking_companys) - 1)  # Destaca a primeira fatia
            ))
            fig.update_layout(
                showlegend=True,
                legend_title_text='Company',
                margin=dict(l=100, r=40, t=10, b=10)
            )
            st.plotly_chart(fig,
                            use_container_width=True,
                            theme='streamlit')
    
        st.subheader("Top 10 modelos mais vendidos")
        df_top_modelos = (df_filtrado.groupby(['Model', 'Company'], as_index=False).agg(Vendas=('Car_id', 'count'),
                                                                                    Faturamento=('Price ($)', 'sum'),
                                                                                    Preço_medio=('Price ($)', 'mean'))
                                                                                    .sort_values('Vendas', ascending=False)).head(10)
        
        df_top_modelos['Faturamento'] = df_top_modelos['Faturamento'].round(2)
        df_top_modelos['Preço_medio'] = df_top_modelos['Preço_medio'].round(2)
        st.table(df_top_modelos)

    with tab3:
        st.subheader("Vendas por região")
        top_region = df_filtrado['Dealer_Region'].value_counts(ascending=False).sort_values(ascending=True).reset_index()
        top_region.columns = ['Region', 'Vendas']
        fig = go.Figure()
        fig.add_traces(go.Bar(
            y=top_region['Region'],
            x=top_region['Vendas'],
            text=top_region['Vendas'],
            textposition='inside',
            textfont=dict(color="#FFFFFF", size=20),
            orientation='h',
            marker_color="#ED1C24"
        ))
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(size=12)),
            margin=dict(l=100, r=40, t=10, b=10)
        )
        st.plotly_chart(fig,
                        use_container_width=True,
                        theme='streamlit')
    
    with tab4:
        st.subheader("Distribuição de vendas por preço")
        eixo_preço = df_filtrado['Price ($)']

        fig = go.Figure()
        fig.add_trace(go.Histogram(
        x=eixo_preço,
        marker_color="#ED1C24",
        opacity=0.85
        ))
        fig.update_layout(
            xaxis_title_text='Valor da venda',
            yaxis_title_text='Quantidade',
            bargap=.2,
            margin=dict(l=100, r=40, t=10, b=10)
        )
        st.plotly_chart(fig,
                        use_container_width=True,
                        theme='streamlit')
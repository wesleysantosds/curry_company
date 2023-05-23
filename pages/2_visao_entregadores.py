# libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import datetime

# bibliotecas necessarias
import folium
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Entregadores', layout = 'wide')

# importar conjunto de dados
df = pd.read_csv('dataset/train.csv')

df1 = df.copy()

#1. excluindo as linhas 'NaN' e convertendo a coluna de idade para numero int
linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['City'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Festival'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

#2. convertendo a coluna ratings de texto para numero decimal (float)
df['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
df1['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], downcast="float")

#3. convertendo a coluna order_date de texto para data
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format  = '%d-%m-%Y')

#4.convertendo multiple_deliveries de texto para numero inteiro (int)
linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

#5.removendo os espacos dentro de strings/texto/object
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()

#6. limpando a coluna de time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

# ==================================================================
# barra lateral no streamlit
# ==================================================================
st.header('Marketplace - Visão Entregadores')

#image_path = r'C:\Users\wesle\Documents\repos\ftc_python\logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.to_datetime('2022-04-13').to_pydatetime(),
    min_value=pd.to_datetime('2022-02-11').to_pydatetime(),
    max_value=pd.to_datetime('2022-04-06').to_pydatetime(),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione a forma de trânsito')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==================================================================
# layout no streamlit
# ==================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.markdown("""---""")
        st.markdown('## Métricas Gerais')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)
        
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        
        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)
        
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição', pior_condicao )
    
    with st.container():
        st.markdown("""___""")
        st.markdown('## Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            df_avg_ratings_per_deliver = df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().round(2).reset_index()
            st.dataframe(df_avg_ratings_per_deliver)
        
        with col2:
            st.markdown('##### Avaliação média e o desvio padrão por tipo de tráfego')
            df_avg_std_ratings_by_traffic = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                                .groupby('Road_traffic_density')
                                                .agg({'Delivery_person_Ratings': ['mean', 'std']})
                                                .round(2))
            df_avg_std_ratings_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_ratings_by_traffic = df_avg_std_ratings_by_traffic.reset_index()
            st.dataframe(df_avg_std_ratings_by_traffic)
            
            st.markdown('##### Avaliação média e o desvio padrão por condições climáticas')
            df_avg_std_ratings_by_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                                .groupby('Weatherconditions')
                                                .agg({'Delivery_person_Ratings': ['mean', 'std'] })
                                                .round(2))
            df_avg_std_ratings_by_weather.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_ratings_by_weather = df_avg_std_ratings_by_weather.reset_index()
            st.dataframe(df_avg_std_ratings_by_weather)
            
    with st.container():
        st.markdown("""___""")
        st.markdown('## Velocida de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Os 10 entregadores mais rápidos por cidade')
            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                        .groupby(['City', 'Delivery_person_ID'])
                        .mean()                        
                        .sort_values(['City', 'Time_taken(min)'], ascending = True)
                        .round(2)
                        .reset_index())
            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop = True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('##### Os 10 entregadores mais lentos por cidade')
            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                        .groupby(['City', 'Delivery_person_ID'])
                        .mean()
                        .sort_values(['City', 'Time_taken(min)'], ascending = False)
                        .round(2)
                        .reset_index())
            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop = True)            
            st.dataframe(df3)
# libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessarias
import folium
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(
    page_title = 'Visão Empresa', 
    layout = 'wide'
)

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

#6. limpando a coluna de time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

# ==================================================================
# barra lateral no streamlit
# ==================================================================
st.header('Marketplace - Visão Empresa')

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
    'Quais as condições do trânsito',
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])
with tab1:
    with st.container():
        st.header('Pedidos por dia')
        cols = ['ID', 'Order_Date']
        df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
        fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Pedidos por tipo de tráfego')
            df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
            fig = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')
            st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            st.header('Pedidos por cidade e tipo de tráfego')
            df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
            st.plotly_chart(fig, use_container_width = True)
            
with tab2:
    with st.container():
        st.header('Quantidade de pedidos por semana')
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        st.header('Quantidade de pedidos por entregador por semana')
        df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
        df_aux = pd.merge(df_aux01, df_aux02, how = 'inner')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        fig = px.line(df_aux, x = 'week_of_year', y = 'order_by_deliver')
        st.plotly_chart(fig, use_container_width = True)
    
with tab3:
    st.header('Localização central de cada cidade por tipo de tráfego')
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup = location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width = 1024, height = 600)
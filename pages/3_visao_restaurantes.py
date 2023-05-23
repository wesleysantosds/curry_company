# libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import datetime

# bibliotecas necessarias
import folium
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Restaurantes', layout = 'wide')

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
st.header('Marketplace - Visão Restaurantes')

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
        st.header('Métricas')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)
        
        with col2:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance'] = (df1.loc[:, cols]
                                    .apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
                                    axis = 1))
            avg_distance = np.round(df1['distance'].mean(), 2)
            col2.metric('Distância média', avg_distance)
        
        with col3:
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2)
            col3.metric('Tempo médio com festival', df_aux)
        
        with col4:
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2)
            col4.metric('Desvio padrão com festival', df_aux)
        
        with col5:
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2)
            col5.metric('Tempo médio sem festival', df_aux)
        
        with col6:
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2)
            col6.metric('Desvio padrão sem festival', df_aux)
                
    with st.container():
        st.markdown("""___""")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Tempo médio e o DP de entrega por cidade')
            df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name = 'Control', x = df_aux['City'], y = df_aux['avg_time'], error_y = dict(type = 'data', array = df_aux['std_time'])))
            fig.update_layout(barmode = 'group')
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            st.markdown('##### Tempo médio e o DP de entrega por cidade e tipo de pedido')
            df_aux = np.round(df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']}), 2)
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux, use_container_width = True)

    with st.container():
        st.markdown("""___""")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Distância média dos restaurantes dos locais de entrega')
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance'] = (df1.loc[:, cols]
                                    .apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), 
                                    axis = 1))
            avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data = [go.Pie(labels = avg_distance['City'], values = avg_distance['distance'], pull = [0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            st.markdown('##### Tempo médio e o DP de entrega por cidade e tipo de tráfego')
            df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], values = 'avg_time',
                              color = 'std_time', color_continuous_scale = 'RdBu',
                              color_continuous_midpoint = np.average(df_aux['std_time']))
            st.plotly_chart(fig, use_container_width = True)
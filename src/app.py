from monitoramento import *
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import BeautifyIcon

APP_TITLE = 'CanaMaps'
APP_SUB_TITLE = 'Monitoramento Geoespacial de Pragas na Cana de Açúcar!'

def get_color(classe):
    if classe == 'AZUL':
        return '#4682B4'
    elif classe == 'VERDE':
        return '#3CB371'
    elif classe == 'AMARELO':
        return '#FFD700'
    elif classe == 'VERMELHO':
        return '#B22222'
    else:
        return '#808080'

def create_map(df):
    # Garantir que o CRS esteja no formato esperado pelo Folium
    df = df.to_crs(epsg=4326)
    
    # Obter o centro do mapa
    centroide_geral = df.geometry.unary_union.centroid
    m = folium.Map(location=[centroide_geral.y, centroide_geral.x], zoom_start=12)

    # Adicionar camada de imagem de satélite
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='ESRI',
        name='ESRI Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    # Converter todas as colunas do tipo datetime para string
    for col in df.select_dtypes(include=['datetime64[ns]']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d')
    
    # Converter GeoDataFrame para GeoJSON
    geojson_data = df.to_json()
    
    # Adicionar as camadas usando GeoJson para estilização dinâmica
    folium.GeoJson(
        data=geojson_data,
        style_function=lambda feature: {
            'fillColor': get_color(feature['properties']['CLASSE']),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.8
        },
        highlight_function=lambda feature: {
            "color": "red",
            "weight": 2,
            "dashArray": "5, 5"
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['TALHAO', 'CD_FA', 'FAZENDA', 'FORNECEDOR'],
            aliases=['Talhão:', 'Código:', 'Fazenda:', 'Fornecedor:'],
            localize=True,
            sticky=False,  # Para não gerar a caixa de destaque
            opacity=0.8
        )
    ).add_to(m)

    # Adicionar código da propriedade nos centróides das fazendas
    centroide_fazenda = df.dissolve(by='PROPRIEDAD').reset_index()
    centroide_fazenda['centroid'] = centroide_fazenda.geometry.centroid

    for _, row in centroide_fazenda.iterrows():
        latitude = row['centroid'].y
        longitude = row['centroid'].x
        codigo_propriedade = row['PROPRIEDAD']

        icon_number = folium.plugins.BeautifyIcon(
            border_color="transparent",
            background_color="transparent",
            number=codigo_propriedade,        
            text_color="green",
            inner_icon_style="font-size:17px;font-weight:900;text-shadow: 1px 1px 4px white, -1px -1px 4px white, 1px -1px 4px white, -1px 1px 4px white;margin-bottom: 25px;"
        )

        folium.Marker(
            location=[latitude, longitude],
            icon=icon_number
        ).add_to(m)

    # Renderizar o mapa no Streamlit
    st_map = st_folium(m, width='100%', height=900)

    if st_map['last_active_drawing']:
        st.write(st_map['last_active_drawing']['properties'])

def display_filter(title, columns):
    temp_list = st.session_state.data[columns].dropna().unique()
    temp_list.sort()
    return st.sidebar.selectbox(title, temp_list)

def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    #LOAD DATA
    gdf = gpd.read_file('data/frutal.geojson')
    if 'data' not in st.session_state:
        with st.spinner("Carregando os dados... isso pode levar alguns segundos..."):
                dfTemp = monitoramento()
                st.session_state.data = pd.merge(gdf.drop(columns=['SAFRA', 'REPONSAVEL']), dfTemp, left_on='UN', right_on='CODIGO', how='left')

    # MENU LATERAL
    st.sidebar.image("data/logo.jpg", width=150)
    st.sidebar.title('Filtros')

    #FILTROS
    usina = display_filter("Usina:", "USINA")
    responsavel = display_filter("Responsável:", "RESPONSAVEL")
    fornecedor = display_filter("Fornecedor:", "FORNECEDOR")

    df = st.session_state.data
    if usina:
        df = df[df['USINA'] == usina]
    if responsavel:
        df = df[df['RESPONSAVEL'] == responsavel]
    if fornecedor:
        df = df[df['FORNECEDOR'] == fornecedor]

    #METRICAS
    area_tt = df['AREA'].sum()
    area_title = f'Área'
    st.metric(area_title, f'{area_tt:,.2f} há'.replace(',','v').replace('.', ',').replace('v', '.'))

    cont_bloco = df['BLOCO'].count()
    cont_bloco_title = f'Qtd. Blocos'
    st.metric(cont_bloco_title, cont_bloco)

    #MAPA
    create_map(df)


if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import pandas as pd
import requests
import pydeck as pdk
from io import StringIO
import plotly.graph_objects as go

# https://endurotrails.pl/static/upload/store/pliki_gpx/Dziabarr.gpx
st.markdown('# Dodaj trasę endurotrails.pl')
title = st.text_input('Link do trasy endurotrails.pl', '')
# st.write('The current movie title is', title)
def parse_gpx_to_dataframe(gpx_url):
    # Pobierz zawartość pliku GPX z URL
    response = requests.get(gpx_url)

    if response.status_code == 200:
        # Parsowanie zawartości pliku GPX
        root = ET.fromstring(response.content)
        
        # Inicjalizacja pustych list na dane
        lon_list, lat_list, ele_list, time_list = [], [], [], []

        # Iteracja przez trkpt elementy w trkseg
        for trkpt in root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt"):
            lon = float(trkpt.get('lon'))
            lat = float(trkpt.get('lat'))
            ele = float(trkpt.find('{http://www.topografix.com/GPX/1/1}ele').text)
            time = trkpt.find('{http://www.topografix.com/GPX/1/1}time').text

            lon_list.append(lon)
            lat_list.append(lat)
            ele_list.append(ele)
            time_list.append(time)

        # Tworzenie DataFrame
        df = pd.DataFrame({'lon': lon_list, 'lat': lat_list, 'ele': ele_list, 'time': time_list})

        return df
    else:
        print("Nie można pobrać pliku GPX z URL.")
        return None


def get_trail_path(df, trail_difficulty):
    data = df
    path_color = [0, 0, 0]
    if trail_difficulty == 'blue':
        path_color = [0, 0, 255]
    if trail_difficulty == 'red':
        path_color = [255, 0, 0]
    if trail_difficulty == 'black':
        path_color = [0, 0, 0]
    
    path_data = [{
        "path": list(zip(data['lon'], data['lat'])),
        "name": "Trasa przejazdu"
    }]
    view_state = pdk.ViewState(
    latitude=data['lat'].mean(),
    longitude=data['lon'].mean(),
    zoom=15,
    pitch=50
    )

    layer = pdk.Layer(
        'PathLayer',
        path_data,
        get_path='path',
        get_width=5,
        get_color=path_color,
        width_scale=20,
        width_min_pixels=2,
        width_max_pixels=5
    )

    # Ustawienie jasnego tła mapy
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="light"
    )

    return r
# szybkie get opis

if title != '':
    st.write("Siema")
  
    gpx_url = title
    
    left_column, right_column = st.columns(2)
    data = parse_gpx_to_dataframe(gpx_url)

    with left_column:
        r = get_trail_path(data, trail_difficulty='blue')
        st.pydeck_chart(r)
    with right_column:
        st.markdown(
            """
            ### Opis trasy
             Ścieżka posiada sporo naturalnych i sztucznych elementów, np. słynna sekcja korzenim muldy, bandy i niewielkie hopki. Zaczyna się niedaleko schroniska, przy starym torze saneczkowym, a kończy przy centrum ścieżek. Trasa ta jest bardzo szybka (!), wymaga sporego asortymentu umiejętności i dużej kontroli roweru.

            W części górnej ścieżka była wcześniej zielonym szlakiem pieszym (stąd nazwa), cenionym bardzo przez bielskie środowisko MTB. Obecnie szlak pieszy przeniesiono parę metrów niżej do zabytkowego toru saneczkowego."""
        )
        twister = {
        'Nazwa': 'TODO',
        # 'Trudność': 'Trasa niebieska - dla średnio-zaawansowanych kolarzy górskich',
        # 'Widoczność': 'Trasa zawsze dobrze widoczna',
        # 'Długość[m]': 4400,
        # 'Podjazd[m]': 95,
        # 'Trudność podjazdu': 'Łatwy',
        # 'Spadek[m]': 270,
        # 'avg_duration': 0,
        
        # 'average_slope': 0,
        
        # 'description': 'Niezbyt stroma, ale bardzo zakręcona ścieżka. Zaczyna sięna wschodnim zboczu, nieopodal szczytu Koziej Góry. Dojazd na start z Błoni potrwa około 45 minut. Poradzi sobie na niej prawie każdy kolarz górski, trzeba jednak uważać na spore bandy i muldy. Należy też liczyć się z jej długością!',
        # 'file_name': 'twister.gpx',
        }
        df = pd.DataFrame.from_dict(twister, orient='index', columns=['Szczegółowe dane trasy'])
        st.dataframe(df,width=600, height=280)

    st.markdown("""---""")
    st.dataframe(data)
    get_enhanced_df = requests.post('http://localhost:5000/get_enhanced_df', json=data.to_json(orient='split'))
    df = pd.read_json(get_enhanced_df.text, orient='split')
    st.dataframe(df)
    
    get_plot_3d = requests.post('http://localhost:5000/get_3d_plot', json=df.to_json(orient='split'))
    plot_3d = get_plot_3d.json()
    st.subheader('Wizualizacja trasy w 3D')
    fig = go.Figure(plot_3d)
    st.plotly_chart(fig)

    get_map_descent_gradient = requests.post('http://localhost:5000/get_map_descent_gradient', json=df.to_json(orient='split'))
    map_descent_gradient = get_map_descent_gradient.json()
    st.subheader('Mapa spadku')
    fig = go.Figure(map_descent_gradient)
    st.plotly_chart(fig)
    

    # Informacje o danych
    st.sidebar.title('Informacje o danych')
    st.sidebar.write(df.describe())
    st.sidebar.title('Rozszerzone dane:')
    st.sidebar.dataframe(df)

    # df trasa 3d
    # df enhance DF

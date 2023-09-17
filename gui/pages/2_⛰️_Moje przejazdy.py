# streamlit_app.py

import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import json
import pydeck as pdk
from io import StringIO

# url = 'https://endurotrails.pl/static/upload/store/pliki_gpx/stary-zielony.gpx'

# payload = {"url": url}
# response = requests.post('http://localhost:5000/load_data', json=payload)

# df = pd.read_json(response.text, orient='split')



# st.dataframe(df)

# wczytanie ilosć itras z bazy danych
name='pparker'
st.sidebar.title(f"Welcome {name}")
st.sidebar.write(f"Tech stack: Web magician")
st.sidebar.write(f"Ilość przejazdów: {0}")
st.sidebar.write(f"Pokonane kilometry: {0}")
st.sidebar.write(f"Ilość km od ostatniego serwisu: {0}")

st.title('Dodaj przejazd')
uploaded_file = st.file_uploader("Wybierz plik")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    # 
    payload = {"route_data": string_data}

    response = requests.post('http://localhost:5000/transform_gpx_data', json=payload)

    df = pd.read_json(response.text, orient='split')
    # send string data to api to parse and get df in return
    
    get_basic_stats = requests.post('http://localhost:5000/get_basic_stats', json=df.to_json(orient='split'))
    basic_stats = get_basic_stats.json()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Wysokość startu**")
        st.write(f"{basic_stats['start_elevation']} m n.p.m.")
        st.write("**Średnia prędkość**")
        st.write(f"{basic_stats['average_speed']} km/h")
        st.write("**Najszybsze 10s**")
        st.write(f"{basic_stats['average_speed_top_10_seconds']} km/h")
    with col2:
        st.write("**Maksymalna wysokość**")
        st.write(f"{basic_stats['max_elevation']} m n.p.m.")
        st.write("**Maksymalna prędkość**")
        st.write(f"{basic_stats['max_speed']} km/h")
        st.write("**Najszybsze 30s**")
        st.write(f"{basic_stats['average_speed_top_30_seconds']} km/h")
    with col3:
        st.write("**Wysokość końca**")
        st.write(f"{basic_stats['end_elevation']} m n.p.m.")
        st.write("**Średni spadek**")
        st.write(f"{basic_stats['average_descent_segmented']} %")
        st.write("**Maksymalny spadek**")
        st.write(f"{basic_stats['max_descent']} %")



    get_plot_3d = requests.post('http://localhost:5000/get_3d_plot', json=df.to_json(orient='split'))
    plot_3d = get_plot_3d.json()
    st.subheader('Wizualizacja trasy w 3D')
    fig = go.Figure(plot_3d)
    st.plotly_chart(fig)


    # TODO
    # get_radar_plot = requests.post('http://localhost:5000/get_radar_plot', json=df.to_json(orient='split'))


    ##MAPY

    get_map_speed_gradient = requests.post('http://localhost:5000/get_map_speed_gradient', json=df.to_json(orient='split'))
    map_speed_gradient = get_map_speed_gradient.json()
    st.subheader('Mapa prędkości')
    fig = go.Figure(map_speed_gradient)
    st.plotly_chart(fig)

    get_map_descent_heatmap = requests.post('http://localhost:5000/get_map_descent_heatmap', json=df.to_json(orient='split'))
    map_descent_heatmap = get_map_descent_heatmap.json()
    st.subheader('Wizualizacja nachylenia trasy - heatmapa')
    fig = go.Figure(map_descent_heatmap)
    st.plotly_chart(fig)

    get_map_descent_gradient = requests.post('http://localhost:5000/get_map_descent_gradient', json=df.to_json(orient='split'))
    map_descent_gradient = get_map_descent_gradient.json()
    st.subheader('Wizualizacja nachylenia trasy - gradient')
    fig = go.Figure(map_descent_gradient)
    st.plotly_chart(fig)

    ##WYKRESY, WIZUALIZACJE

    get_map_speed_heatmap = requests.post('http://localhost:5000/get_map_speed_heatmap', json=df.to_json(orient='split'))
    map_speed_heatmap = get_map_speed_heatmap.json()
    st.subheader('Wizualizacja prędkości trasy - heatmapa')
    fig = go.Figure(map_speed_heatmap)
    st.plotly_chart(fig)

    get_radar_plot = requests.post('http://localhost:5000/get_radar_plot', json=df.to_json(orient='split'))
    radar_plot = get_radar_plot.json()
    st.subheader('Radar plot')
    fig = go.Figure(radar_plot)
    st.plotly_chart(fig)

    get_cummulative_descent = requests.post('http://localhost:5000/get_cummulative_descent', json=df.to_json(orient='split'))
    cummulative_descent = get_cummulative_descent.json()
    st.subheader('Kumulacyjny spadek wysokości')
    fig = go.Figure(cummulative_descent)
    st.plotly_chart(fig)

    get_speed_box_plot = requests.post('http://localhost:5000/speed_box_plot', json=df.to_json(orient='split'))
    speed_box_plot = get_speed_box_plot.json()
    st.subheader('Rozkład prędkości')
    fig = go.Figure(speed_box_plot)
    st.plotly_chart(fig)

    get_descent_change_plot = requests.post('http://localhost:5000/get_descent_change_plot', json=df.to_json(orient='split'))
    descent_change_plot = get_descent_change_plot.json()
    st.subheader('Zmiany nachylenia w czasie')
    fig = go.Figure(descent_change_plot)
    st.plotly_chart(fig)

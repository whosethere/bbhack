# streamlit_app.py

import streamlit as st
import sys
sys.path.append('../gui/tools')
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import xml.etree.ElementTree as ET
import pandas as pd
import requests
import math
from tools.data_processing import haversine, enhance_dataframe
# from tools.data_loader import get_data_from_url
from tools.data_loader import load_data

# Wczytanie danych
# @st.cache

# Ponowne przetestowanie funkcji

data = load_data()
data = enhance_dataframe(data.copy())
enhanced_data = data


st.title('Analiza trasy rowerowej')

start_elevation = enhanced_data['ele'].iloc[0]
max_elevation = enhanced_data['ele'].max()
end_elevation = enhanced_data['ele'].iloc[-1]
average_speed = enhanced_data['speeds'].mean()
max_speed = enhanced_data['speeds'].max()

# Obliczenie różnic czasu
enhanced_data['time_diff'] = (pd.to_datetime(enhanced_data['time']) - pd.to_datetime(enhanced_data['time'].shift(1))).dt.total_seconds()

# Ponowne obliczenie średniej prędkości w najszybszych 10 sekundach
top_10_seconds_speeds = enhanced_data.sort_values(by='speeds', ascending=False).head(int(10/enhanced_data['time_diff'].mean()))['speeds']
average_speed_top_10_seconds = top_10_seconds_speeds.mean()

# Ponowne obliczenie średniej prędkości w najszybszych 30 sekundach
top_30_seconds_speeds = enhanced_data.sort_values(by='speeds', ascending=False).head(int(30/enhanced_data['time_diff'].mean()))['speeds']
average_speed_top_30_seconds = top_30_seconds_speeds.mean()


# Wizualizacja obliczonych wartości
st.subheader('Podstawowe informacje o trasie:')
col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Wysokość startu**")
    st.write(f"{enhanced_data['ele'].iloc[0]:.2f} m n.p.m.")
    st.write("**Średnia prędkość**")
    st.write(f"{enhanced_data['speeds'].mean():.2f} km/h")
    st.write("**Prędkość w 10s**")
    st.write(f"{average_speed_top_10_seconds:.2f} km/h")
with col2:
    st.write("**Maksymalna wysokość**")
    st.write(f"{enhanced_data['ele'].max():.2f} m n.p.m.")
    st.write("**Maksymalna prędkość**")
    st.write(f"{enhanced_data['speeds'].max():.2f} km/h")
    st.write("**Prędkość w 30s**")
    st.write(f"{average_speed_top_30_seconds:.2f} km/h")
with col3:
    st.write("**Wysokość końca**")
    st.write(f"{enhanced_data['ele'].iloc[-1]:.2f} m n.p.m.")

# Wykres 3D trasy
st.subheader('Wykres 3D trasy')
fig = go.Figure()
fig.add_trace(go.Scatter3d(x=enhanced_data['lon'], y=enhanced_data['lat'], z=enhanced_data['ele'],
                           mode='lines+markers',
                           line=dict(color='darkred', width=2),
                           marker=dict(size=2)))
fig.update_layout(scene=dict(
    xaxis_title="Długość geograficzna",
    yaxis_title="Szerokość geograficzna",
    zaxis_title="Wysokość n.p.m."
))

st.plotly_chart(fig)
# start_elevation = enhanced_data['ele'].iloc[0]
# max_elevation = enhanced_data['ele'].max()
# end_elevation = enhanced_data['ele'].iloc[-1]
# average_speed = enhanced_data['speeds'].mean()
# Wykres radarowy
total_distance = enhanced_data['distances'].sum()
minimal_elevation = enhanced_data['ele'].min()
average_elevation = enhanced_data['ele'].mean()


labels = ['Maksymalna prędkość', 'Średnia prędkość', 'Min. wysokość', 'Maks. wysokość', 'Średnia wysokość', 'Całkowita odległość']
stats = [max_speed, average_speed, minimal_elevation, max_elevation, average_elevation, total_distance]

# Normalizacja danych
max_values = [150, 50, 800, 1500, 2000, 6]  # Przykładowe wartości maksymalne dla normalizacji
normalized_stats = [s/m for s, m in zip(stats, max_values)]
st.subheader('Wykres radarowy')
fig = px.line_polar(r=normalized_stats, theta=labels, line_close=True)
fig.update_traces(fill='toself')
st.plotly_chart(fig)

# Boxplot prędkości
st.subheader('Rozkład prędkości')
fig = px.box(y=enhanced_data['speeds'], title="Rozkład prędkości", labels={"y": "Prędkość (km/h)"})
st.plotly_chart(fig)

# Wizualizacja nachylenia
st.subheader('Zmiany nachylenia w czasie')
fig = px.line(x=enhanced_data['time'], y=enhanced_data['gradients'], title="Zmiany nachylenia w czasie", labels={"x": "Czas", "y": "Nachylenie (%)"})
st.plotly_chart(fig)

# Kumulacyjny spadek wysokości
st.subheader('Kumulacyjny spadek wysokości')
fig = px.line(x=enhanced_data['time'], y=enhanced_data['cumulative_elevation_drop'], title="Kumulacyjny spadek wysokości w czasie", labels={"x": "Czas", "y": "Kumulacyjny spadek wysokości (m)"})
st.plotly_chart(fig)

# Mapa trasy z uwzględnieniem prędkości
st.subheader('Mapa trasy z uwzględnieniem prędkości')
fig = px.scatter_mapbox(enhanced_data, lat='lat', lon='lon', color='speeds',
                        size='speeds', hover_data=['ele', 'time'],
                        color_continuous_scale=px.colors.sequential.Viridis, 
                        size_max=15, zoom=14)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig)

fig_gradient = px.scatter_mapbox(enhanced_data, lat='lat', lon='lon', color='gradients',
                                 size=abs(enhanced_data['gradients']), hover_data=['ele', 'time', 'speeds'],
                                 color_continuous_scale=px.colors.sequential.RdBu_r, 
                                 size_max=10, zoom=14,
                                 labels={"gradients": "Nachylenie (%)", "ele": "Wysokość (m n.p.m.)", "time": "Czas", "speeds": "Prędkość (km/h)"},
                                 title="Mapa trasy z uwzględnieniem nachylenia")

fig_gradient.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_gradient)

fig_heatmap = px.density_mapbox(enhanced_data, lat='lat', lon='lon', z='gradients',
                                radius=10, zoom=14,
                                color_continuous_scale=px.colors.sequential.RdBu_r, 
                                labels={"gradients": "Nachylenie (%)"},
                                title="Heatmapa trasy z uwzględnieniem nachylenia")
fig_heatmap.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_heatmap)





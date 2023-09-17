# flask_server.py
import sys
sys.path.append('../solution/tools')
from flask import Flask, jsonify
import plotly.graph_objs as go
import json
from tools.data_processing import haversine, enhance_dataframe
from tools.data_loader import get_data_from_url, parse_gpx_to_dataframe, parse_gpx_file
from flask import Flask, request, jsonify
import plotly.graph_objs as go
import json
import pandas as pd
import plotly.express as px

# app = Flask(__name__)

# @app.route('/get_plot')
# def get_plot():
#     # Tworzenie przykładowego wykresu
#     fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
#     fig_json = json.loads(fig.to_json())

#     return jsonify(fig_json)


# @app.route('/get_data')
# def get_data():
#     df = load_data()
#     df = enhance_dataframe(df)




app = Flask(__name__)


@app.route('/load_data', methods=['POST'])
def load_data():
    data = request.json
    url = data['url']
    df = get_data_from_url(url)
    df = enhance_dataframe(df)
    # przekonwertuj df na json i zwróć dane w json
    # print(df)
    df_json = df.to_json(orient='split')
    return df_json

@app.route('/get_enhanced_df', methods=['POST'])
def get_enhanced_df():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    df = enhance_dataframe(df)
    df_json = df.to_json(orient='split')
    return df_json


@app.route('/transform_gpx_data', methods=['POST'])
def transform_gpx_data():
    data = request.json
    df = parse_gpx_file(data['route_data'])
    # print(df)
    df = enhance_dataframe(df)
    df_json = df.to_json(orient='split')
    return df_json
    
    # przekonwertuj df na json i zwróć dane w json
    # print(df)
    # df_json = df.to_json(orient='split')
    # return df_json
    pass


@app.route('/get_basic_stats', methods=['POST'])
def get_basic_stats():
    #read json to dataframe
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    #calculate basic stats

    start_elevation = df['ele'].iloc[0]
    max_elevation = df['ele'].max()
    end_elevation = df['ele'].iloc[-1]
    average_speed = round(df['speeds'].mean(), 2)
    max_speed = round(df['speeds'].max(),2)
    df['time_diff'] = (pd.to_datetime(df['time']) - pd.to_datetime(df['time'].shift(1))).dt.total_seconds()
    top_10_seconds_speeds = df.sort_values(by='speeds', ascending=False).head(int(10/df['time_diff'].mean()))['speeds']
    average_speed_top_10_seconds = round(top_10_seconds_speeds.mean(), 2)

    # Ponowne obliczenie średniej prędkości w najszybszych 30 sekundach
    top_30_seconds_speeds = df.sort_values(by='speeds', ascending=False).head(int(30/df['time_diff'].mean()))['speeds']
    average_speed_top_30_seconds = round(top_30_seconds_speeds.mean(), 2)
    average_descent_segmented = round(df['gradients'].mean(), 2)
    max_descent = round(df['gradients'].max(), 2)
    response = {
        "start_elevation": start_elevation,
        "max_elevation": max_elevation,
        "end_elevation": end_elevation,
        "average_speed": average_speed,
        "max_speed": max_speed,
        "average_speed_top_10_seconds": average_speed_top_10_seconds,
        "average_speed_top_30_seconds": average_speed_top_30_seconds,
        "average_descent_segmented": average_descent_segmented,
        "max_descent": max_descent
    }
    print(response)
    return jsonify(response)

# @app.route('/send_data', methods=['POST'])
# def send_data():
#     # Odbieranie danych w formacie JSON i konwersja na DataFrame
#     data_json = json.loads(request.data)
#     df = pd.read_json(data_json, orient='split')
    
#     # Tutaj możesz przetworzyć DataFrame, zanim wygenerujesz wizualizację
#     print(df)
    
#     # Tworzenie przykładowego wykresu na podstawie przesłanego DataFrame
#     fig = go.Figure(data=go.Bar(y=df['A']))
#     fig_json = json.loads(fig.to_json())

#     return jsonify(fig_json)
@app.route('/get_3d_plot', methods=['POST'])
def get_3d_plot():

    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    enhanced_data = df
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=enhanced_data['lon'], y=enhanced_data['lat'], z=enhanced_data['ele'],
                            mode='lines+markers',
                            line=dict(color='darkred', width=2),
                            marker=dict(size=2)))
    fig.update_layout(scene=dict(
        xaxis_title="Długość geograficzna",
        yaxis_title="Szerokość geograficzna",
        zaxis_title="Wysokość n.p.m."))
    fig_json = json.loads(fig.to_json())
    return jsonify(fig_json)


@app.route('/get_map_speed_gradient', methods=['POST'])
def get_map_speed_gradient():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    
    enhanced_data = df
    fig = px.scatter_mapbox(enhanced_data, lat='lat', lon='lon', color='speeds',
                        size='speeds', hover_data=['ele', 'time'],
                        color_continuous_scale=px.colors.sequential.Viridis, 
                        size_max=15, zoom=14)
    fig.update_layout(mapbox_style="open-street-map")

    fig_json = json.loads(fig.to_json())
    return jsonify(fig_json)


@app.route('/get_map_descent_gradient', methods=['POST'])
def get_map_descent_gradient():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    enhanced_data = df
    fig_gradient = px.scatter_mapbox(enhanced_data, lat='lat', lon='lon', color='gradients',
                                 size=abs(enhanced_data['gradients']), hover_data=['ele', 'time', 'speeds'],
                                 color_continuous_scale=px.colors.sequential.RdBu_r, 
                                 size_max=10, zoom=14,
                                 labels={"gradients": "Nachylenie (%)", "ele": "Wysokość (m n.p.m.)", "time": "Czas", "speeds": "Prędkość (km/h)"},
                                 title="Mapa trasy z uwzględnieniem nachylenia")

    fig_gradient.update_layout(mapbox_style="open-street-map")
    fig_json = json.loads(fig_gradient.to_json())
    return jsonify(fig_json)


@app.route('/get_map_descent_heatmap', methods=['POST'])
def get_map_descent_heatmap():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    enhanced_data = df
    fig_heatmap = px.density_mapbox(enhanced_data, lat='lat', lon='lon', z='gradients',
                                radius=10, zoom=14,
                                color_continuous_scale=px.colors.sequential.RdBu_r, 
                                labels={"gradients": "Nachylenie (%)"},
                                title="Heatmapa trasy z uwzględnieniem nachylenia")
    fig_heatmap.update_layout(mapbox_style="open-street-map")
    fig_json = json.loads(fig_heatmap.to_json())
    return jsonify(fig_json)

@app.route('/get_map_speed_heatmap', methods=['POST'])
def get_map_speed_heatmap():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    data = df

    fig = go.Figure()

    # Dodanie mapy cieplnej
    # Dodanie mapy cieplnej
    fig.add_trace(go.Densitymapbox(lat=data['lat'], lon=data['lon'], colorscale="Blues", radius=8))


    # Dodanie trasy
    fig.add_trace(go.Scattermapbox(lat=data['lat'], lon=data['lon'], mode='lines+markers', marker=dict(size=4, color='red')))

    # Aktualizacja układu mapy
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center_lon=data['lon'].mean(),
        mapbox_center_lat=data['lat'].mean(),
        mapbox_zoom=14,
        title="Mapa cieplna trasy z wizualizacją trasy"
    )
    fig_json = json.loads(fig.to_json())

    return jsonify(fig_json)

@app.route('/get_radar_plot', methods=['POST'])
def get_radar_plot():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    enhanced_data = df
    start_elevation = enhanced_data['ele'].iloc[0]
    max_elevation = enhanced_data['ele'].max()
    end_elevation = enhanced_data['ele'].iloc[-1]
    average_speed = enhanced_data['speeds'].mean()
    max_speed = enhanced_data['speeds'].max()
    total_distance = enhanced_data['distances'].sum()
    minimal_elevation = enhanced_data['ele'].min()
    average_elevation = enhanced_data['ele'].mean()

    labels = ['Maksymalna prędkość', 'Średnia prędkość', 'Min. wysokość', 'Maks. wysokość', 'Średnia wysokość', 'Całkowita odległość']
    stats = [max_speed, average_speed, minimal_elevation, max_elevation, average_elevation, total_distance]
    
    max_values = [150, 50, 800, 1500, 2000, 6]  # Przykładowe wartości maksymalne dla normalizacji
    normalized_stats = [s/m for s, m in zip(stats, max_values)]

    fig = px.line_polar(r=normalized_stats, theta=labels, line_close=True)
    fig.update_traces(fill='toself')
    fig_json = json.loads(fig.to_json())
    return jsonify(fig_json)


# @app.route('/get_map_speed_heatmap', methods=['POST'])
# def get_map_speed_heatmap():
#     pass
# 

@app.route('/get_cummulative_descent', methods=['POST'])
def get_cummulative_descent():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    enhanced_data = df
    fig = px.line(x=enhanced_data['time'], y=enhanced_data['cumulative_elevation_drop'], title="Kumulacyjny spadek wysokości w czasie", labels={"x": "Czas", "y": "Kumulacyjny spadek wysokości (m)"})
    fig_json = json.loads(fig.to_json())
    return jsonify(fig_json)


@app.route('/speed_box_plot', methods=['POST'])
def get_speed_box_plot():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    enhanced_data = df
    fig = px.box(y=enhanced_data['speeds'], title="Rozkład prędkości", labels={"y": "Prędkość (km/h)"})
    fig_json = json.loads(fig.to_json())
    return jsonify(fig_json)


@app.route('/get_descent_change_plot', methods=['POST'])
def get_descent_change_plot():
    data_json = json.loads(request.data)
    df = pd.read_json(data_json, orient='split')
    enhanced_data = df
    fig = px.line(x=enhanced_data['time'], y=enhanced_data['gradients'], title="Zmiany nachylenia w czasie", labels={"x": "Czas", "y": "Nachylenie (%)"})
    fig_json = json.loads(fig.to_json())
    return jsonify(fig_json)



if __name__ == "__main__":
    app.run(port=5000)


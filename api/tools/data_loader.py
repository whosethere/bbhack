import pandas as pd
import xml.etree.ElementTree as ET
import pandas as pd
import requests


def parse_gpx_file(str):

    root = ET.fromstring(str)
    
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

def parse_gpx_to_dataframe(gpx_url):
    """
        gpx_url = 'https://endurotrails.pl/static/upload/store/pliki_gpx/stary-zielony.gpx'  # Zmień na właściwy URL
        df = parse_gpx_to_dataframe(gpx_url)
    """
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

# Przykład użycia funkcji:
def get_data_from_url(url):
    df = parse_gpx_to_dataframe(url)
    return df

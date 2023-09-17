import xml.etree.ElementTree as ET
import pandas as pd
import math

def haversine(lon1, lat1, lon2, lat2):
    """
    Oblicza odległość w kilometrach między dwoma punktami na powierzchni Ziemi, określonymi przez współrzędne geograficzne.
    """
    # Stała - promień Ziemi w km
    R = 6371.0

    # Konwersja stopni na radiany
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Obliczenia
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

def enhance_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Obliczenie odległości między punktami
    distances = [haversine(df['lon'][i-1], df['lat'][i-1], df['lon'][i], df['lat'][i]) for i in range(1, len(df))]
    distances = [0] + distances
    df['distances'] = distances
    
    # Obliczenie prędkości
    df['time_diff'] = (pd.to_datetime(df['time']) - pd.to_datetime(df['time'].shift(1))).dt.total_seconds()
    df['speeds'] = df['distances'] / df['time_diff'] * 3600  # Przeliczenie na km/h
    
    # Obliczenie nachylenia
    df['elevation_diff'] = df['ele'].diff()
    df['gradients'] = 100 * df['elevation_diff'] / (df['distances'] * 1000)  # Nachylenie w procentach
    df['gradients'].fillna(0, inplace=True)
    
    # Obliczenie kumulacyjnego spadku wysokości
    df['elevation_drops'] = df['elevation_diff'].apply(lambda x: max(-x, 0))
    df['cumulative_elevation_drop'] = df['elevation_drops'].cumsum()
    
    # Usunięcie kolumn pomocniczych
    df.drop(columns=['time_diff', 'elevation_diff', 'elevation_drops'], inplace=True)
    df.fillna(0, inplace=True)
    return df
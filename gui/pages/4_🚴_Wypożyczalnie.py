import streamlit as st
import pandas as pd
import numpy as np

# st.title('Uber pickups in NYC')

# DATE_COLUMN = 'date/time'
# DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
#             'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

# @st.cache_data
# def load_data(nrows):
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     lowercase = lambda x: str(x).lower()
#     data.rename(lowercase, axis='columns', inplace=True)
#     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#     return data

# data_load_state = st.text('Loading data...')
# data = load_data(10000)
# data_load_state.text("Done! (using st.cache_data)")

# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     st.write(data)

# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
# # 49.794630, 19.038309
punkt = {
    'LAT': 49.779325,
    'LON': 19.055309
}

# Tworzenie DataFrame z punktem
df = pd.DataFrame([punkt], columns=["LAT", "LON"])

# Wyświetlenie punktu na mapie

st.subheader('Wypożycz rower w enduro trails')
st.map(df)

st.subheader('Rowery do wypożyczenia:')
col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Rower 1**")
    st.write(f"Opis roweru")
    st.write("**Rower 2**")
    st.write(f"Opis roweru")
with col2:
    st.write("**Rower 3**")
    st.write(f"Opis roweru")
    st.write("**Rower 4**")
    st.write(f"Opis roweru")
with col3:
    st.write("**Rower 5**")
    st.write(f"Opis roweru")
    st.write("**Rower 6**")
    st.write(f"Opis roweru")
    
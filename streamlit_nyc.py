import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


DATA_URL = (
    "E:/VS Code/Web app using Streamlit/streamlit-nyc/dataset/Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used "
            "to analyze motor vehicle collisions in NYC 🚗")

# load data
@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

    def lowercase(x):
        return str(x).lower()

    data.rename(lowercase, axis="columns", inplace=True)
    data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True)
    return data


data = load_data(100000)

# visualize data on map
st.header("Most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)  # max num of injured people who are a total of 19 at the spot
st.map(data.query("injured_persons >= @injured_people")
       [["latitude", "longitude"]].dropna(how="any"))

# filtering data
st.header("Collisions occur during a given time of day")
hour = st.slider("Hour to look at", 0, 23)
original_data = data
data = data[data['date/time'].dt.hour == hour]

# visualize data using charts and histograms
st.subheader("Breakdown by minute between %i:00 and %i:00" %(hour, (hour + 1) % 24))
filtered = data[(data['date/time'].dt.hour >= hour) &
                (data['date/time'].dt.hour < (hour + 1))]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x='minute', y='crashes',
             hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 10 dangerous streets by affected class")
select = st.selectbox('Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(
        by=['injured_pedestrians'], ascending=False).dropna(how="any")[:10])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(
        by=['injured_cyclists'], ascending=False).dropna(how="any")[:10])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(
        by=['injured_motorists'], ascending=False).dropna(how="any")[:10])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)

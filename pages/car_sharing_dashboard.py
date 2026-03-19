import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    trips = pd.read_csv("dataset/trips.csv")
    cars = pd.read_csv("dataset/cars.csv")
    cities = pd.read_csv("dataset/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    trips = pd.read_csv("dataset/trips.csv")
    cars = pd.read_csv("dataset/cars.csv")
    cities = pd.read_csv("dataset/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

# Merge trips with cars
trips_merged = trips.merge(cars, left_on="car_id", right_on="id")

# Merge with cities
trips_merged = trips_merged.merge(cities, on="city_id")

# Drop useless columns
trips_merged = trips_merged.drop(columns=["id_x", "id_y", "city_id", "customer_id", "car_id"])

# Convert dates
trips_merged['pickup_date'] = pd.to_datetime(trips_merged['pickup_time']).dt.date

# Sidebar filter
cars_brand = st.sidebar.multiselect("Select the Car Brand", trips_merged["brand"].unique())
if cars_brand:
    trips_merged = trips_merged[trips_merged["brand"].isin(cars_brand)]

# Metrics
total_trips = len(trips_merged)
total_distance = trips_merged["distance"].sum()
top_car = trips_merged.groupby("model")["revenue"].sum().idxmax()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Trips", value=total_trips)
with col2:
    st.metric(label="Top Car Model by Revenue", value=top_car)
with col3:
    st.metric(label="Total Distance (km)", value=f"{total_distance:,.2f}")

st.write(trips_merged.head())

st.title("Car Sharing Dashboard")

# 1. Trips Over Time
st.subheader("Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size().reset_index(name="num_trips")
st.line_chart(trips_over_time.set_index("pickup_date"))

# 2. Revenue Per Car Model
st.subheader("Revenue Per Car Model")
revenue_per_model = trips_merged.groupby("model")["revenue"].sum()
st.bar_chart(revenue_per_model)

# 3. Number of Trips Per Car Model
st.subheader("Number of Trips Per Car Model")
trips_per_model = trips_merged.groupby("model").size()
st.bar_chart(trips_per_model)

# 4. Revenue by City
st.subheader("Revenue by City")
revenue_by_city = trips_merged.groupby("city_name")["revenue"].sum()
st.bar_chart(revenue_by_city)

# 5. Cumulative Revenue Growth Over Time
st.subheader("Cumulative Revenue Growth Over Time")
cumulative_revenue = trips_merged.groupby("pickup_date")["revenue"].sum().cumsum()
st.area_chart(cumulative_revenue)
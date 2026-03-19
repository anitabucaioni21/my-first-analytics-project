import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    trips = pd.read_csv("dataset/trips.csv")
    cars = pd.read_csv("dataset/cars.csv")
    cities = pd.read_csv("dataset/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

trips_merged = trips.merge(cars, left_on="car_id", right_on="id", suffixes=("_trip", "_car"))
trips_merged = trips_merged.merge(cities, on="city_id")
trips_merged = trips_merged.drop(columns=["id_trip", "id_car", "car_id", "city_id"], errors="ignore")
trips_merged['pickup_date'] = pd.to_datetime(trips_merged['pickup_time']).dt.date

cars_brand = st.sidebar.multiselect("Select the Car Brand", trips_merged["brand"].unique(), key="brand_filter")
if cars_brand:
    trips_merged = trips_merged[trips_merged["brand"].isin(cars_brand)]

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

st.subheader("Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size().reset_index(name="num_trips")
st.line_chart(trips_over_time.set_index("pickup_date"))

st.subheader("Revenue Per Car Model")
st.bar_chart(trips_merged.groupby("model")["revenue"].sum())

st.subheader("Number of Trips Per Car Model")
st.bar_chart(trips_merged.groupby("model").size())

st.subheader("Revenue by City")
st.bar_chart(trips_merged.groupby("city_name")["revenue"].sum())

st.subheader("Cumulative Revenue Growth Over Time")
st.area_chart(trips_merged.groupby("pickup_date")["revenue"].sum().cumsum())

st.subheader("Average Trip Duration by City")
trips_merged['duration_min'] = (
    pd.to_datetime(trips_merged['dropoff_time']) - 
    pd.to_datetime(trips_merged['pickup_time'])
).dt.total_seconds() / 60
st.bar_chart(trips_merged.groupby("city_name")["duration_min"].mean())

st.subheader("Revenue by Car Brand")
st.bar_chart(trips_merged.groupby("brand")["revenue"].sum())

st.subheader("Distance Distribution by Model")
st.bar_chart(trips_merged.groupby("model")["distance"].mean())

st.subheader("Top 10 Customers by Revenue")
st.bar_chart(trips_merged.groupby("customer_id")["revenue"].sum().nlargest(10))

st.subheader("Average Daily Revenue Over Time")
st.area_chart(trips_merged.groupby("pickup_date")["revenue"].mean())

st.subheader("Trips by Day of Week")
trips_merged['day_of_week'] = pd.to_datetime(trips_merged['pickup_time']).dt.day_name()
trips_by_day = trips_merged.groupby("day_of_week").size().reindex(
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
)
st.bar_chart(trips_by_day)

st.subheader("Revenue per KM by Car Model")
trips_merged['revenue_per_km'] = trips_merged['revenue'] / trips_merged['distance']
st.bar_chart(trips_merged.groupby("model")["revenue_per_km"].mean())

st.subheader("Revenue Share by Car Brand")
revenue_brand = trips_merged.groupby("brand")["revenue"].sum().reset_index()
fig1 = px.pie(revenue_brand, values="revenue", names="brand", title="Revenue Share by Brand")
st.plotly_chart(fig1)

st.subheader("Trips Share by City")
trips_city = trips_merged.groupby("city_name").size().reset_index(name="num_trips")
fig2 = px.pie(trips_city, values="num_trips", names="city_name", title="Trips Share by City")
st.plotly_chart(fig2)

st.subheader("Revenue Share by Car Model")
revenue_model = trips_merged.groupby("model")["revenue"].sum().reset_index()
fig3 = px.pie(revenue_model, values="revenue", names="model", title="Revenue Share by Model")
st.plotly_chart(fig3)


city_filter = st.sidebar.multiselect("Select the City", trips_merged["city_name"].unique(), key="city_filter")
if city_filter:
    trips_merged = trips_merged[trips_merged["city_name"].isin(city_filter)]


trips_merged['year_trip'] = pd.to_datetime(trips_merged['pickup_time']).dt.year
year_filter = st.sidebar.multiselect("Select the Year", sorted(trips_merged["year_trip"].unique()), key="year_filter")
if year_filter:
    trips_merged = trips_merged[trips_merged["year_trip"].isin(year_filter)]

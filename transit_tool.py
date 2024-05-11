import pandas as pd
import plotly.express as px
import streamlit as st
import os
from dotenv import load_dotenv
import requests
import requests_cache
import datetime

# Load .env variables
load_dotenv()

# Populate the Bing API KEY
BING_MAPS_API_KEY = os.getenv("BING_MAPS_API_KEY", st.secrets["BING_MAPS_API_KEY"])

BASE_QUERY_URI = f"http://dev.virtualearth.net/REST/v1/Locations?&key={BING_MAPS_API_KEY}&maxResults=3&userLocation=43.65,-79.38&query="
requests_cache.install_cache("places_api_cache", expire_after=3600 * 24 * 365)

# Streamlit Config and Headers
st.set_page_config(
    page_title="Transit Data Visualization Tool", page_icon="🚆'",
)

st.title("Transit Data Visualization Tool 🚆")
st.write(
    """

----

"""
)

@st.cache_data
def stop_to_coordinate(df):
    coordinate_array = []
    df_locations = df["Location"].squeeze()

    for location in df_locations.values:
        try:
            url = f"{BASE_QUERY_URI}{location}"
            data = requests.get(url).json()

            num_results = data["resourceSets"][0]["estimatedTotal"]
            resources = data["resourceSets"][0]["resources"]

            for resource in resources:
                province = resource["address"]["adminDistrict"]
                country = resource["address"]["countryRegion"]
                location_type = resource["entityType"]
                faulty_types = ["PopulatedPlace", "AdminDivision2", "Neighborhood"]

                if province != "ON" or country != "Canada" or location_type in faulty_types:
                    continue

                latitude_longitude = (
                    resource["point"]["coordinates"][0],
                    resource["point"]["coordinates"][1],
                )

                coordinate_array.append(latitude_longitude)
                break

        except Exception as e:
            pass

    coordinate_df = pd.DataFrame(coordinate_array, columns=["latitude", "longitude"])
    st.map(coordinate_df, size=40)

@st.cache_data
def clean_raw_data(df):
    df = df[["Date", "Location", "Amount", "Transit Agency"]]
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y %I:%M:%S %p")
    df = df.replace(
        {
            "Zone17": "Aldershot GO",
            "Zone20": "Square One",
            "Zone27": "University of Waterloo",
        }
    )
    return df

@st.cache_data
def map_frequent_stops(df):
    location_counts = df["Location"].value_counts().nlargest(7)
    fig = px.bar(location_counts)
    fig.update_layout(xaxis_title="Location", yaxis_title="Count", showlegend=False)
    number_unique_stops = len(df["Location"].unique())
    return fig, number_unique_stops

@st.cache_data
def get_spendings_data(df):
    df["Amount"] = df["Amount"].str.replace("-", "").str.replace("$", "").astype(float)
    df["Date"] = pd.to_datetime(df["Date"])
    df.Date = df.Date - pd.DateOffset(months=1)
    out = df.set_index("Date").groupby(pd.Grouper(freq="M"))["Amount"].sum()
    num_amount_spent = df["Amount"].sum()
    return out, num_amount_spent

@st.cache_data
def get_tap_data(df):
    df["Date"] = pd.to_datetime(df["Date"])
    unique_days_travelled = df["Date"].dt.date.nunique()
    df = df.groupby(pd.Grouper(key="Date", freq="M"))["Amount"].count()
    fig2 = px.bar(df)
    return fig2, unique_days_travelled

st.write("Enter your exported Metrolinx transit data 📖")

try:
    uploaded_csv = st.file_uploader("CSV file:", type="csv")

    if not uploaded_csv:
        uploaded_csv = "transit_usage.csv"

    df = pd.read_csv(uploaded_csv)
    df = clean_raw_data(df)

    st.markdown("---")

    fig, number_unique_stops = map_frequent_stops(df)
    st.plotly_chart(fig)
    st.write("Woah! You have visited ", number_unique_stops, " different stops!")

    stop_to_coordinate(df)

    st.markdown("---")

    out, num_amount_spent = get_spendings_data(df)
    amountFig = px.bar(out)
    st.subheader("💸 Monthly Transit Spendings")
    amountFig.update_layout(
        xaxis_title="Month", yaxis_title="Amount Spent ($)", showlegend=False
    )
    st.plotly_chart(amountFig)

    current_year = datetime.date.today().year 
    data_year = df.loc[0, "Date"].year + 1

    if current_year != data_year:
        st.write("💸 Amount spent in ", data_year, ": $", round(num_amount_spent, 2))
    elif current_year == data_year:
        st.write(
            "💸 Amount spent so far in ", current_year, ": $", round(num_amount_spent, 2)
        )

    st.markdown("---")

    fig2, unique_days_travelled = get_tap_data(df)
    st.subheader("📊 Tap On/Off Frequency")
    fig2.update_layout(xaxis_title="Month", yaxis_title="Count", showlegend=False)
    st.plotly_chart(fig2)
    st.write("You took Metrolinx on", unique_days_travelled, " days! Keep it going!")

    st.subheader("📊 Amount Spent per Transit Agency")
    df["Amount"] = df["Amount"].str.replace("-", "").str.replace("$", "").astype(float)
    df3 = df.groupby("Transit Agency")["Amount"].agg("sum")
    agencyFig = px.bar(df3)
    agencyFig.update_layout(
        xaxis_title="Transit Agency", yaxis_title="Amount ($)", showlegend=False
    )
    st.plotly_chart(agencyFig)

except Exception as e:
    st.error(f"An error occurred: {e}")
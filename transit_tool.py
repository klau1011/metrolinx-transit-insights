import pandas as pd
import plotly.express as px
import streamlit as st
import os
from dotenv import load_dotenv, dotenv_values
import requests
import requests_cache

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
BASE_QUERY_URI = f'https://maps.googleapis.com/maps/api/place/textsearch/json?key={GOOGLE_API_KEY}&query='
requests_cache.install_cache('places_api_cache', expire_after=3600*24*365)  

st.set_page_config(
    page_title="Transit Data Visualization Tool",
    page_icon="🚆'",

)

st.title('Transit Data Visualization Tool 🚆')
st.write("""

----

""")

@st.cache_data
def stop_to_coordinate(df):
    coordinate_array = []
    df_locations = df[['Location']]
    df_locations = df_locations.replace({'Zone20': 'Square One', 'Zone27': "University of Waterloo"})
    df_locations = df_locations.squeeze()
    
    for index, location in enumerate(df_locations.values):
        url = f'{BASE_QUERY_URI}{location}'
        data = requests.get(url).json()

        coordinates = data["results"][0]["geometry"]["location"]
        latitude_longitude = (coordinates['lat'], coordinates['lng'])


st.write("Enter your exported Metrolinx transit data 📖")

try: 
    uploaded_csv = st.file_uploader("Input your CSV file:", type="csv")

    if not uploaded_csv:
        uploaded_csv = 'transit_usage.csv'

    # Get relevant columns
    df = pd.read_csv(uploaded_csv)
    df = df[['Date', 'Location', 'Amount']]
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p')

    # -- MOST FREQ STOPS ------

    # get the most 10 popular stops
    location_counts = df['Location'].value_counts().nlargest(10)

    # plot locations
    fig = px.bar(location_counts)

    # add axis titles
    st.subheader('Most frequent stops 📊')
    fig.update_layout(xaxis_title="Location", yaxis_title="Count", showlegend=False)

    # output graph to show most freq stops
    st.plotly_chart(fig)


    # MONTHLY TRANSIT SPENDINGS -------
    df2 = df
    df2['Amount'] = df['Amount'].astype(str)
    df2['Amount'] = df2['Amount'].str.replace('-', '')
    df2['Amount'] = df2['Amount'].str.replace('$', '')
    df2['Amount'] = df2['Amount'].astype(float)

    # # date time format
    df2['Date'] = pd.to_datetime(df2['Date'])

    # offset by 1 mo to display correct months
    df2.Date = df2.Date - pd.DateOffset(months=1)

    # group by and sum each month
    out = df2.set_index('Date').groupby(pd.Grouper(freq='M'))['Amount'].sum()

    # output graph 
    amountFig = px.bar(out)
    st.subheader('Monthly Transit Spendings')
    amountFig.update_layout(xaxis_title="Month", yaxis_title="Amount Spent ($)", showlegend=False)

    # output graph to show spendings per month
    st.plotly_chart(amountFig)



    # TAP ON/OFF COUNT PER MONTH  -----------
    df3 = df

    df3['Date'] = pd.to_datetime(df3['Date'])

    df3 = df3.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].count()

    fig2 = px.bar(df3)
    st.subheader('Tap On/Off Frequency')
    fig2.update_layout(xaxis_title="Month", yaxis_title="Count", showlegend=False)

    # output graph to shows taps per months
    st.plotly_chart(fig2)

    stop_to_coordinate(df2)
except: 
    pass





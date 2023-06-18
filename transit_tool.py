import pandas as pd
import plotly.express as px
import streamlit as st

st.title('Transit Data Visualization Tool')
st.write("""

----

""")


st.write("Enter your exported Metrolinx transit data to recieve your own summaries")

try: 
    uploaded_csv = st.file_uploader("Input your CSV file:", type="csv")

    if not uploaded_csv:
        uploaded_csv = 'transit_usage.csv'

    df = pd.read_csv(uploaded_csv)
    df = df[['Date', 'Location', 'Amount']]
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p')

    # -- MOST FREQ STOPS --

    # get the most 10 popular stops
    location_counts = df['Location'].value_counts().nlargest(10)

    # plot locations
    fig = px.bar(location_counts)

    # add axis titles
    st.subheader('Most frequent stops')
    fig.update_layout(xaxis_title="Location", yaxis_title="Count", showlegend=False)

    # output graph to show most freq stops
    st.plotly_chart(fig)

    # MONTHLY TRANSIT SPENDINGS 
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


    # TAP ON/OFF COUNT PER MONTH 
    df3 = df

    df3['Date'] = pd.to_datetime(df3['Date'])

    df3 = df3.groupby(pd.Grouper(key='Date', freq='M'))['Amount'].count()

    fig2 = px.bar(df3)
    st.subheader('Tap On/Off Frequency')
    fig2.update_layout(xaxis_title="Month", yaxis_title="Count", showlegend=False)

    # output graph to shows taps per months
    st.plotly_chart(fig2)

except: 
    pass

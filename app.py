import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 1. Database Connection
engine = create_engine("mysql+pymysql://root:12345@localhost/phonepe_db")

st.set_page_config(page_title="PhonePe Pulse Data Visualization", layout="wide")
st.title("📱 PhonePe Pulse Insights")

# 2. Sidebar for Filters
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022, 2023, 2024])

# 3. Query Data from SQL
query = f"SELECT State, SUM(Transaction_Amount) as Total_Amount FROM aggregated_transaction WHERE Year = {year} GROUP BY State"
df = pd.read_sql(query, engine)

# 4. Visualization
st.subheader(f"Total Transaction Amount by State in {year}")
fig = px.bar(df, x="State", y="Total_Amount", color="Total_Amount", color_continuous_scale="Viridis")
st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="PhonePe Pulse Dashboard", layout="wide")
st.title("📊 PhonePe Pulse Data Visualization")

# --- LOAD DATA ---
@st.cache_data # This makes your app much faster
def load_data():
    df = pd.read_csv("phonepe_transactions.csv")
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Options")
selected_year = st.sidebar.selectbox("Select Year", sorted(df['Year'].unique()))
selected_quarter = st.sidebar.selectbox("Select Quarter", sorted(df['Quarter'].unique()))

# --- FILTER DATA ---
filtered_df = df[(df['Year'] == selected_year) & (df['Quarter'] == selected_quarter)]

# --- VISUALIZATION 1: TOTAL TRANSACTIONS BY STATE ---
st.subheader(f"Transaction Analysis for {selected_year} - Q{selected_quarter}")

state_data = filtered_df.groupby("State")["Transaction_Amount"].sum().reset_index()

fig_state = px.bar(
    state_data, 
    x="State", 
    y="Transaction_Amount",
    title="Total Transaction Amount per State",
    color="Transaction_Amount",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig_state, use_container_width=True)

# --- VISUALIZATION 2: TRANSACTION TYPE BREAKDOWN ---
type_data = filtered_df.groupby("Transaction_Type")["Transaction_Count"].sum().reset_index()

fig_pie = px.pie(
    type_data, 
    values="Transaction_Count", 
    names="Transaction_Type", 
    title="Breakdown of Transaction Types",
    hole=0.4
)
st.subheader("Transaction Categories")
st.plotly_chart(fig_pie, use_container_width=True)

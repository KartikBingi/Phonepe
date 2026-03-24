import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PhonePe Pulse PRO", layout="wide", page_icon="📈")

# FIXED: Changed 'unsafe_allow_value' to 'unsafe_allow_html'
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #6e42ff; }
    .stMetric { 
        background-color: #1e2130; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #3e4259;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADERS ---
@st.cache_data
def load_and_clean_data():
    try:
        t_df = pd.read_csv("phonepe_transactions.csv")
        u_df = pd.read_csv("phonepe_users.csv")
        m_df = pd.read_csv("map_transactions.csv")
        
        # Clean state names for the Map (e.g., 'andaman-&-nicobar' -> 'Andaman & Nicobar')
        for df in [t_df, u_df, m_df]:
            df['State'] = df['State'].str.replace('-', ' ').str.title()
            df['State'] = df['State'].str.replace('Andaman & Nicobar Islands', 'Andaman & Nicobar')
        return t_df, u_df, m_df
    except FileNotFoundError:
        return None, None, None

t_df, u_df, m_df = load_and_clean_data()

if t_df is None:
    st.error("⚠️ CSV files not found in the repository. Please upload your CSVs to GitHub.")
    st.stop()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("📊 Control Panel")
    year = st.selectbox("Year", sorted(t_df['Year'].unique(), reverse=True))
    quarter = st.select_slider("Quarter", options=[1, 2, 3, 4])

# Filtered Data
f_trans = t_df[(t_df['Year'] == year) & (t_df['Quarter'] == quarter)]
f_map = m_df[(m_df['Year'] == year) & (m_df['Quarter'] == quarter)]

# --- 4. HEADER & METRICS ---
st.title("📱 PhonePe Pulse PRO Dashboard")
col1, col2, col3 = st.columns(3)

total_val = f_trans['Transaction_Amount'].sum()
total_cnt = f_trans['Transaction_Count'].sum()
reg_users = u_df[(u_df['Year'] == year) & (u_df['Quarter'] == quarter)]['Registered_Users'].sum()

col1.metric("Total Value", f"₹{total_val/1e7:.2f} Cr")
col2.metric("Total Transactions", f"{total_cnt/1e5:.2f} L")
col3.metric("Registered Users", f"{reg_users/1e5:.2f} L")

# --- 5. VISUALIZATIONS ---
st.markdown("---")
c1, c2 = st.columns([1.2, 0.8])

with c1:
    st.subheader("🗺️ India Heatmap")
    map_data = f_map.groupby("State")["Amount"].sum().reset_index()
    fig_map = px.choropleth(
        map_data,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9ad97d3121354efebd9e57e/raw/0ad293846248c1d3008a30ad47e440590f1a3229/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color='Amount',
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map, use_container_width=True)

with c2:
    st.subheader("📊 Transaction Type")
    type_data = f_trans.groupby("Transaction_Type")["Transaction_Amount"].sum().reset_index()
    fig_pie = px.pie(type_data, values='Transaction_Amount', names='Transaction_Type', hole=0.5)
    st.plotly_chart(fig_pie, use_container_width=True)

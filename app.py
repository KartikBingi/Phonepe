import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. PRO CONFIGURATION ---
st.set_page_config(page_title="PhonePe Pulse PRO", layout="wide", page_icon="📈")

# Custom CSS for a professional dark-themed dashboard
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

# --- 2. DATA LOADERS (Cached for performance) ---
@st.cache_data
def load_and_clean_data():
    # Load your 3 core CSVs
    t_df = pd.read_csv("phonepe_transactions.csv")
    u_df = pd.read_csv("phonepe_users.csv")
    m_df = pd.read_csv("map_transactions.csv")
    
    # Data Cleaning: Convert "andaman-&-nicobar" to "Andaman & Nicobar Islands"
    # This ensures the map GeoJSON recognizes the names correctly
    for df in [t_df, u_df, m_df]:
        df['State'] = df['State'].str.replace('-', ' ').str.title()
        df['State'] = df['State'].str.replace('Andaman & Nicobar Islands', 'Andaman & Nicobar')
        
    return t_df, u_df, m_df

try:
    trans_df, user_df, map_df = load_and_clean_data()
except FileNotFoundError:
    st.error("Error: CSV files not found. Ensure phonepe_transactions.csv, phonepe_users.csv, and map_transactions.csv are in your repo.")
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📊 Control Panel")
    year = st.selectbox("Select Year", sorted(trans_df['Year'].unique(), reverse=True))
    quarter = st.select_slider("Select Quarter", options=[1, 2, 3, 4])
    st.info("Filter data to see insights across India.")

# Global Filters
f_trans = trans_df[(trans_df['Year'] == year) & (trans_df['Quarter'] == quarter)]
f_map = map_df[(map_df['Year'] == year) & (map_df['Quarter'] == quarter)]

# --- 4. TOP ROW: DYNAMIC KPI METRICS ---
st.title("📱 PhonePe Pulse Analytics Dashboard")
st.caption(f"Visualizing Data for Financial Year {year} - Quarter {quarter}")

total_val = f_trans['Transaction_Amount'].sum()
total_count = f_trans['Transaction_Count'].sum()
# Calculate Transaction per User if registered users data exists
total_users = user_df[(user_df['Year'] == year) & (user_df['Quarter'] == quarter)]['Registered_Users'].sum()

m1, m2, m3 = st.columns(3)
m1.metric("Total Transaction Value", f"₹{total_val/1e7:.2f} Cr")
m2.metric("Total Transactions", f"{total_count/1e5:.2f} L")
m3.metric("Registered Users", f"{total_users/1e5:.2f} L")

st.markdown("---")

# --- 5. MIDDLE ROW: GEOGRAPHIC & CATEGORY ANALYSIS ---
col_left, col_right = st.columns([1.2, 0.8])

with col_left:
    st.subheader("🗺️ India Transaction Heatmap")
    # Mapping Data
    map_viz_data = f_map.groupby("State")["Amount"].sum().reset_index()
    
    fig_india = px.choropleth(
        map_viz_data,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9ad97d3121354efebd9e57e/raw/0ad293846248c1d3008a30ad47e440590f1a3229/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color='Amount',
        color_continuous_scale="Viridis",
        hover_name="State",
        template="plotly_dark"
    )
    fig_india.update_geos(fitbounds="locations", visible=False)
    fig_india.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
    st.plotly_chart(fig_india, use_container_width=True)

with col_right:
    st.subheader("📈 Transaction Type")
    type_data = f_trans.groupby("Transaction_Type")["Transaction_Amount"].sum().reset_index()
    fig_pie = px.pie(type_data, values='Transaction_Amount', names='Transaction_Type', 
                     hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
    fig_pie.update_layout(showlegend=False, height=450)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 6. BOTTOM ROW: TOP PERFORMERS ---
st.markdown("---")
st.subheader("🏆 Top 10 Performing States")
top_10_states = f_trans.groupby("State")["Transaction_Amount"].sum().sort_values(ascending=False).head(10).reset_index()

fig_top = px.bar(
    top_10_states, 
    x="Transaction_Amount", 
    y="State", 
    orientation='h',
    color="Transaction_Amount",
    color_continuous_scale="Blues",
    text_auto='.2s'
)
fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
st.plotly_chart(fig_top, use_container_width=True)

st.caption("Data processed from PhonePe Pulse Open Repo. Built by Kartik.")

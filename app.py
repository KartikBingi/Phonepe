import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. PRO CONFIGURATION ---
st.set_page_config(page_title="PhonePe Pulse PRO", layout="wide", page_icon="📈")

# Custom CSS for that "Premium" feel
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4259; }
    </style>
    """, unsafe_allow_value=True)

# --- 2. DATA LOADERS (Cached for speed) ---
@st.cache_data
def get_data():
    trans_df = pd.read_csv("phonepe_transactions.csv")
    user_df = pd.read_csv("phonepe_users.csv")
    map_df = pd.read_csv("map_transactions.csv") # Make sure this is in your repo!
    return trans_df, user_df, map_df

trans_df, user_df, map_df = get_data()

# --- 3. SIDEBAR (Clean & Organized) ---
with st.sidebar:
    st.image("https://www.phonepe.com/webstatic/8404/static/76798b68894988775267b2d56637313a/43110/phonepe-logo.png", width=200)
    st.title("Control Panel")
    year = st.selectbox("Select Financial Year", sorted(trans_df['Year'].unique(), reverse=True))
    quarter = st.slider("Select Quarter", 1, 4, 1)
    state = st.selectbox("Focus State", sorted(trans_df['State'].unique()))

# Filter data once to use everywhere
f_trans = trans_df[(trans_df['Year'] == year) & (trans_df['Quarter'] == quarter) & (trans_df['State'] == state)]
f_map = map_df[(map_df['Year'] == year) & (map_df['Quarter'] == quarter)]

# --- 4. TOP ROW: KPI METRICS ---
total_val = f_trans['Transaction_Amount'].sum()
total_count = f_trans['Transaction_Count'].sum()
avg_val = total_val / total_count if total_count > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Transaction Value", f"₹{total_val/1e7:.2f} Cr", delta="Regional Volume")
col2.metric("Total Transaction Count", f"{total_count/1e5:.2f} Lakh", delta="Active Users")
col3.metric("Avg. Ticket Size", f"₹{avg_val:.2f}", delta="Per User")

st.divider()

# --- 5. MAIN DASHBOARD LAYOUT ---
row1_col1, row1_col2 = st.columns([1.2, 0.8])

with row1_col1:
    st.subheader("🗺️ Geographic Distribution (India)")
    # Group map data by state for the India map
    india_map_data = f_map.groupby("State")["Amount"].sum().reset_index()
    
    fig_map = px.choropleth(
        india_map_data,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9ad97d3121354efebd9e57e/raw/0ad293846248c1d3008a30ad47e440590f1a3229/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color='Amount',
        color_continuous_scale="Plasma",
        hover_name="State"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

with row1_col2:
    st.subheader("📊 Transaction Type")
    fig_pie = px.sunburst(f_trans, path=['Transaction_Type'], values='Transaction_Amount',
                          color='Transaction_Amount', color_continuous_scale='RdBu')
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 6. SECOND ROW: ANALYSIS ---
st.subheader(f"📈 Top Districts in {state}")
dist_data = f_map[f_map['State'] == state].sort_values(by="Amount", ascending=False).head(10)
fig_dist = px.bar(dist_data, x="District", y="Amount", color="Amount", template="plotly_dark")
st.plotly_chart(fig_dist, use_container_width=True)

# --- 7. FOOTER ---
st.caption(f"Data source: PhonePe Pulse Open Data | Visualizing {state} for {year} Q{quarter}")

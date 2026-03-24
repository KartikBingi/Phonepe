import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="PhonePe Pulse PRO", layout="wide", page_icon="📈")

# The fix for your previous error is 'unsafe_allow_html=True'
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
        
        # Professional Cleaning: Sync state names for the India Map
        for df in [t_df, u_df, m_df]:
            df['State'] = df['State'].str.replace('-', ' ').str.title()
            df['State'] = df['State'].str.replace('Andaman & Nicobar Islands', 'Andaman & Nicobar')
            df['State'] = df['State'].str.replace('Dadra & Nagar Haveli & Daman & Diu', 'Dadra and Nagar Haveli and Daman and Diu')
        return t_df, u_df, m_df
    except Exception as e:
        return None, None, str(e)

trans_df, user_df, map_df = load_and_clean_data()

# Error handling if CSVs are missing
if trans_df is None:
    st.error(f"⚠️ CSV files not found or Error: {map_df}. Please ensure your CSV files are in the main folder of your GitHub repo.")
    st.stop()

# --- 3. SIDEBAR FILTERS ---
with st.sidebar:
    st.title("📊 Control Panel")
    year = st.selectbox("Select Year", sorted(trans_df['Year'].unique(), reverse=True))
    quarter = st.select_slider("Select Quarter", options=[1, 2, 3, 4])
    st.divider()
    st.info("This dashboard visualizes PhonePe's transaction and user data across India.")

# Apply filters
f_trans = trans_df[(trans_df['Year'] == year) & (trans_df['Quarter'] == quarter)]
f_map = map_df[(map_df['Year'] == year) & (map_df['Quarter'] == quarter)]
f_user = user_df[(user_df['Year'] == year) & (user_df['Quarter'] == quarter)]

# --- 4. DASHBOARD HEADER ---
st.title("📱 PhonePe Pulse Analytics")
st.caption(f"Showing insights for Financial Year {year} | Quarter {quarter}")

# Top KPI Metrics
m1, m2, m3 = st.columns(3)
total_val = f_trans['Transaction_Amount'].sum()
total_cnt = f_trans['Transaction_Count'].sum()
total_reg = f_user['Registered_Users'].sum()

m1.metric("Total Transaction Value", f"₹{total_val/1e7:.2f} Cr")
m2.metric("Total Transactions", f"{total_cnt/1e5:.2f} L")
m3.metric("Registered Users", f"{total_reg/1e5:.2f} L")

st.divider()

# --- 5. VISUALIZATIONS ---
row1_col1, row1_col2 = st.columns([1.3, 0.7])

with row1_col1:
    st.subheader("🗺️ India Transaction Heatmap")
    # Group by state for map
    map_data = f_map.groupby("State")["Amount"].sum().reset_index()
    
    fig_india = px.choropleth(
        map_data,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9ad97d3121354efebd9e57e/raw/0ad293846248c1d3008a30ad47e440590f1a3229/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color='Amount',
        color_continuous_scale="Viridis",
        template="plotly_dark",
        hover_name="State"
    )
    fig_india.update_geos(fitbounds="locations", visible=False)
    fig_india.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
    st.plotly_chart(fig_india, key="india_map")

with row1_col2:
    st.subheader("📊 Category Breakdown")
    type_data = f_trans.groupby("Transaction_Type")["Transaction_Amount"].sum().reset_index()
    fig_pie = px.pie(type_data, values='Transaction_Amount', names='Transaction_Type', hole=0.5)
    fig_pie.update_layout(showlegend=False, height=450)
    st.plotly_chart(fig_pie, key="type_pie")

# --- 6. TOP PERFORMERS ---
st.divider()
st.subheader(f"🏆 Top 10 States by Transaction Volume")
top_states = f_trans.groupby("State")["Transaction_Amount"].sum().sort_values(ascending=False).head(10).reset_index()

fig_bar = px.bar(top_states, x="Transaction_Amount", y="State", orientation='h', 
                 color="Transaction_Amount", color_continuous_scale="Purples")
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar, key="top_states_bar")

st.caption("Data source: PhonePe Pulse Open Data | Developed by Kartik")

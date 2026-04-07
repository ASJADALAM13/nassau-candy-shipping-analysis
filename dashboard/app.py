# ============================================================
# Nassau Candy Distributor
# Factory-to-Customer Shipping Route Efficiency Dashboard
# ============================================================
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Nassau Candy Shipping Dashboard",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    # df = pd.read_csv(r"A:\UM\nassau_candy_project\data\Nassau Candy Distributor.csv")
    df = pd.read_csv(r"data/Nassau Candy Distributor.csv")

    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d-%m-%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d-%m-%Y')
    df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    df = df[df['Lead Time'] > 0]
    factory_mapping = {
        'Wonka Bar - Nutty Crunch Surprise': "Lot's O' Nuts",
        'Wonka Bar - Fudge Mallows': "Lot's O' Nuts",
        'Wonka Bar -Scrumdiddlyumptious': "Lot's O' Nuts",
        'Wonka Bar - Milk Chocolate': "Wicked Choccy's",
        'Wonka Bar - Triple Dazzle Caramel': "Wicked Choccy's",
        'Laffy Taffy': 'Sugar Shack',
        'SweeTARTS': 'Sugar Shack',
        'Nerds': 'Sugar Shack',
        'Fun Dip': 'Sugar Shack',
        'Fizzy Lifting Drinks': 'Sugar Shack',
        'Everlasting Gobstopper': 'Secret Factory',
        'Hair Toffee': 'The Other Factory',
        'Lickable Wallpaper': 'Secret Factory',
        'Wonka Gum': 'Secret Factory',
        'Kazookles': 'The Other Factory'
    }
    df['Factory'] = df['Product Name'].map(factory_mapping)
    df['Route'] = df['Factory'] + ' → ' + df['State/Province']
    df['Region Route'] = df['Factory'] + ' → ' + df['Region']
    return df

df = load_data()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("""
<div style='background-color:#2E75B6; padding:15px; border-radius:8px; text-align:center;'>
    <h2 style='color:white; margin:0;'>🍬 Nassau Candy</h2>
    <p style='color:#D6E4F0; margin:0; font-size:12px;'>Shipping Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.title("Dashboard Filters")

# date range filter
st.sidebar.subheader("📅 Date Range")
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# region filter
st.sidebar.subheader("🌍 Region")
all_regions = ['All'] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", all_regions)

# state filter
st.sidebar.subheader("📍 State")
if selected_region == 'All':
    all_states = ['All'] + sorted(df['State/Province'].unique().tolist())
else:
    all_states = ['All'] + sorted(
        df[df['Region'] == selected_region]['State/Province'].unique().tolist()
    )
selected_state = st.sidebar.selectbox("Select State", all_states)

# ship mode filter
st.sidebar.subheader("🚚 Ship Mode")
all_shipmodes = ['All'] + sorted(df['Ship Mode'].unique().tolist())
selected_shipmode = st.sidebar.selectbox("Select Ship Mode", all_shipmodes)

# lead time threshold slider
st.sidebar.subheader("⏱️ Lead Time Threshold")
max_lead = int(df['Lead Time'].max())
min_lead = int(df['Lead Time'].min())
lead_threshold = st.sidebar.slider(
    "Maximum Lead Time (Days)",
    min_value=min_lead,
    max_value=max_lead,
    value=max_lead
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**About this Dashboard**
- **Project:** Nassau Candy Shipping Analysis
- **Analyst:** MD Asjad Alam
- **Data:** 10,194 orders (2024-2025)
- **Routes:** 196 unique routes
- **Factories:** 5 factories
""")

# ============================================================
# APPLYING FILTERS
# ============================================================
filtered_df = df.copy()
filtered_df = filtered_df[
    (filtered_df['Order Date'].dt.date >= start_date) &
    (filtered_df['Order Date'].dt.date <= end_date)
]
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_state != 'All':
    filtered_df = filtered_df[filtered_df['State/Province'] == selected_state]
if selected_shipmode != 'All':
    filtered_df = filtered_df[filtered_df['Ship Mode'] == selected_shipmode]
filtered_df = filtered_df[filtered_df['Lead Time'] <= lead_threshold]

# safety check
if len(filtered_df) == 0:
    st.warning("⚠️ No data found for the selected filters. Please adjust your filters.")
    st.stop()

# ============================================================
# COMPUTING KPIs
# ============================================================
avg_lead_time = filtered_df['Lead Time'].mean()
filtered_df = filtered_df.copy()
filtered_df['Is Delayed'] = filtered_df['Lead Time'] > avg_lead_time

route_analysis = filtered_df.groupby('Route').agg(
    Total_Shipments=('Order ID', 'count'),
    Avg_Lead_Time=('Lead Time', 'mean'),
    Delay_Frequency=('Is Delayed', 'mean')
).reset_index()
route_analysis['Delay_Frequency_%'] = (route_analysis['Delay_Frequency'] * 100).round(2)
route_analysis['Avg_Lead_Time'] = route_analysis['Avg_Lead_Time'].round(2)

scaler = MinMaxScaler()
if len(route_analysis) > 1:
    route_analysis['Norm_Lead_Time'] = scaler.fit_transform(route_analysis[['Avg_Lead_Time']])
    route_analysis['Norm_Delay_Freq'] = scaler.fit_transform(route_analysis[['Delay_Frequency_%']])
    route_analysis['Efficiency_Score'] = (
        1 - (route_analysis['Norm_Lead_Time'] + route_analysis['Norm_Delay_Freq']) / 2
    ).round(4)
else:
    route_analysis['Efficiency_Score'] = 1.0

route_analysis = route_analysis.sort_values(
    'Efficiency_Score', ascending=False
).reset_index(drop=True)

shipmode_analysis = filtered_df.groupby('Ship Mode').agg(
    Total_Shipments=('Order ID', 'count'),
    Avg_Lead_Time=('Lead Time', 'mean'),
    Delay_Frequency=('Is Delayed', 'mean')
).reset_index()
shipmode_analysis['Delay_Frequency_%'] = (shipmode_analysis['Delay_Frequency'] * 100).round(2)
shipmode_analysis['Avg_Lead_Time'] = shipmode_analysis['Avg_Lead_Time'].round(2)

state_analysis = filtered_df.groupby('State/Province').agg(
    Total_Shipments=('Order ID', 'count'),
    Avg_Lead_Time=('Lead Time', 'mean'),
    Delay_Frequency=('Is Delayed', 'mean')
).reset_index()
state_analysis['Delay_Frequency_%'] = (state_analysis['Delay_Frequency'] * 100).round(2)
state_analysis['Avg_Lead_Time'] = state_analysis['Avg_Lead_Time'].round(2)

factory_analysis = filtered_df.groupby('Factory').agg(
    Total_Shipments=('Order ID', 'count'),
    Avg_Lead_Time=('Lead Time', 'mean'),
    Delay_Frequency=('Is Delayed', 'mean')
).reset_index()
factory_analysis['Delay_Frequency_%'] = (factory_analysis['Delay_Frequency'] * 100).round(2)
factory_analysis['Avg_Lead_Time'] = factory_analysis['Avg_Lead_Time'].round(2)
factory_analysis = factory_analysis.sort_values('Avg_Lead_Time').reset_index(drop=True)

# ============================================================
# DASHBOARD HEADER
# ============================================================
st.title("🍬 Nassau Candy Distributor")
st.subheader("Factory-to-Customer Shipping Route Efficiency Dashboard")
st.markdown("---")

# filter summary
st.info(f"📊 Showing **{len(filtered_df):,}** orders | Region: **{selected_region}** | State: **{selected_state}** | Ship Mode: **{selected_shipmode}** | Max Lead Time: **{lead_threshold} days**")

# ============================================================
# KPI CARDS
# ============================================================
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="Total Orders", value=f"{len(filtered_df):,}")
with col2:
    st.metric(label="Avg Lead Time", value=f"{filtered_df['Lead Time'].mean():.1f} days")
with col3:
    st.metric(label="Total Routes", value=f"{route_analysis.shape[0]}")
with col4:
    st.metric(label="Delay Frequency", value=f"{filtered_df['Is Delayed'].mean()*100:.1f}%")
with col5:
    st.metric(label="Avg Efficiency Score", value=f"{route_analysis['Efficiency_Score'].mean():.3f}")

st.markdown("---")

# ============================================================
# MODULE 1 — ROUTE EFFICIENCY OVERVIEW
# ============================================================
st.header("📦 Module 1 — Route Efficiency Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Most Efficient Routes")
    top10 = route_analysis.head(10)
    fig_top = px.bar(
        top10,
        x='Efficiency_Score',
        y='Route',
        orientation='h',
        color='Efficiency_Score',
        color_continuous_scale='Blues',
        text='Efficiency_Score',
        labels={'Efficiency_Score': 'Score', 'Route': 'Route'}
    )
    fig_top.update_layout(
        plot_bgcolor='white',
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    st.subheader("⚠️ Bottom 10 Least Efficient Routes")
    bottom10 = route_analysis.tail(10)
    fig_bottom = px.bar(
        bottom10,
        x='Efficiency_Score',
        y='Route',
        orientation='h',
        color='Efficiency_Score',
        color_continuous_scale='Reds',
        text='Efficiency_Score',
        labels={'Efficiency_Score': 'Score', 'Route': 'Route'}
    )
    fig_bottom.update_layout(
        plot_bgcolor='white',
        height=400,
        yaxis={'categoryorder': 'total descending'}
    )
    st.plotly_chart(fig_bottom, use_container_width=True)

# route leaderboard
st.subheader("📋 Full Route Performance Leaderboard")
st.dataframe(
    route_analysis[['Route', 'Total_Shipments',
                    'Avg_Lead_Time', 'Delay_Frequency_%',
                    'Efficiency_Score']],
    use_container_width=True,
    height=400,
    column_config={
        "Efficiency_Score": st.column_config.ProgressColumn(
            "Efficiency Score",
            min_value=0,
            max_value=1,
            format="%.4f"
        ),
        "Delay_Frequency_%": st.column_config.NumberColumn(
            "Delay Frequency %",
            format="%.2f%%"
        ),
        "Avg_Lead_Time": st.column_config.NumberColumn(
            "Avg Lead Time (Days)",
            format="%.2f"
        )
    }
)

# download button
csv = route_analysis[['Route', 'Total_Shipments',
                       'Avg_Lead_Time', 'Delay_Frequency_%',
                       'Efficiency_Score']].to_csv(index=False)
st.download_button(
    label="📥 Download Route Analysis CSV",
    data=csv,
    file_name="nassau_candy_route_analysis.csv",
    mime="text/csv"
)

st.markdown("---")

# ============================================================
# MODULE 2 — GEOGRAPHIC SHIPPING MAP
# ============================================================
st.header("🗺️ Module 2 — Geographic Shipping Map")

location_coords = {
    'Alabama': (32.8, -86.8), 'Alaska': (64.2, -153.4),
    'Arizona': (34.3, -111.1), 'Arkansas': (34.8, -92.2),
    'California': (36.8, -119.4), 'Colorado': (39.0, -105.5),
    'Connecticut': (41.6, -72.7), 'Delaware': (39.0, -75.5),
    'Florida': (27.8, -81.7), 'Georgia': (32.2, -82.9),
    'Hawaii': (20.9, -157.4), 'Idaho': (44.2, -114.5),
    'Illinois': (40.3, -89.0), 'Indiana': (40.3, -86.1),
    'Iowa': (42.0, -93.2), 'Kansas': (38.5, -98.4),
    'Kentucky': (37.5, -85.3), 'Louisiana': (31.1, -91.8),
    'Maine': (44.7, -69.4), 'Maryland': (39.1, -76.8),
    'Massachusetts': (42.2, -71.5), 'Michigan': (44.3, -85.4),
    'Minnesota': (46.4, -93.1), 'Mississippi': (32.7, -89.7),
    'Missouri': (38.5, -92.3), 'Montana': (46.9, -110.5),
    'Nebraska': (41.5, -99.9), 'Nevada': (39.3, -116.6),
    'New Hampshire': (43.5, -71.6), 'New Jersey': (40.1, -74.5),
    'New Mexico': (34.8, -106.2), 'New York': (42.2, -74.9),
    'North Carolina': (35.6, -79.8), 'North Dakota': (47.5, -100.5),
    'Ohio': (40.4, -82.8), 'Oklahoma': (35.6, -96.9),
    'Oregon': (43.9, -120.6), 'Pennsylvania': (40.6, -77.2),
    'Rhode Island': (41.7, -71.5), 'South Carolina': (33.9, -80.9),
    'South Dakota': (44.4, -100.2), 'Tennessee': (35.9, -86.7),
    'Texas': (31.1, -97.6), 'Utah': (39.4, -111.1),
    'Vermont': (44.1, -72.7), 'Virginia': (37.8, -78.2),
    'Washington': (47.4, -121.5), 'West Virginia': (38.5, -80.6),
    'Wisconsin': (44.3, -89.6), 'Wyoming': (43.0, -107.6),
    'District of Columbia': (38.9, -77.0),
    'Ontario': (51.3, -85.3), 'Alberta': (55.0, -115.0),
    'British Columbia': (53.7, -127.6), 'Quebec': (52.9, -73.5),
    'Nova Scotia': (45.0, -63.0), 'Manitoba': (55.0, -97.0),
    'Saskatchewan': (55.0, -106.0), 'New Brunswick': (46.5, -66.5),
    'Newfoundland and Labrador': (53.1, -59.0),
    'Prince Edward Island': (46.3, -63.3)
}
#From Project Description
factory_coords = {
    "Lot's O' Nuts":     {'lat': 32.881893, 'lon': -111.768036},
    "Wicked Choccy's":   {'lat': 32.076176, 'lon': -81.088371},
    "Sugar Shack":       {'lat': 48.11914,  'lon': -96.18115},
    "Secret Factory":    {'lat': 41.446333, 'lon': -90.565487},
    "The Other Factory": {'lat': 35.1175,   'lon': -89.971107}
}
factory_coords_df = pd.DataFrame([
    {'Factory': name, 'Lat': v['lat'], 'Lon': v['lon']}
    for name, v in factory_coords.items()
])

state_analysis['Lat'] = state_analysis['State/Province'].map(
    lambda x: location_coords.get(x, (None, None))[0]
)
state_analysis['Lon'] = state_analysis['State/Province'].map(
    lambda x: location_coords.get(x, (None, None))[1]
)
state_map = state_analysis.dropna(subset=['Lat', 'Lon'])

map_type = st.radio(
    "Select Map View:",
    ["Customer Destinations", "Complete Shipping Network"],
    horizontal=True
)

if map_type == "Customer Destinations":
    fig_map = px.scatter_geo(
        state_map,
        lat='Lat', lon='Lon',
        color='Avg_Lead_Time',
        size='Total_Shipments',
        hover_name='State/Province',
        hover_data={
            'Avg_Lead_Time': True,
            'Delay_Frequency_%': True,
            'Total_Shipments': True,
            'Lat': False, 'Lon': False
        },
        title='Average Shipping Lead Time — US and Canada',
        color_continuous_scale='RdYlGn_r',
        scope='north america',
        labels={'Avg_Lead_Time': 'Avg Lead Time (Days)'}
    )
else:
    fig_map = px.scatter_geo(
        state_map,
        lat='Lat', lon='Lon',
        color='Avg_Lead_Time',
        size='Total_Shipments',
        hover_name='State/Province',
        hover_data={
            'Avg_Lead_Time': True,
            'Delay_Frequency_%': True,
            'Total_Shipments': True,
            'Lat': False, 'Lon': False
        },
        title='Nassau Candy — Complete Shipping Network',
        color_continuous_scale='RdYlGn_r',
        scope='north america',
        labels={'Avg_Lead_Time': 'Avg Lead Time (Days)'}
    )
    fig_map.add_trace(go.Scattergeo(
        lat=factory_coords_df['Lat'],
        lon=factory_coords_df['Lon'],
        text=factory_coords_df['Factory'],
        mode='markers',
        marker=dict(symbol='star', size=20,
                    color='gold',
                    line=dict(color='black', width=1)),
        name='Factories',
        hoverinfo='text'
    ))

fig_map.update_layout(
    height=600,
    geo=dict(
        showland=True, landcolor='lightgray',
        showocean=True, oceancolor='lightblue',
        showlakes=True, lakecolor='lightblue',
        showcoastlines=True, coastlinecolor='white',
        lonaxis=dict(range=[-170, -50]),
        lataxis=dict(range=[20, 75])
    )
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# ============================================================
# MODULE 3 — SHIP MODE COMPARISON
# ============================================================
st.header("🚚 Module 3 — Ship Mode Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Lead Time by Ship Mode")
    fig_sm1 = px.bar(
        shipmode_analysis.sort_values('Avg_Lead_Time'),
        x='Ship Mode',
        y='Avg_Lead_Time',
        color='Avg_Lead_Time',
        color_continuous_scale='RdYlGn_r',
        text='Avg_Lead_Time',
        labels={'Avg_Lead_Time': 'Avg Lead Time (Days)'}
    )
    fig_sm1.update_layout(plot_bgcolor='white', height=350)
    st.plotly_chart(fig_sm1, use_container_width=True)

with col2:
    st.subheader("Delay Frequency by Ship Mode")
    fig_sm2 = px.bar(
        shipmode_analysis.sort_values('Delay_Frequency_%'),
        x='Ship Mode',
        y='Delay_Frequency_%',
        color='Delay_Frequency_%',
        color_continuous_scale='RdYlGn_r',
        text='Delay_Frequency_%',
        labels={'Delay_Frequency_%': 'Delay Frequency (%)'}
    )
    fig_sm2.update_layout(plot_bgcolor='white', height=350)
    st.plotly_chart(fig_sm2, use_container_width=True)

st.markdown("---")

# ============================================================
# MODULE 4 — ROUTE DRILL DOWN
# ============================================================
st.header("🔍 Module 4 — Route Drill Down")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Factory Performance")
    fig_factory = px.bar(
        factory_analysis,
        x='Factory',
        y='Avg_Lead_Time',
        color='Delay_Frequency_%',
        color_continuous_scale='RdYlGn_r',
        text='Avg_Lead_Time',
        labels={
            'Avg_Lead_Time': 'Avg Lead Time (Days)',
            'Factory': 'Factory Name'
        }
    )
    fig_factory.update_layout(plot_bgcolor='white', height=350)
    st.plotly_chart(fig_factory, use_container_width=True)

with col2:
    st.subheader("Top 15 Most Delayed States")
    top_states = state_analysis.sort_values(
        'Avg_Lead_Time', ascending=False
    ).head(15)
    fig_state = px.bar(
        top_states,
        x='Avg_Lead_Time',
        y='State/Province',
        orientation='h',
        color='Delay_Frequency_%',
        color_continuous_scale='RdYlGn_r',
        text='Avg_Lead_Time',
        labels={
            'Avg_Lead_Time': 'Avg Lead Time (Days)',
            'State/Province': 'State'
        }
    )
    fig_state.update_layout(
        plot_bgcolor='white',
        height=350,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_state, use_container_width=True)

# order level data
st.subheader("📋 Order Level Shipment Data")
st.dataframe(
    filtered_df[[
        'Order ID', 'Order Date', 'Ship Date',
        'Lead Time', 'Factory', 'Route',
        'Ship Mode', 'State/Province', 'Region',
        'Is Delayed'
    ]].sort_values('Lead Time', ascending=False),
    use_container_width=True,
    height=400
)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🍭 Nassau Candy Distributor")
with col2:
    st.caption("📈 Internship Project")
with col3:
    st.caption(" MD Asjad Alam | April 2026")
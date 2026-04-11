

# ============================================================
# Nassau Candy Distributor
# Factory-to-Customer Shipping Route Efficiency Dashboard
# Built by: MD Asjad Alam | Data Analytics Internship | April 2026
# ============================================================
# This dashboard analyzes planned shipping route efficiency
# across Nassau Candy's factory-to-customer network.
# Note: Ship Dates are planned future delivery dates (2026-2030),
# so all lead times represent planned delivery timelines.
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
# set the browser tab title, icon, and layout
# ============================================================
st.set_page_config(
    page_title="Nassau Candy Shipping Dashboard",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LOAD AND PREPARE DATA
# we cache this so the app does not reload data on every filter change
# ============================================================
@st.cache_data
def load_data():
    # loading the main dataset
    # df = pd.read_csv(r"A:\UM\nassau_candy_project\data\Nassau Candy Distributor.csv")

    # using a relative path so this works both locally and on Streamlit Cloud
    df = pd.read_csv('data/Nassau Candy Distributor.csv')

    # converting date columns from text to proper datetime format
    # without this conversion we cannot subtract dates to get lead time
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d-%m-%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d-%m-%Y')

    # calculating planned lead time in days
    # Ship Dates are planned future delivery dates (2026-2030)
    # so this represents the planned number of days from order to delivery
    df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

    # removing any records where lead time is zero or negative
    # those would be data entry errors and make no logical sense
    df = df[df['Lead Time'] > 0]

    # mapping each product to its factory
    # this information comes from the project description
    # since the dataset does not have a Factory column directly
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

    # applying the factory mapping to create a new Factory column
    df['Factory'] = df['Product Name'].map(factory_mapping)

    # creating the Route column — the core feature of this entire analysis
    # State-level route: Factory → Customer State (196 unique routes)
    # Region-level route: Factory → Customer Region (20 unique routes)
    df['Route'] = df['Factory'] + ' → ' + df['State/Province']
    df['Region Route'] = df['Factory'] + ' → ' + df['Region']

    return df

# loading the data when the app starts
df = load_data()

# ============================================================
# SIDEBAR — BRANDING AND FILTERS
# ============================================================

# branded header using custom HTML since Streamlit does not have a styled banner component
st.sidebar.markdown("""
<div style='background-color:#2E75B6; padding:15px; border-radius:8px; text-align:center;'>
    <h2 style='color:white; margin:0;'>🍬 Nassau Candy</h2>
    <p style='color:#D6E4F0; margin:0; font-size:12px;'>Shipping Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.title("Dashboard Filters")
st.sidebar.caption("All filters update every chart on this page in real time.")

# --- Date Range Filter ---
# lets users focus on a specific period of order dates
st.sidebar.subheader("📅 Order Date Range")
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# --- Region Filter ---
# selecting a region also updates the State filter below it
st.sidebar.subheader("🌍 Region")
all_regions = ['All'] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", all_regions)

# --- State Filter ---
# if a region is selected, only show states from that region
st.sidebar.subheader("📍 State / Province")
if selected_region == 'All':
    all_states = ['All'] + sorted(df['State/Province'].unique().tolist())
else:
    all_states = ['All'] + sorted(
        df[df['Region'] == selected_region]['State/Province'].unique().tolist()
    )
selected_state = st.sidebar.selectbox("Select State", all_states)

# --- Ship Mode Filter ---
st.sidebar.subheader("🚚 Ship Mode")
all_shipmodes = ['All'] + sorted(df['Ship Mode'].unique().tolist())
selected_shipmode = st.sidebar.selectbox("Select Ship Mode", all_shipmodes)

# --- Lead Time Threshold Slider ---
# lets users filter out routes with planned lead times above a threshold
st.sidebar.subheader("⏱️ Max Planned Lead Time")
max_lead = int(df['Lead Time'].max())
min_lead = int(df['Lead Time'].min())
lead_threshold = st.sidebar.slider(
    "Maximum Lead Time (Days)",
    min_value=min_lead,
    max_value=max_lead,
    value=max_lead
)

st.sidebar.markdown("---")

# project info section at the bottom of sidebar
st.sidebar.markdown("""
**About this Dashboard**
- **Project:** Nassau Candy Shipping Analysis
- **Analyst:** MD Asjad Alam
- **Orders:** 10,194 (Jan 2024 – Dec 2025)
- **Routes:** 196 unique factory-to-state routes
- **Factories:** 5 manufacturing locations
- **Note:** Ship Dates are planned future dates
""")

# ============================================================
# APPLYING FILTERS TO THE DATASET
# we apply filters one by one so each one stacks on the previous
# ============================================================
filtered_df = df.copy()

# applying the date range filter on Order Date
filtered_df = filtered_df[
    (filtered_df['Order Date'].dt.date >= start_date) &
    (filtered_df['Order Date'].dt.date <= end_date)
]

# applying region filter if a specific region was selected
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

# applying state filter if a specific state was selected
if selected_state != 'All':
    filtered_df = filtered_df[filtered_df['State/Province'] == selected_state]

# applying ship mode filter if a specific mode was selected
if selected_shipmode != 'All':
    filtered_df = filtered_df[filtered_df['Ship Mode'] == selected_shipmode]

# applying the lead time threshold — removes orders with very long planned lead times
filtered_df = filtered_df[filtered_df['Lead Time'] <= lead_threshold]

# safety check — if filters remove all data, show a warning and stop
# without this the app would crash with confusing errors
if len(filtered_df) == 0:
    st.warning("⚠️ No data found for the selected filters. Please adjust your filters and try again.")
    st.stop()

# ============================================================
# COMPUTING KPIs FROM FILTERED DATA
# all calculations below use the filtered dataset
# so every metric updates when filters change
# ============================================================

# using average lead time as our delay threshold
# any order with lead time above average is flagged as "above average delay"
# we use average because a fixed day threshold (like 5 days) does not
# make sense when planned lead times range from 904 to 1,642 days
avg_lead_time = filtered_df['Lead Time'].mean()
filtered_df = filtered_df.copy()
filtered_df['Is Delayed'] = filtered_df['Lead Time'] > avg_lead_time

# --- Route Level Analysis ---
# grouping all orders by route and calculating performance metrics
route_analysis = filtered_df.groupby('Route').agg(
    Total_Shipments=('Order ID', 'count'),
    Avg_Lead_Time=('Lead Time', 'mean'),
    Delay_Frequency=('Is Delayed', 'mean')
).reset_index()

# converting delay frequency from decimal to percentage and rounding
route_analysis['Delay_Frequency_%'] = (route_analysis['Delay_Frequency'] * 100).round(2)
route_analysis['Avg_Lead_Time'] = route_analysis['Avg_Lead_Time'].round(2)

# calculating Route Efficiency Score using Min-Max normalization
# this combines lead time and delay frequency into one score between 0 and 1
# higher score = more efficient route
# we need at least 2 routes to normalize — otherwise just set score to 1.0
scaler = MinMaxScaler()
if len(route_analysis) > 1:
    route_analysis['Norm_Lead_Time'] = scaler.fit_transform(route_analysis[['Avg_Lead_Time']])
    route_analysis['Norm_Delay_Freq'] = scaler.fit_transform(route_analysis[['Delay_Frequency_%']])
    route_analysis['Efficiency_Score'] = (
        1 - (route_analysis['Norm_Lead_Time'] + route_analysis['Norm_Delay_Freq']) / 2
    ).round(4)
else:
    route_analysis['Efficiency_Score'] = 1.0

# sorting by efficiency score — best routes at the top
route_analysis = route_analysis.sort_values(
    'Efficiency_Score', ascending=False
).reset_index(drop=True)

# --- Ship Mode Analysis ---
shipmode_analysis = filtered_df.groupby('Ship Mode').agg(
    Total_Shipments=('Order ID', 'count'),
    Avg_Lead_Time=('Lead Time', 'mean'),
    Delay_Frequency=('Is Delayed', 'mean')
).reset_index()
shipmode_analysis['Delay_Frequency_%'] = (shipmode_analysis['Delay_Frequency'] * 100).round(2)
shipmode_analysis['Avg_Lead_Time'] = shipmode_analysis['Avg_Lead_Time'].round(2)

# --- State Level Analysis ---
state_analysis = filtered_df.groupby('State/Province').agg(
    Total_Shipments=('Order ID', 'count'),
    Avg_Lead_Time=('Lead Time', 'mean'),
    Delay_Frequency=('Is Delayed', 'mean')
).reset_index()
state_analysis['Delay_Frequency_%'] = (state_analysis['Delay_Frequency'] * 100).round(2)
state_analysis['Avg_Lead_Time'] = state_analysis['Avg_Lead_Time'].round(2)

# --- Factory Level Analysis ---
# sorted ascending so best performing factory (lowest lead time) appears first
factory_analysis = filtered_df.groupby('Factory').agg(
    Total_Shipments=('Order ID', 'count'),
    Avg_Lead_Time=('Lead Time', 'mean'),
    Delay_Frequency=('Is Delayed', 'mean')
).reset_index()
factory_analysis['Delay_Frequency_%'] = (factory_analysis['Delay_Frequency'] * 100).round(2)
factory_analysis['Avg_Lead_Time'] = factory_analysis['Avg_Lead_Time'].round(2)
factory_analysis = factory_analysis.sort_values('Avg_Lead_Time').reset_index(drop=True)

# ============================================================
# MAIN DASHBOARD — HEADER
# ============================================================
st.title("🍬 Nassau Candy Distributor")
st.subheader("Factory-to-Customer Shipping Route Efficiency Dashboard")
st.markdown("---")

# showing the user exactly what data they are currently looking at
st.info(
    f"📊 Showing **{len(filtered_df):,}** orders  |  "
    f"Region: **{selected_region}**  |  "
    f"State: **{selected_state}**  |  "
    f"Ship Mode: **{selected_shipmode}**  |  "
    f"Max Lead Time: **{lead_threshold:,} days**"
)

# important disclaimer about the nature of this dataset
st.caption(
    "📌 Note: Ship Dates in this dataset represent planned future delivery dates (2026–2030). "
    "All lead times and delay rates reflect planned delivery timelines, not historical completed deliveries. "
    "This is a forward-looking logistics planning analysis."
)

# ============================================================
# KPI CARDS — 5 KEY METRICS AT A GLANCE
# ============================================================
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Orders",
        value=f"{len(filtered_df):,}",
        help="Total number of orders in the filtered dataset"
    )
with col2:
    st.metric(
        label="Avg Planned Lead Time",
        value=f"{filtered_df['Lead Time'].mean():.0f} days",
        help="Average number of days between order placement and planned delivery"
    )
with col3:
    st.metric(
        label="Total Routes",
        value=f"{route_analysis.shape[0]}",
        help="Number of unique factory-to-state routes in the filtered data"
    )
with col4:
    st.metric(
        label="Above-Average Delay Rate",
        value=f"{filtered_df['Is Delayed'].mean()*100:.1f}%",
        help="Percentage of orders with planned lead time above the average threshold"
    )
with col5:
    st.metric(
        label="Avg Efficiency Score",
        value=f"{route_analysis['Efficiency_Score'].mean():.3f}",
        help="Average route efficiency score (0 = worst, 1 = best)"
    )

st.markdown("---")

# ============================================================
# MODULE 1 — ROUTE EFFICIENCY OVERVIEW
# ============================================================
st.header("📦 Module 1 — Route Efficiency Overview")
st.caption(
    "The Route Efficiency Score combines planned lead time and above-average delay rate "
    "into a single normalized score. Higher is better. Score of 1.0 = perfect, 0.0 = critical."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Best Performing Routes")
    top10 = route_analysis.head(10)
    fig_top = px.bar(
        top10,
        x='Efficiency_Score',
        y='Route',
        orientation='h',
        color='Efficiency_Score',
        color_continuous_scale='Blues',
        text='Efficiency_Score',
        labels={'Efficiency_Score': 'Efficiency Score', 'Route': 'Route'},
        title='Top 10 Routes — Planned to Perform Best'
    )
    fig_top.update_layout(
        plot_bgcolor='white',
        height=420,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    fig_top.update_traces(texttemplate='%{text:.4f}', textposition='outside')
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    st.subheader("⚠️ Bottom 10 Routes Needing Attention")
    bottom10 = route_analysis.tail(10)
    fig_bottom = px.bar(
        bottom10,
        x='Efficiency_Score',
        y='Route',
        orientation='h',
        color='Efficiency_Score',
        color_continuous_scale='Reds',
        text='Efficiency_Score',
        labels={'Efficiency_Score': 'Efficiency Score', 'Route': 'Route'},
        title='Bottom 10 Routes — Planned to Underperform'
    )
    fig_bottom.update_layout(
        plot_bgcolor='white',
        height=420,
        yaxis={'categoryorder': 'total descending'},
        showlegend=False
    )
    fig_bottom.update_traces(texttemplate='%{text:.4f}', textposition='outside')
    st.plotly_chart(fig_bottom, use_container_width=True)

# full route leaderboard with progress bar for efficiency score
st.subheader("📋 Full Route Performance Leaderboard")
st.caption("Click any column header to sort. The Efficiency Score bar shows relative performance at a glance.")
st.dataframe(
    route_analysis[['Route', 'Total_Shipments', 'Avg_Lead_Time', 'Delay_Frequency_%', 'Efficiency_Score']],
    use_container_width=True,
    height=420,
    column_config={
        "Route": st.column_config.TextColumn("Route", width="large"),
        "Total_Shipments": st.column_config.NumberColumn("Total Orders", format="%d"),
        "Avg_Lead_Time": st.column_config.NumberColumn("Avg Planned Lead Time (Days)", format="%.2f"),
        "Delay_Frequency_%": st.column_config.NumberColumn("Above-Avg Delay Rate %", format="%.2f%%"),
        "Efficiency_Score": st.column_config.ProgressColumn(
            "Efficiency Score",
            min_value=0,
            max_value=1,
            format="%.4f"
        )
    }
)

# download button so users can take the analysis offline
csv = route_analysis[['Route', 'Total_Shipments', 'Avg_Lead_Time', 'Delay_Frequency_%', 'Efficiency_Score']].to_csv(index=False)
st.download_button(
    label="📥 Download Route Analysis as CSV",
    data=csv,
    file_name="nassau_candy_route_analysis.csv",
    mime="text/csv",
    help="Download the full route performance table as a CSV file"
)

st.markdown("---")

# ============================================================
# MODULE 2 — GEOGRAPHIC SHIPPING MAP
# ============================================================
st.header("🗺️ Module 2 — Geographic Shipping Map")
st.caption(
    "Each circle represents a delivery destination. "
    "Circle size = number of orders. Circle color = planned average lead time. "
    "Green = shorter planned lead time. Red = longer planned lead time."
)

# geographic center coordinates for all US states and Canadian provinces
# sourced from standard geographic reference data
# used because our data includes both US and Canadian customers
# a standard US choropleth map cannot show Canadian provinces
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
    # Canadian provinces — included because our dataset has Canadian customers
    'Ontario': (51.3, -85.3), 'Alberta': (55.0, -115.0),
    'British Columbia': (53.7, -127.6), 'Quebec': (52.9, -73.5),
    'Nova Scotia': (45.0, -63.0), 'Manitoba': (55.0, -97.0),
    'Saskatchewan': (55.0, -106.0), 'New Brunswick': (46.5, -66.5),
    'Newfoundland and Labrador': (53.1, -59.0),
    'Prince Edward Island': (46.3, -63.3)
}

# exact factory coordinates sourced directly from project description
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

# mapping coordinates to the state analysis dataframe
state_analysis['Lat'] = state_analysis['State/Province'].map(
    lambda x: location_coords.get(x, (None, None))[0]
)
state_analysis['Lon'] = state_analysis['State/Province'].map(
    lambda x: location_coords.get(x, (None, None))[1]
)

# dropping any states we do not have coordinates for
state_map = state_analysis.dropna(subset=['Lat', 'Lon'])

# map view toggle — customer destinations only or full network with factories
map_type = st.radio(
    "Select Map View:",
    ["📍 Customer Destinations Only", "🌐 Complete Shipping Network (with factories)"],
    horizontal=True
)

if "Customer" in map_type:
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
        title='Planned Average Lead Time by Delivery Destination — US and Canada',
        color_continuous_scale='RdYlGn_r',
        scope='north america',
        labels={'Avg_Lead_Time': 'Avg Planned Lead Time (Days)'}
    )
else:
    # complete network view with both customer circles and factory stars
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
        title='Nassau Candy — Complete Planned Shipping Network (Factories + Destinations)',
        color_continuous_scale='RdYlGn_r',
        scope='north america',
        labels={'Avg_Lead_Time': 'Avg Planned Lead Time (Days)'}
    )
    # adding factory locations as gold stars
    # hover over a star to see the factory name
    fig_map.add_trace(go.Scattergeo(
        lat=factory_coords_df['Lat'],
        lon=factory_coords_df['Lon'],
        text=factory_coords_df['Factory'],
        mode='markers',
        marker=dict(
            symbol='star',
            size=20,
            color='gold',
            line=dict(color='black', width=1)
        ),
        name='Factories',
        hoverinfo='text'
    ))

fig_map.update_layout(
    height=600,
    legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5),
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
st.caption(
    "Comparing all 4 shipping methods by planned lead time and above-average delay rate. "
    "Surprising finding: Standard Class is both the fastest and most cost-effective option."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Planned Lead Time by Ship Mode")
    fig_sm1 = px.bar(
        shipmode_analysis.sort_values('Avg_Lead_Time'),
        x='Ship Mode',
        y='Avg_Lead_Time',
        color='Avg_Lead_Time',
        color_continuous_scale='RdYlGn_r',
        text='Avg_Lead_Time',
        labels={'Avg_Lead_Time': 'Avg Planned Lead Time (Days)'},
        title='Which Ship Mode is Planned to Deliver Fastest?'
    )
    fig_sm1.update_layout(plot_bgcolor='white', height=380)
    fig_sm1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    st.plotly_chart(fig_sm1, use_container_width=True)

with col2:
    st.subheader("Above-Average Delay Rate by Ship Mode")
    fig_sm2 = px.bar(
        shipmode_analysis.sort_values('Delay_Frequency_%'),
        x='Ship Mode',
        y='Delay_Frequency_%',
        color='Delay_Frequency_%',
        color_continuous_scale='RdYlGn_r',
        text='Delay_Frequency_%',
        labels={'Delay_Frequency_%': 'Above-Average Delay Rate (%)'},
        title='Which Ship Mode Has the Highest Planned Delay Rate?'
    )
    fig_sm2.update_layout(plot_bgcolor='white', height=380)
    fig_sm2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_sm2, use_container_width=True)

st.markdown("---")

# ============================================================
# MODULE 4 — ROUTE DRILL DOWN
# ============================================================
st.header("🔍 Module 4 — Route Drill Down")
st.caption(
    "Deeper look at factory-level and state-level performance. "
    "Use the sidebar filters to isolate specific routes or regions."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Factory Performance Comparison")
    st.caption("Bar height = planned avg lead time. Color = above-average delay rate.")
    fig_factory = px.bar(
        factory_analysis,
        x='Factory',
        y='Avg_Lead_Time',
        color='Delay_Frequency_%',
        color_continuous_scale='RdYlGn_r',
        text='Avg_Lead_Time',
        labels={
            'Avg_Lead_Time': 'Avg Planned Lead Time (Days)',
            'Factory': 'Factory Name',
            'Delay_Frequency_%': 'Above-Avg Delay Rate %'
        },
        title='Which Factory Has the Best Planned Delivery Timeline?'
    )
    fig_factory.update_layout(plot_bgcolor='white', height=380)
    fig_factory.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    st.plotly_chart(fig_factory, use_container_width=True)

with col2:
    st.subheader("Top 15 States with Longest Planned Lead Times")
    st.caption("These are the destinations with the highest planned delivery timelines.")
    top_states = state_analysis.sort_values('Avg_Lead_Time', ascending=False).head(15)
    fig_state = px.bar(
        top_states,
        x='Avg_Lead_Time',
        y='State/Province',
        orientation='h',
        color='Delay_Frequency_%',
        color_continuous_scale='RdYlGn_r',
        text='Avg_Lead_Time',
        labels={
            'Avg_Lead_Time': 'Avg Planned Lead Time (Days)',
            'State/Province': 'State / Province',
            'Delay_Frequency_%': 'Above-Avg Delay Rate %'
        },
        title='States with Longest Planned Delivery Timelines'
    )
    fig_state.update_layout(
        plot_bgcolor='white',
        height=380,
        yaxis={'categoryorder': 'total ascending'}
    )
    fig_state.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    st.plotly_chart(fig_state, use_container_width=True)

# order level data table — individual shipment view
st.subheader("📋 Order-Level Shipment Planning Data")
st.caption(
    "Every individual order with its planned lead time and delay status. "
    "Sorted by longest planned lead time first. "
    "Is Delayed = True means the planned lead time exceeds the current average."
)
st.dataframe(
    filtered_df[[
        'Order ID', 'Order Date', 'Ship Date',
        'Lead Time', 'Factory', 'Route',
        'Ship Mode', 'State/Province', 'Region',
        'Is Delayed'
    ]].sort_values('Lead Time', ascending=False).rename(columns={
        'Lead Time': 'Planned Lead Time (Days)',
        'Is Delayed': 'Above Avg Lead Time'
    }),
    use_container_width=True,
    height=420
)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🍬 Nassau Candy Distributor")
with col2:
    st.caption("📊 Data Analytics Internship Project | April 2026")
with col3:
    st.caption("👨‍💻 MD Asjad Alam")

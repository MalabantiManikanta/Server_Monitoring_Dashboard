import streamlit as st
import pandas as pd
import pysqlite3 as sqlite3
import plotly.graph_objects as go
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------------------- Streamlit Page Configuration --------------------------
#st.set_page_config(page_title="Website Uptime Dashboard", layout="wide")

# -------------------------- Database Connection --------------------------
@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_data(query, params=None):
    try:
        conn = sqlite3.connect("db.sqlite3")
        logging.info(f"Executing query: {query} with params: {params}")
        df = pd.read_sql(query, conn, params=params)
        logging.info(f"Query returned {len(df)} rows")
        conn.close()
        return df
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        st.error(f"Database error occurred: {e}")
        return pd.DataFrame()

# -------------------------- Dashboard Header --------------------------
st.markdown("""
<div style="background-color:#f8f9fa; padding:15px; border-radius:5px; margin-bottom:15px;">
    <h1 style="color:#343a40; margin:0;">Enterprise Website Monitoring</h1>
    <p style="color:#6c757d; margin:0;">Real-time performance monitoring dashboard</p>
</div>
""", unsafe_allow_html=True)

# -------------------------- Sidebar Controls --------------------------
st.sidebar.markdown("""
<div style="background-color:#343a40; padding:10px; border-radius:5px; margin-bottom:15px;">
    <h3 style="color:white; margin:0;">Dashboard Controls</h3>
</div>
""", unsafe_allow_html=True)

# Time Range Selection
time_range = st.sidebar.radio("⏳ Select Time Range:", ["Last 60 Minutes", "Last 60 Hours", "Last 60 Days"])

# -------------------------- Query Based on Time Range --------------------------
@st.cache_data(ttl=600)  # Cache the data for each time range
def get_data_for_time_range(time_range):
    if time_range == "Last 60 Minutes":
        query = "SELECT * FROM monitoring_websiteuptime ORDER BY timestamp ASC LIMIT 60"  # Ascending for performance
        time_unit = "minutes"
    elif time_range == "Last 60 Hours":
        query = """
        SELECT *
        FROM (
            SELECT *
            FROM monitoring_hourlywebsiteuptime
            ORDER BY timestamp DESC
            LIMIT 60
        ) subquery
        ORDER BY timestamp ASC
        """
        time_unit = "hours"
    else:  # Last 60 Days
        # Based on available timestamps, query for the month of March 2025
        start_date = "01-03-2025"
        end_date = "31-03-2025"

        # Fetch data for the specified range from daily database in ascending order
        query = """
        SELECT *
        FROM monitoring_dailywebsiteuptime
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp ASC
        """
        params = (start_date, end_date)
        time_unit = "days"
        return fetch_data(query, params), time_unit

    return fetch_data(query), time_unit

df, time_unit = get_data_for_time_range(time_range)

# Check if DataFrame is empty and handle it
if df.empty:
    st.error("No data found for the selected time range. Please check the database or adjust the date range.")
    try:
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='monitoring_dailywebsiteuptime';")
        table_exists = cursor.fetchone()
        if table_exists:
            available_timestamps = pd.read_sql("SELECT DISTINCT timestamp FROM monitoring_dailywebsiteuptime ORDER BY timestamp ASC", conn)
            conn.close()
            if not available_timestamps.empty:
                logging.info("Available timestamps in monitoring_dailywebsiteuptime:")
                st.write("Available timestamps in the database:")
                st.write(available_timestamps)
            else:
                logging.warning("No timestamps found in monitoring_dailywebsiteuptime table.")
                st.warning("No timestamps found in the monitoring_dailywebsiteuptime table.")
        else:
            logging.error("monitoring_dailywebsiteuptime table does not exist.")
            st.error("The monitoring_dailywebsiteuptime table does not exist in the database.")
    except sqlite3.Error as e:
        logging.error(f"Error checking available timestamps: {e}")
        st.error(f"Error checking database timestamps: {e}")
    st.stop()  # Stop execution if no data is available
else:
    # -------------------------- Data Preprocessing --------------------------
    df = df.drop(columns=['id'], errors='ignore')

    try:
        # Explicitly tell pandas that the day comes first in the date string
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y', dayfirst=True, errors='raise')
    except ValueError:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='raise')
        except ValueError as e:
            st.error(f"Could not parse timestamps: {e}")
            st.stop()

    # Convert website columns to numeric and fill NaN values only once
    website_cols = [col for col in df.columns if col != "timestamp"]
    for col in website_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df[website_cols] = df[website_cols].fillna(df[website_cols].mean())  # Fill all at once

    # -------------------------- Website Selection --------------------------
    websites = [col for col in df.columns if col != "timestamp"]

    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        st.markdown("### 🌐 Select Websites")
    with col2:
        select_all = st.button("Select All")

    if select_all:
        selected_websites = websites
    else:
        selected_websites = st.sidebar.multiselect("Choose websites to monitor:", websites, default=websites[:5] if len(websites) > 5 else websites)

    if not selected_websites:
        st.warning("Please select at least one website to display data.")
        st.stop()

    # -------------------------- Max Number of Websites Warning --------------------------
    # Show warning if too many websites are selected for optimal visualization
    MAX_OPTIMAL_WEBSITES = 8
    if len(selected_websites) > MAX_OPTIMAL_WEBSITES:
        st.warning(f"You've selected {len(selected_websites)} websites. For optimal visualization, consider selecting {MAX_OPTIMAL_WEBSITES} or fewer websites.")

    # Allow for custom ordering
    st.sidebar.markdown("### 📋 Reorder Websites")
    st.sidebar.markdown("Drag to reorder websites in the visualization")
    website_order_df = pd.DataFrame({"Websites": selected_websites})
    reordered_df = st.sidebar.data_editor(website_order_df, key="website_order", use_container_width=True, hide_index=True)
    selected_websites = reordered_df["Websites"].tolist()

    df = df[["timestamp"] + selected_websites]

    # -------------------------- Status Classification Function --------------------------
    def get_status_code(value):
        if value >= 99.5:
            return 3  # Excellent
        elif value >= 98:
            return 2  # Good
        elif value >= 95:
            return 1  # Warning
        else:
            return 0  # Critical

    def get_status_name(code):
        status_names = {
            3: "Excellent",
            2: "Good",
            1: "Warning",
            0: "Critical"
        }
        return status_names.get(code, "Unknown")

    def get_color(code):
        colors = {
            3: "#2ECC71",  # Green
            2: "#3498DB",  # Blue
            1: "#F39C12",  # Orange
            0: "#E74C3C"   # Red
        }
        return colors.get(code, "#95A5A6")  # Default gray

    # -------------------------- Metrics Section --------------------------
    # Calculate number of columns to display based on number of selected websites
    num_cols = min(6, len(selected_websites))  # Max 6 columns per row
    metrics_rows = [selected_websites[i:i + num_cols] for i in range(0, len(selected_websites), num_cols)]

    for row_websites in metrics_rows:
        metrics_row = st.columns(len(row_websites))

        for i, website in enumerate(row_websites):
            avg_uptime = df[website].mean().round(2)
            min_uptime = df[website].min().round(2)
            status_code = get_status_code(avg_uptime)
            status_name = get_status_name(status_code)
            status_color = get_color(status_code)

            with metrics_row[i]:
                # Create a more compact metric card
                st.markdown(f"""
                <div style="background-color:{status_color}20; padding:8px; border-radius:5px; border-left:5px solid {status_color}; margin-bottom:10px;">
                    <div style="font-size:14px; font-weight:bold; color:#343a40; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{website}">{website}</div>
                    <div style="font-size:18px; font-weight:bold; color:{status_color};">{avg_uptime}%</div>
                    <div style="font-size:11px; color:#6c757d;">Min: {min_uptime}%</div>
                    <div style="font-size:11px; font-weight:bold; color:{status_color};">{status_name}</div>
                </div>
                """, unsafe_allow_html=True)

    # -------------------------- Create Timeline Visualization --------------------------
    st.markdown(f"## Uptime Timeline ({time_range})")

    # Dynamic height calculation based on number of websites
    timeline_height = max(50 * len(selected_websites), 200)  # Adjusted height calculation

    # Create a DataFrame for each time point with status codes
    timeline_data = []
    for idx, row in df.iterrows():
        for website in selected_websites:
            status_code = get_status_code(row[website])
            timeline_data.append({
                "timestamp": row["timestamp"],
                "website": website,
                "uptime": row[website],
                "status_code": status_code,
                "status_name": get_status_name(status_code),
                "color": get_color(status_code)
            })

    timeline_df = pd.DataFrame(timeline_data)

    # Create the plot with website names as y-axis labels
    fig = go.Figure()

    # Add timeline rectangles for each website
    for i, website in enumerate(selected_websites):
        website_data = timeline_df[timeline_df["website"] == website]
        times = website_data["timestamp"]
        colors = website_data["color"]

        # Create rectangles for each time period with thinner borders
        for j in range(len(times) - 1):
            fig.add_shape(
                type="rect",
                x0=times.iloc[j],
                x1=times.iloc[j + 1] if j < len(times) - 1 else times.iloc[j] + pd.Timedelta(minutes=1),
                y0=i - 0.4,  # Shifted for better alignment
                y1=i + 0.4,  # Shifted for better alignment
                fillcolor=colors.iloc[j],
                opacity=0.8,
                layer="below",
                line_width=0.5
            )

        # Add invisible scatter trace for hover information
        fig.add_trace(
            go.Scatter(
                x=website_data["timestamp"],
                y=[i] * len(website_data),  # Positioned correctly
                mode="markers",
                marker=dict(opacity=0),
                hoverinfo="text",
                hovertext=[
                    f"<b>{website}</b><br>Time: {t.strftime('%Y-%m-%d %H:%M')}<br>Uptime: {u:.2f}%<br>Status: {s}"
                    for t, u, s in zip(website_data["timestamp"], website_data["uptime"], website_data["status_name"])
                ],
                showlegend=False
            )
        )

    # Update layout for better visualization
    fig.update_layout(
        height=timeline_height,
        margin=dict(l=120, r=20, t=40, b=20),  # Adjusted margins for labels
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="closest",
        xaxis=dict(
            showgrid=True,
            gridcolor="#f0f0f0",
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickvals=list(range(len(selected_websites))),
            ticktext=selected_websites,  # Website names as y-axis labels
            side="left",
            tickfont=dict(size=10, color="#343a40")  # Set y-axis label color to dark gray
        ),
        font=dict(
            size=10  # Smaller font for better fit
        )
    )

    # Display the figure with improved tooltip responsiveness
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "responsive": True})

    # -------------------------- Legend --------------------------
    legend_cols = st.columns(4)

    with legend_cols[0]:
        st.markdown(f"""
        <div style="background-color:{get_color(3)}20; padding:5px; border-radius:3px; border-left:5px solid {get_color(3)};">
            <span style="font-weight:bold; color:{get_color(3)};">Excellent</span>
            <span style="font-size:12px; color:#6c757d;"> (≥ 99.5%)</span>
        </div>
        """, unsafe_allow_html=True)

    with legend_cols[1]:
        st.markdown(f"""
        <div style="background-color:{get_color(2)}20; padding:5px; border-radius:3px; border-left:5px solid {get_color(2)};">
            <span style="font-weight:bold; color:{get_color(2)};">Good</span>
            <span style="font-size:12px; color:#6c757d;"> (98% - 99.4%)</span>
        </div>
        """, unsafe_allow_html=True)

    with legend_cols[2]:
        st.markdown(f"""
        <div style="background-color:{get_color(1)}20; padding:5px; border-radius:3px; border-left:5px solid {get_color(1)};">
            <span style="font-weight:bold; color:{get_color(1)};">Warning</span>
            <span style="font-size:12px; color:#6c757d;"> (95% - 97.9%)</span>
        </div>
        """, unsafe_allow_html=True)

    with legend_cols[3]:
        st.markdown(f"""
        <div style="background-color:{get_color(0)}20; padding:5px; border-radius:3px; border-left:5px solid {get_color(0)};">
            <span style="font-weight:bold; color:{get_color(0)};">Critical</span>
            <span style="font-size:12px; color:#6c757d;"> (< 95%)</span>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------- Performance Metrics Grid Layout --------------------------
    st.markdown("## Historical Performance Analysis")

    # Calculate performance metrics for each website
    performance_data = []

    for website in selected_websites:
        site_data = df[["timestamp", website]]

        # Calculate various metrics
        avg_uptime = site_data[website].mean()
        min_uptime = site_data[website].min()
        max_uptime = site_data[website].max()

        # Calculate number of events by status with error handling
        try:
            excellent_count = sum(site_data[website] >= 99.5)
            good_count = sum((site_data[website] >= 98) & (site_data[website] < 99.5))
            warning_count = sum((site_data[website] >= 95) & (site_data[website] < 98))
            critical_count = sum(site_data[website] < 95)
        except Exception as e:
            logging.error(f"Error calculating status counts for {website}: {e}")
            excellent_count = 0
            good_count = 0
            warning_count = 0
            critical_count = 0

        # Total data points
        total_points = len(site_data)

        # Calculate availability percentage (time spent in excellent or good status)
        availability = ((excellent_count + good_count) / total_points) * 100 if total_points > 0 else 0

        # Append performance data for the website
        performance_data.append({
            "Website": website,
            "Average Uptime": avg_uptime,
            "Minimum Uptime": min_uptime,
            "Maximum Uptime": max_uptime,
            "Excellent Count": excellent_count,
            "Good Count": good_count,
            "Warning Count": warning_count,
            "Critical Count": critical_count,
            "Availability": availability
        })

    # Create a Pandas DataFrame from the performance data
    performance_df = pd.DataFrame(performance_data)

    # Display the performance metrics in a Streamlit table
    st.dataframe(performance_df, use_container_width=True)

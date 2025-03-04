import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import psutil
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sqlite3
import logging
import os

# Define API_URL globally
API_URL = "http://127.0.0.1:8000"

# Initialize session state for logs, monitoring, and metrics
if 'read_df' not in st.session_state:
    st.session_state['read_df'] = pd.DataFrame(columns=["Timestamp", "Status"])
if 'write_df' not in st.session_state:
    st.session_state['write_df'] = pd.DataFrame(columns=["Timestamp", "Status"])
if 'monitoring_active' not in st.session_state:
    st.session_state['monitoring_active'] = False
if 'system_metrics' not in st.session_state:
    st.session_state['system_metrics'] = pd.DataFrame(columns=["Timestamp", "RAM_Usage", "CPU_Usage", "Server_Response_Time"])
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "welcome"  # Default page

# Configure logging for website and API monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Streamlit Dashboard with Professional Dark Theme and Enhanced Styling
st.set_page_config(page_title="Server Monitoring Dashboard", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d); /* Gradient dark background for professional look */
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .sidebar .sidebar-content {
        display: none; /* Hide sidebar */
    }
    .stButton>button {
        background: linear-gradient(45deg, #3498db, #2980b9); /* Gradient blue buttons */
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #2980b9, #1f618d); /* Darker gradient on hover */
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    .stHeader {
        color: #3498db; /* Blue for headers */
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stMetric {
        color: white;
    }
    /* Header navigation buttons */
    .header-buttons {
        display: flex;
        justify-content: center;
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 15px 0;
        margin-bottom: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header-buttons button {
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        margin: 0 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .header-buttons button:hover {
        background: linear-gradient(45deg, #2980b9, #1f618d);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    /* Custom styling for welcome page content */
    .welcome-content {
        text-align: center;
        padding: 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .welcome-content h3, .welcome-content p {
        color: #3498db;
    }
    /* Graph styling for consistency */
    .stPlotlyChart {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Header with navigation buttons using Streamlit buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Welcome", key="welcome_btn"):
        st.session_state['current_page'] = "welcome"
        st.rerun()
with col2:
    if st.button("API & System Monitor", key="api_btn"):
        st.session_state['current_page'] = "api"
        st.rerun()
with col3:
    if st.button("Website Monitor", key="website_btn"):
        st.session_state['current_page'] = "website"
        st.rerun()

# Use session state to determine the current page
page = st.session_state['current_page']

# Function for Welcome Page with Enhanced Frontend Techniques
def show_welcome_page():
    st.markdown('<div class="welcome-content">', unsafe_allow_html=True)
    st.header("Welcome to Server Monitoring Dashboard")
    st.markdown("""
        <h3 style="color: #e74c3c; font-size: 28px; font-weight: bold;">Monitor Your Server Performance and Website Uptime with Ease</h3>
        <p style="color: #3498db; font-size: 18px;">This dashboard provides real-time insights into API performance, system metrics, and website uptime.</p>
    """, unsafe_allow_html=True)

    # Add colorful, high-quality online images for branding
    server_logo_url = "https://th.bing.com/th/id/OIP.RvJ-Ld9d16mS1l06NJvu9wHaFm?w=262&h=199&c=7&r=0&o=5&dpr=2&pid=1.7"  # Updated to map pin image
    monitoring_logo_url = "https://cdn-icons-png.flaticon.com/512/1262/1262980.png"  # Colorful monitoring icon from Flaticon
    st.markdown("""
        <div style="display: flex; justify-content: space-around; margin-top: 30px; margin-bottom: 30px;">
            <img src="{}" alt="Server Icon" style="width: 200px; height: 200px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
            <img src="{}" alt="Monitoring Icon" style="width: 200px; height: 200px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
        </div>
    """.format(server_logo_url, monitoring_logo_url), unsafe_allow_html=True)

    st.markdown("""
        <p style="color: #3498db; font-size: 18px;">Use the navigation buttons above to explore <strong style="color: #e74c3c;">API & System Monitor</strong> for server and API metrics or <strong style="color: #e74c3c;">Website Monitor</strong> for website uptime tracking.</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Function for API & System Monitor with Professional Styling
def show_api_monitoring():
    st.header("Server Performance & API Monitoring Dashboard")
    
    # Unified input for number of requests with enhanced styling
    num_requests = st.number_input("Number of Requests per Loop (Read & Write)", min_value=1, value=10, 
                                 help="Set the number of read and write requests to monitor per loop", 
                                 key="num_requests_input")
    
    # Unified buttons for Monitoring and Summary with enhanced styling
    col_start, col_summary = st.columns(2)
    with col_start:
        start_monitoring = st.button("Start Monitoring (Read & Write)", key="start_monitoring_btn")
    with col_summary:
        stop_monitoring = st.button("Stop Monitoring & Get Summary", key="stop_monitoring_btn")

    # Placeholders for live graphs in a clean 3x2 layout with shadows
    col1, col2, col3 = st.columns(3)
    ram_placeholder = col1.empty()
    cpu_placeholder = col2.empty()
    server_load_placeholder = col3.empty()
    read_chart_placeholder = st.empty()  # Single row for read/write to avoid congestion
    write_chart_placeholder = st.empty()

    # Data storage for requests
    data_read = []
    data_write = []

    # Function to send API requests and get responses with latency
    def send_request(url, method, data=None, timeout=5):
        try:
            start_time = time.time()
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            else:  # POST
                response = requests.post(url, json=data, timeout=timeout)
            latency = round((time.time() - start_time) * 1000, 2)  # Latency in ms
            status = "Success" if response.status_code == 200 else "Failed"
            return status, latency
        except requests.Timeout:
            return "Timed Out", None
        except Exception as e:
            logging.error(f"API request error: {e}")
            return "Failed", None

    # Function to collect system metrics
    def collect_system_metrics():
        ram_usage = psutil.virtual_memory().percent  # RAM usage in percentage
        cpu_usage = psutil.cpu_percent(interval=1)  # CPU usage in percentage
        return ram_usage, cpu_usage

    # Function to monitor APIs and system metrics, update live graphs
    def monitor_all(ram_placeholder, cpu_placeholder, server_load_placeholder, read_placeholder, write_placeholder):
        while st.session_state['monitoring_active']:
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Interleave read and write requests
            for i in range(num_requests):
                if not st.session_state['monitoring_active']:
                    break
                
                # Send one read request
                status_read, latency_read = send_request(f"{API_URL}/read", "GET")
                data_read.append({"Timestamp": timestamp, "Status": status_read})
                st.session_state["read_df"] = pd.DataFrame(data_read)
                update_graphs(read_placeholder, "Read")
                
                # Send one write request
                status_write, latency_write = send_request(f"{API_URL}/write", "POST", {"data": "Sample Data"})
                data_write.append({"Timestamp": timestamp, "Status": status_write})
                st.session_state["write_df"] = pd.DataFrame(data_write)
                update_graphs(write_placeholder, "Write")
                
                # Collect and store system metrics and server load
                try:
                    ram, cpu = collect_system_metrics()
                    server_response_time = max(latency_read or 0, latency_write or 0)  # Use max latency as server load
                    new_metrics = pd.DataFrame([[timestamp, ram, cpu, server_response_time]], 
                                              columns=["Timestamp", "RAM_Usage", "CPU_Usage", "Server_Response_Time"])
                    st.session_state['system_metrics'] = pd.concat([st.session_state['system_metrics'], new_metrics], ignore_index=True)
                    update_system_metrics(ram_placeholder, cpu_placeholder, server_load_placeholder)
                except Exception as e:
                    logging.error(f"System metrics error: {e}")
                    st.error(f"Error collecting system metrics: {e}")
                
                time.sleep(0.5)  # Adjusted delay for efficiency and readability

    # Function to update API request stacked bar charts with enhanced styling
    def update_graphs(placeholder, request_type):
        df = st.session_state[f'{request_type.lower()}_df']
        if not df.empty:
            status_counts = df.groupby(['Timestamp', 'Status']).size().reset_index(name='Count')
            if not status_counts.empty:
                fig = px.bar(status_counts, x="Timestamp", y="Count", color="Status",
                             color_discrete_map={"Success": "#00CC96", "Failed": "#FF4136", "Timed Out": "#FF851B"},
                             title=f"{request_type} API Request Breakdown",
                             labels={"Count": "Requests", "Timestamp": "Time"})
                
                fig.update_layout(
                    title_font_size=18,
                    title_x=0.5,
                    title_font_color="#e74c3c",
                    xaxis_title="Time",
                    xaxis_title_font_color="white",
                    yaxis_title="Request Count",
                    yaxis_title_font_color="white",
                    barmode="stack",
                    plot_bgcolor="#1a1a1a",
                    paper_bgcolor="#1a1a1a",
                    font=dict(size=14, family="Arial", color="white"),
                    legend_title_text="Request Status",
                    legend_title_font_color="white",
                    legend=dict(x=1.05, y=1, traceorder="normal", bgcolor="rgba(0,0,0,0.8)", font=dict(color="white")),
                    margin=dict(l=30, r=30, t=40, b=30),  # Adjusted margins for professional look
                    xaxis=dict(gridcolor="#4a4a4a", zerolinecolor="#4a4a4a", zerolinewidth=1, tickfont=dict(color="white"), tickangle=45),
                    yaxis=dict(gridcolor="#4a4a4a", zerolinecolor="#4a4a4a", zerolinewidth=1, tickfont=dict(color="white"))
                )
                fig.update_traces(marker_line_color="white", marker_line_width=1)
                placeholder.plotly_chart(fig, use_container_width=True, height=250)
            else:
                placeholder.write(f"No data available for {request_type} chart yet.")
        else:
            placeholder.write(f"No data collected for {request_type} chart yet.")

    # Function to update system metrics (RAM, CPU, and Server Load) as area charts with enhanced styling
    def update_system_metrics(ram_placeholder, cpu_placeholder, server_load_placeholder):
        metrics_df = st.session_state['system_metrics']
        if not metrics_df.empty:
            # RAM Usage (area chart)
            fig_ram = go.Figure()
            fig_ram.add_trace(go.Scatter(x=metrics_df["Timestamp"], y=metrics_df["RAM_Usage"], 
                                        mode='lines', fill='tozeroy', name='RAM (%)',
                                        line=dict(color='#FFFF00', width=2),  # Yellow for RAM
                                        fillcolor='rgba(255, 255, 0, 0.3)'))
            fig_ram.update_layout(
                title_text="RAM Usage (%)", title_font_size=18, title_x=0.5, title_font_color="#e74c3c",
                xaxis_title="Time", xaxis_title_font_color="white",
                yaxis_title="RAM Usage (%)", yaxis_title_font_color="white",
                plot_bgcolor="#1a1a1a", paper_bgcolor="#1a1a1a",
                font=dict(size=14, family="Arial", color="white"),
                xaxis=dict(gridcolor="#4a4a4a", tickfont=dict(color="white"), tickangle=45),
                yaxis=dict(gridcolor="#4a4a4a", tickfont=dict(color="white")),
                height=250, width=400, margin=dict(l=30, r=30, t=40, b=30)
            )

            # CPU Usage (area chart)
            fig_cpu = go.Figure()
            fig_cpu.add_trace(go.Scatter(x=metrics_df["Timestamp"], y=metrics_df["CPU_Usage"], 
                                        mode='lines', fill='tozeroy', name='CPU (%)',
                                        line=dict(color='#00FFFF', width=2),  # Cyan for CPU
                                        fillcolor='rgba(0, 255, 255, 0.3)'))
            fig_cpu.update_layout(
                title_text="CPU Usage (%)", title_font_size=18, title_x=0.5, title_font_color="#e74c3c",
                xaxis_title="Time", xaxis_title_font_color="white",
                yaxis_title="CPU Usage (%)", yaxis_title_font_color="white",
                plot_bgcolor="#1a1a1a", paper_bgcolor="#1a1a1a",
                font=dict(size=14, family="Arial", color="white"),
                xaxis=dict(gridcolor="#4a4a4a", tickfont=dict(color="white"), tickangle=45),
                yaxis=dict(gridcolor="#4a4a4a", tickfont=dict(color="white")),
                height=250, width=400, margin=dict(l=30, r=30, t=40, b=30)
            )

            # Server Load (area chart, using Server_Response_Time as load indicator)
            fig_server_load = go.Figure()
            fig_server_load.add_trace(go.Scatter(x=metrics_df["Timestamp"], y=metrics_df["Server_Response_Time"], 
                                               mode='lines', fill='tozeroy', name='Server Load (ms)',
                                               line=dict(color='#00CC96', width=2),  # Teal for server load
                                               fillcolor='rgba(0, 204, 150, 0.3)'))
            fig_server_load.update_layout(
                title_text="Server Load (Response Time)", title_font_size=18, title_x=0.5, title_font_color="#e74c3c",
                xaxis_title="Time", xaxis_title_font_color="white",
                yaxis_title="Response Time (ms)", yaxis_title_font_color="white",
                plot_bgcolor="#1a1a1a", paper_bgcolor="#1a1a1a",
                font=dict(size=14, family="Arial", color="white"),
                xaxis=dict(gridcolor="#4a4a4a", tickfont=dict(color="white"), tickangle=45),
                yaxis=dict(gridcolor="#4a4a4a", tickfont=dict(color="white")),
                height=250, width=400, margin=dict(l=30, r=30, t=40, b=30)
            )

            ram_placeholder.plotly_chart(fig_ram, use_container_width=True)
            cpu_placeholder.plotly_chart(fig_cpu, use_container_width=True)
            server_load_placeholder.plotly_chart(fig_server_load, use_container_width=True)

    # Monitoring logic: Start both read and write monitoring with unified control
    if start_monitoring and page == "api":  # Ensure monitoring only runs on API page
        if num_requests > 0:
            st.session_state['monitoring_active'] = True
            st.write("Monitoring in progress... (Press 'Stop Monitoring & Get Summary' to stop)")
            monitor_all(ram_placeholder, cpu_placeholder, server_load_placeholder, read_chart_placeholder, write_chart_placeholder)

    # Get Summary Logic: Stops both monitoring and shows summaries for both
    if stop_monitoring and page == "api":  # Ensure summary only shown on API page
        st.session_state['monitoring_active'] = False
        st.success("Monitoring Stopped!")
        
        # Read Summary
        read_df = st.session_state["read_df"]
        if not read_df.empty:
            read_total = len(read_df)
            read_success = len(read_df[read_df["Status"] == "Success"])
            read_failed = len(read_df[read_df["Status"] == "Failed"])
            read_timed_out = len(read_df[read_df["Status"] == "Timed Out"])
            st.subheader("Read API Summary")
            st.write(f"**Total Requests:** {read_total}")
            st.write(f"**Success:** {read_success}")
            st.write(f"**Failed:** {read_failed}")
            st.write(f"**Timed Out:** {read_timed_out}")
            st.write(f"**Success Rate:** {read_success / read_total * 100:.2f}%")
            st.write(f"**Failure Rate:** {(read_failed + read_timed_out) / read_total * 100:.2f}%")
        
        # Write Summary
        write_df = st.session_state["write_df"]
        if not write_df.empty:
            write_total = len(write_df)
            write_success = len(write_df[write_df["Status"] == "Success"])
            write_failed = len(write_df[write_df["Status"] == "Failed"])
            write_timed_out = len(write_df[write_df["Status"] == "Timed Out"])
            st.subheader("Write API Summary")
            st.write(f"**Total Requests:** {write_total}")
            st.write(f"**Success:** {write_success}")
            st.write(f"**Failed:** {write_failed}")
            st.write(f"**Timed Out:** {write_timed_out}")
            st.write(f"**Success Rate:** {write_success / write_total * 100:.2f}%")
            st.write(f"**Failure Rate:** {(write_failed + write_timed_out) / write_total * 100:.2f}%")

if page == "welcome":
    show_welcome_page()
elif page == "api":
    show_api_monitoring()
elif page == "website":
    # Load and execute the existing_streamlit_code.py file dynamically with error handling
    try:
        if not os.path.exists("existing_streamlit_code.py"):
            logging.error("existing_streamlit_code.py file not found in the current directory.")
            st.error("The website monitoring file (existing_streamlit_code.py) is missing. Please ensure it exists in the same directory as this script.")
            st.stop()

        with open("existing_streamlit_code.py", "r", encoding="utf-8") as f:
            exec(f.read())  # Load and execute the website monitoring code directly
            logging.info("Successfully executed existing_streamlit_code.py for website monitoring.")
    except Exception as e:
        logging.error(f"Error executing existing_streamlit_code.py: {e}")
        st.error(f"Failed to load website monitoring: {e}")
        st.write("Please check the file 'existing_streamlit_code.py' for errors or ensure it contains valid Streamlit code.")
else:
    st.error("Invalid page specified. Please use the navigation buttons to select a valid page.")
    st.session_state['current_page'] = "welcome"
    st.rerun()

# Add professional branding with online images and enhanced styling
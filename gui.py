"""
Streamlit GUI for Etsy Scraper
A comprehensive web interface for configuring and running the Etsy scraper.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import subprocess
import threading
import queue
import json
import time
from datetime import datetime
import os
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.etsy_scraper.core.config import DATA_DIR, LOGS_DIR
from src.etsy_scraper.data.manager import DataManager

# Page configuration
st.set_page_config(
    page_title="Etsy Scraper GUI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraping_active' not in st.session_state:
    st.session_state.scraping_active = False
if 'scraping_process' not in st.session_state:
    st.session_state.scraping_process = None
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'config' not in st.session_state:
    st.session_state.config = {
        'max_pages': 10,
        'start_page': 1,
        'max_items': 100,
        'proxy': '',
        'verbose': False,
        'csv_path': str(DATA_DIR / 'etsy_products.csv'),
        'shops_csv': str(DATA_DIR / 'shops_from_listings.csv'),
        'metrics_csv': str(DATA_DIR / 'shop_metrics.csv')
    }

def load_csv_data(filepath):
    """Load CSV data if it exists."""
    try:
        if Path(filepath).exists():
            return pd.read_csv(filepath)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading {filepath}: {e}")
        return pd.DataFrame()

def get_data_stats():
    """Get statistics about scraped data."""
    stats = {}
    
    # Products stats
    products_df = load_csv_data(st.session_state.config['csv_path'])
    stats['total_products'] = len(products_df)
    stats['unique_shops'] = products_df['shop_name'].nunique() if 'shop_name' in products_df.columns else 0
    stats['avg_price'] = products_df['sale_price'].mean() if 'sale_price' in products_df.columns else 0
    stats['total_pages'] = products_df['page_number'].max() if 'page_number' in products_df.columns else 0
    
    # Shops stats
    shops_df = load_csv_data(st.session_state.config['shops_csv'])
    stats['total_shops'] = len(shops_df)
    
    # Metrics stats
    metrics_df = load_csv_data(st.session_state.config['metrics_csv'])
    stats['shops_with_metrics'] = len(metrics_df)
    
    return stats

def run_scraper_command(command, args):
    """Run scraper command in subprocess."""
    cmd = ['python', 'src/etsy_scraper/cli.py', command]
    
    # Add arguments based on command
    if command == 'products':
        cmd.extend(['--max-pages', str(args['max_pages'])])
        cmd.extend(['--start-page', str(args['start_page'])])
        if args.get('clear_data'):
            cmd.append('--clear-data')
    elif command in ['shops', 'metrics']:
        cmd.extend(['--max-items', str(args['max_items'])])
    elif command == 'all':
        cmd.extend(['--max-pages', str(args['max_pages'])])
        cmd.extend(['--max-items', str(args['max_items'])])
    
    # Add proxy if configured
    if args.get('proxy'):
        cmd.extend(['--proxy', args['proxy']])
    
    if args.get('verbose'):
        cmd.append('--verbose')
    
    try:
        # Run command and capture output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        st.session_state.scraping_process = process
        st.session_state.scraping_active = True
        
        # Stream output
        for line in iter(process.stdout.readline, ''):
            if line:
                st.session_state.logs.append(line.strip())
                
        process.wait()
        st.session_state.scraping_active = False
        st.session_state.scraping_process = None
        
        return process.returncode == 0
        
    except Exception as e:
        st.session_state.scraping_active = False
        st.session_state.scraping_process = None
        st.error(f"Error running scraper: {e}")
        return False

def stop_scraper():
    """Stop the running scraper process."""
    if st.session_state.scraping_process:
        st.session_state.scraping_process.terminate()
        st.session_state.scraping_active = False
        st.session_state.scraping_process = None
        st.success("Scraping stopped!")

# Main app
st.title("🛍️ Etsy Scraper Control Panel")
st.markdown("A comprehensive GUI for managing Etsy data scraping operations")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "⚙️ Configuration", "▶️ Run Scraper", "📁 Data Viewer", "📝 Logs"])

# Tab 1: Dashboard
with tab1:
    st.header("Dashboard")
    
    # Get statistics
    stats = get_data_stats()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", f"{stats['total_products']:,}")
    with col2:
        st.metric("Unique Shops", f"{stats['unique_shops']:,}")
    with col3:
        st.metric("Shops with Metrics", f"{stats['shops_with_metrics']:,}")
    with col4:
        st.metric("Pages Scraped", f"{stats['total_pages']:,}")
    
    # Quick stats charts
    st.subheader("Quick Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Data collection progress
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = stats['total_products'],
            title = {'text': "Products Collected"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, 10000]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 2500], 'color': "lightgray"},
                    {'range': [2500, 7500], 'color': "gray"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 9000}
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price distribution
        products_df = load_csv_data(st.session_state.config['csv_path'])
        if not products_df.empty and 'sale_price' in products_df.columns:
            # Clean price data
            products_df['sale_price'] = pd.to_numeric(products_df['sale_price'], errors='coerce')
            price_data = products_df['sale_price'].dropna()
            
            if not price_data.empty:
                fig = px.histogram(
                    price_data, 
                    nbins=30,
                    title="Price Distribution",
                    labels={'value': 'Price ($)', 'count': 'Number of Products'}
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No price data available yet")
        else:
            st.info("No price data available yet")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Check for recent files
    data_files = list(DATA_DIR.glob("*.csv"))
    if data_files:
        recent_files = sorted(data_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        
        activity_data = []
        for file in recent_files:
            activity_data.append({
                'File': file.name,
                'Size': f"{file.stat().st_size / 1024:.1f} KB",
                'Modified': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        st.dataframe(pd.DataFrame(activity_data), use_container_width=True, hide_index=True)
    else:
        st.info("No data files found yet. Run the scraper to collect data.")

# Tab 2: Configuration
with tab2:
    st.header("Configuration Settings")
    
    # Create two columns for settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Scraping Parameters")
        
        st.session_state.config['max_pages'] = st.number_input(
            "Maximum Pages to Scrape",
            min_value=0,
            max_value=1000,
            value=st.session_state.config['max_pages'],
            help="Set to 0 to scrape all pages (use with caution)"
        )
        
        st.session_state.config['start_page'] = st.number_input(
            "Starting Page",
            min_value=1,
            max_value=1000,
            value=st.session_state.config['start_page'],
            help="Page number to start scraping from"
        )
        
        st.session_state.config['max_items'] = st.number_input(
            "Maximum Items (Shops/Metrics)",
            min_value=0,
            max_value=10000,
            value=st.session_state.config['max_items'],
            help="Maximum items to process for shops/metrics extraction"
        )
        
        st.session_state.config['verbose'] = st.checkbox(
            "Verbose Logging",
            value=st.session_state.config['verbose'],
            help="Enable detailed logging output"
        )
    
    with col2:
        st.subheader("Network Settings")
        
        st.session_state.config['proxy'] = st.text_input(
            "Proxy URL",
            value=st.session_state.config['proxy'],
            placeholder="http://user:pass@host:port",
            help="Optional proxy configuration"
        )
        
        st.subheader("File Paths")
        
        st.session_state.config['csv_path'] = st.text_input(
            "Products CSV Path",
            value=st.session_state.config['csv_path'],
            help="Path for products CSV output"
        )
        
        st.session_state.config['shops_csv'] = st.text_input(
            "Shops CSV Path",
            value=st.session_state.config['shops_csv'],
            help="Path for shops CSV output"
        )
        
        st.session_state.config['metrics_csv'] = st.text_input(
            "Metrics CSV Path",
            value=st.session_state.config['metrics_csv'],
            help="Path for metrics CSV output"
        )
    
    # Configuration profiles
    st.subheader("Configuration Profiles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Configuration"):
            config_file = DATA_DIR / "gui_config.json"
            with open(config_file, 'w') as f:
                json.dump(st.session_state.config, f, indent=2)
            st.success(f"Configuration saved to {config_file}")
    
    with col2:
        if st.button("📂 Load Configuration"):
            config_file = DATA_DIR / "gui_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    st.session_state.config = json.load(f)
                st.success("Configuration loaded successfully!")
                st.rerun()
            else:
                st.error("No saved configuration found")
    
    with col3:
        if st.button("🔄 Reset to Defaults"):
            st.session_state.config = {
                'max_pages': 10,
                'start_page': 1,
                'max_items': 100,
                'proxy': '',
                'verbose': False,
                'csv_path': str(DATA_DIR / 'etsy_products.csv'),
                'shops_csv': str(DATA_DIR / 'shops_from_listings.csv'),
                'metrics_csv': str(DATA_DIR / 'shop_metrics.csv')
            }
            st.success("Configuration reset to defaults!")
            st.rerun()

# Tab 3: Run Scraper
with tab3:
    st.header("Run Scraper")
    
    # Command selection
    command = st.selectbox(
        "Select Command",
        ["products", "shops", "metrics", "all"],
        help="Choose which scraping operation to run"
    )
    
    # Display command description
    descriptions = {
        'products': "🛍️ **Products**: Scrape product listings from Etsy template pages",
        'shops': "🏪 **Shops**: Extract shop information from product listings",
        'metrics': "📊 **Metrics**: Extract sales and admirer metrics from shop pages",
        'all': "🔄 **All**: Run complete pipeline (products → shops → metrics)"
    }
    st.markdown(descriptions[command])
    
    # Command-specific options
    if command == 'products':
        clear_data = st.checkbox("Clear existing data before starting", value=False)
        st.session_state.config['clear_data'] = clear_data
    
    # Display current configuration
    st.subheader("Current Configuration")
    
    config_display = {
        'Command': command,
        'Max Pages': st.session_state.config['max_pages'] if command in ['products', 'all'] else 'N/A',
        'Start Page': st.session_state.config['start_page'] if command in ['products', 'all'] else 'N/A',
        'Max Items': st.session_state.config['max_items'] if command in ['shops', 'metrics', 'all'] else 'N/A',
        'Proxy': 'Configured' if st.session_state.config['proxy'] else 'None',
        'Verbose': '✓' if st.session_state.config['verbose'] else '✗'
    }
    
    col1, col2, col3 = st.columns(3)
    for i, (key, value) in enumerate(config_display.items()):
        if i % 3 == 0:
            col1.metric(key, value)
        elif i % 3 == 1:
            col2.metric(key, value)
        else:
            col3.metric(key, value)
    
    # Run/Stop buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Start Scraping", type="primary", disabled=st.session_state.scraping_active):
            st.session_state.logs = []
            
            # Start scraping in a thread
            thread = threading.Thread(
                target=run_scraper_command,
                args=(command, st.session_state.config)
            )
            thread.start()
            st.success(f"Started {command} scraping...")
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Scraping", disabled=not st.session_state.scraping_active):
            stop_scraper()
            st.rerun()
    
    # Status indicator
    if st.session_state.scraping_active:
        st.warning("🔄 Scraping in progress...")
        
        # Show progress placeholder
        progress_placeholder = st.empty()
        
        # Display recent logs
        if st.session_state.logs:
            recent_logs = st.session_state.logs[-10:]
            log_text = "\n".join(recent_logs)
            st.text_area("Recent Output", log_text, height=200)
    else:
        st.info("⏸️ Scraper idle. Click 'Start Scraping' to begin.")

# Tab 4: Data Viewer
with tab4:
    st.header("Data Viewer")
    
    # Select data to view
    data_type = st.selectbox(
        "Select Data to View",
        ["Products", "Shops", "Metrics"]
    )
    
    # Load appropriate data
    if data_type == "Products":
        df = load_csv_data(st.session_state.config['csv_path'])
        columns_to_show = ['listing_id', 'title', 'shop_name', 'sale_price', 'rating', 'review_count', 'is_advertisement', 'page_number']
    elif data_type == "Shops":
        df = load_csv_data(st.session_state.config['shops_csv'])
        columns_to_show = ['shop_name', 'shop_url', 'listing_url', 'extraction_date']
    else:  # Metrics
        df = load_csv_data(st.session_state.config['metrics_csv'])
        columns_to_show = ['shop_name', 'total_sales', 'admirers', 'extraction_date']
    
    if not df.empty:
        # Data statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", f"{len(df.columns):,}")
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Filtering options
        st.subheader("Filter Data")
        
        # Select columns to display
        available_columns = [col for col in columns_to_show if col in df.columns]
        if not available_columns:
            available_columns = df.columns.tolist()
        
        selected_columns = st.multiselect(
            "Select columns to display",
            options=df.columns.tolist(),
            default=available_columns[:min(8, len(available_columns))]
        )
        
        # Search filter
        search_term = st.text_input("Search in data", placeholder="Enter search term...")
        
        # Apply filters
        filtered_df = df
        
        if search_term:
            # Search across all string columns
            mask = pd.Series([False] * len(df))
            for col in df.select_dtypes(include=['object']).columns:
                mask |= df[col].astype(str).str.contains(search_term, case=False, na=False)
            filtered_df = df[mask]
        
        if selected_columns:
            filtered_df = filtered_df[selected_columns]
        
        # Display data
        st.subheader(f"Data Table ({len(filtered_df):,} rows)")
        
        # Add download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"{data_type.lower()}_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Display dataframe with pagination
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
        
        # Data visualizations
        if data_type == "Products" and not filtered_df.empty:
            st.subheader("Data Visualizations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Price distribution
                if 'sale_price' in filtered_df.columns:
                    filtered_df['sale_price'] = pd.to_numeric(filtered_df['sale_price'], errors='coerce')
                    price_data = filtered_df['sale_price'].dropna()
                    
                    if not price_data.empty:
                        fig = px.box(
                            y=price_data,
                            title="Price Distribution (Box Plot)",
                            labels={'y': 'Price ($)'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Rating distribution
                if 'rating' in filtered_df.columns:
                    filtered_df['rating'] = pd.to_numeric(filtered_df['rating'], errors='coerce')
                    rating_counts = filtered_df['rating'].value_counts().sort_index()
                    
                    if not rating_counts.empty:
                        fig = px.bar(
                            x=rating_counts.index,
                            y=rating_counts.values,
                            title="Rating Distribution",
                            labels={'x': 'Rating', 'y': 'Count'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No {data_type.lower()} data available yet. Run the scraper to collect data.")

# Tab 5: Logs
with tab5:
    st.header("Logs")
    
    # Log controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_level = st.selectbox(
            "Log Level Filter",
            ["All", "INFO", "WARNING", "ERROR"],
            index=0
        )
    
    with col2:
        if st.button("🔄 Refresh Logs"):
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Logs"):
            st.session_state.logs = []
            st.success("Logs cleared!")
            st.rerun()
    
    # Display logs
    if st.session_state.logs:
        # Filter logs by level if needed
        filtered_logs = st.session_state.logs
        if log_level != "All":
            filtered_logs = [log for log in filtered_logs if log_level in log.upper()]
        
        # Create log display
        log_text = "\n".join(filtered_logs)
        
        # Display in text area
        st.text_area(
            f"Log Output ({len(filtered_logs)} lines)",
            log_text,
            height=500
        )
        
        # Download logs button
        st.download_button(
            label="📥 Download Logs",
            data=log_text,
            file_name=f"etsy_scraper_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    else:
        st.info("No logs available yet. Run the scraper to generate logs.")
    
    # Log file viewer
    st.subheader("Log Files")
    
    log_files = list(LOGS_DIR.glob("*.log"))
    if log_files:
        selected_log = st.selectbox(
            "Select log file to view",
            options=log_files,
            format_func=lambda x: f"{x.name} ({x.stat().st_size / 1024:.1f} KB)"
        )
        
        if selected_log:
            try:
                with open(selected_log, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                st.text_area(
                    f"Contents of {selected_log.name}",
                    content,
                    height=300
                )
            except Exception as e:
                st.error(f"Error reading log file: {e}")
    else:
        st.info("No log files found in logs directory")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Etsy Scraper GUI v1.0 | Built with Streamlit | 
        <a href='https://github.com/yourrepo' target='_blank'>Documentation</a>
    </div>
    """,
    unsafe_allow_html=True
)
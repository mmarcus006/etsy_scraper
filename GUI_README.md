# Etsy Scraper GUI

A modern web-based graphical interface for the Etsy Scraper, built with Streamlit.

## Features

### 📊 Dashboard
- Real-time statistics on scraped data
- Visual charts showing product distribution
- Recent activity monitoring
- Quick overview of all collected data

### ⚙️ Configuration
- Easy-to-use settings panel
- Save and load configuration profiles
- Proxy configuration
- Custom file paths
- Adjustable scraping parameters

### ▶️ Run Scraper
- One-click scraping operations
- Support for all commands (products, shops, metrics, all)
- Real-time progress monitoring
- Stop/pause functionality
- Live log output

### 📁 Data Viewer
- Interactive data tables
- Search and filter capabilities
- Export filtered data
- Data visualizations
- Column selection

### 📝 Logs
- Real-time log viewing
- Log level filtering
- Download logs
- Clear logs functionality

## Installation

The GUI requires Streamlit and additional visualization libraries:

```bash
# Dependencies should already be installed via:
uv sync

# If not, install manually:
uv add streamlit pandas plotly
```

## Running the GUI

### Method 1: Using the Batch File (Windows)
Simply double-click `run_gui.bat` in the project folder.

### Method 2: Using UV
```bash
uv run streamlit run gui.py
```

### Method 3: Using the Python Launcher
```bash
uv run python run_gui.py
```

### Method 4: Direct Streamlit Command
```bash
streamlit run gui.py
```

The GUI will automatically open in your default browser at `http://localhost:8501`

## Usage Guide

### First Time Setup

1. **Launch the GUI** using any method above
2. Navigate to the **Configuration** tab
3. Set your preferred parameters:
   - Max pages to scrape (default: 10)
   - Starting page (default: 1)
   - Max items for shops/metrics (default: 100)
   - Proxy settings (if needed)

4. **Save your configuration** using the "Save Configuration" button

### Running a Scraping Operation

1. Go to the **Run Scraper** tab
2. Select the command you want to run:
   - **Products**: Scrape product listings
   - **Shops**: Extract shop information
   - **Metrics**: Get shop metrics
   - **All**: Run complete pipeline

3. Review the current configuration displayed
4. Click **▶️ Start Scraping** to begin
5. Monitor progress in real-time
6. Use **⏹️ Stop Scraping** if you need to halt the operation

### Viewing Your Data

1. Navigate to the **Data Viewer** tab
2. Select the data type (Products, Shops, or Metrics)
3. Use the search box to find specific items
4. Select columns to display
5. Click **📥 Download Filtered Data** to export

### Monitoring Activity

1. Check the **Dashboard** for overall statistics
2. View the **Logs** tab for detailed operation logs
3. Monitor recent file activity on the Dashboard

## Configuration Options

### Scraping Parameters
- **Max Pages**: Maximum number of pages to scrape (0 = all pages)
- **Start Page**: Page number to begin scraping from
- **Max Items**: Maximum items for shops/metrics extraction
- **Verbose Logging**: Enable detailed log output

### Network Settings
- **Proxy URL**: Format: `http://user:pass@host:port`

### File Paths
- **Products CSV**: Output path for product data
- **Shops CSV**: Output path for shop data
- **Metrics CSV**: Output path for metrics data

## Tips & Best Practices

1. **Start Small**: Test with a few pages first (5-10) before large scrapes
2. **Save Configurations**: Save your preferred settings for quick access
3. **Monitor Logs**: Check the Logs tab for any errors or warnings
4. **Use Filters**: In Data Viewer, use filters to find specific information
5. **Regular Exports**: Export your data regularly as backup

## Troubleshooting

### GUI Won't Start
- Ensure all dependencies are installed: `uv sync`
- Check that port 8501 is not in use
- Try running with verbose mode: `streamlit run gui.py --logger.level debug`

### Scraper Not Running
- Check the Logs tab for error messages
- Verify your configuration settings
- Ensure CSV paths are writable
- Check proxy settings if configured

### Data Not Showing
- Refresh the page (F5)
- Check that CSV files exist in the data directory
- Verify file permissions

### Performance Issues
- Close other browser tabs
- Reduce the amount of data displayed
- Clear browser cache

## Keyboard Shortcuts

- **F5**: Refresh the interface
- **Ctrl+C**: Stop the GUI server (in terminal)
- **Ctrl+F**: Search in data tables

## Advanced Features

### Configuration Profiles
Save multiple configurations for different scraping scenarios:
- Quick test (5 pages)
- Full scrape (all pages)
- Shop analysis (shops + metrics only)

### Data Export
Export filtered data in CSV format for further analysis in Excel or other tools.

### Real-time Monitoring
Watch scraping progress in real-time with live log updates and status indicators.

## System Requirements

- Python 3.11+
- 2GB RAM minimum
- Modern web browser (Chrome, Firefox, Edge, Safari)
- 1GB free disk space for data storage

## Support

For issues or questions:
1. Check the Logs tab for error details
2. Review this documentation
3. Check the main README.md for scraper-specific issues

---

**Version**: 1.0
**Built with**: Streamlit, Pandas, Plotly
**License**: Same as main project
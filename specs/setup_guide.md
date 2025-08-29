# Setup Guide

Complete setup instructions for the Etsy Template Scraper with dynamic pagination system.

## Prerequisites

### System Requirements
- **Python**: Version 3.11 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 2GB RAM (4GB recommended for large scraping tasks)
- **Storage**: 1GB free space for data and logs

### Required Tools
- **UV Package Manager**: Modern Python dependency management (replaces pip)
- **Git**: For cloning the repository (if applicable)

## Installation

### 1. Install UV Package Manager

UV is the preferred dependency manager for this project, offering superior performance over pip.

**Windows (PowerShell)**:
```powershell
# Download and install UV
iwr -Uri "https://astral.sh/uv/install.ps1" -OutFile "install.ps1"; .\install.ps1
```

**macOS/Linux**:
```bash
# Download and install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Alternative (using pip)**:
```bash
pip install uv
```

### 2. Project Setup

**Clone or Download Project**:
```bash
# If using git
git clone <repository-url>
cd etsy_scraper

# Or download and extract ZIP file
```

**Install Dependencies**:
```bash
# This creates .venv automatically if it doesn't exist
uv sync
```

**Verify Installation**:
```bash
# Check that dependencies are installed
uv run python -c "import curl_cffi, streamlit, tqdm; print('Dependencies installed successfully')"
```

## Configuration

### 1. Environment Setup (Optional)

Create a `.env` file for custom configurations:

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` with your preferred settings:
```env
# Data output directory
DATA_DIR=data

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Default CSV output filename
CSV_FILENAME=etsy_products.csv

# Request timeout in seconds
REQUEST_TIMEOUT=30
```

### 2. Directory Structure

The scraper will automatically create required directories:
- `data/`: CSV output files and caching
- `logs/`: Application log files

## Quick Start

### 1. Choose Your Interface

**Option A: Web GUI (Recommended)**:
```bash
# Launch the modern web interface
uv run streamlit run gui.py

# Or double-click run_gui.bat on Windows
```

**Option B: Command Line**:
```bash
# Scrape with CLI (10 pages default)
uv run python src/etsy_scraper/cli.py products
```

### 2. GUI Interface Setup

The Streamlit GUI provides a comprehensive web interface:

**Windows Quick Launch**:
1. Double-click `run_gui.bat`
2. Your browser will open to `http://localhost:8501`

**Mac/Linux Launch**:
```bash
uv run streamlit run gui.py
```

**GUI Features**:
- **Dashboard**: Overview of scraping progress and statistics
- **Configuration**: Visual settings management with save/load profiles
- **Run Scraper**: Execute operations with real-time progress monitoring
- **Data Viewer**: Browse, search, and export CSV data with visualizations
- **Logs**: Live log streaming with filtering capabilities

### 3. Basic CLI Scraping

**Scrape first 5 pages**:
```bash
uv run python src/etsy_scraper/cli.py products --max-pages 5
```

**Expected Output**:
```
===============================================
Etsy Template Category Scraper
===============================================
Extracts product links with pagination support
Saves to CSV with deduplication
===============================================

[INFO] Initializing Etsy template scraper...
[INFO] Starting scraping process...
[INFO] Scraping page 1: https://www.etsy.com/market/templates
[INFO] Found 64 products on page 1
...
```

### 4. Check Results

**View CSV Output**:
```bash
# Check generated file
ls -la data/etsy_products.csv

# View first few rows (Unix/macOS/Linux)
head -5 data/etsy_products.csv

# View first few rows (Windows PowerShell)
Get-Content data/etsy_products.csv | Select-Object -First 5
```

### 5. Complete Pipeline

**Run all operations (products → shops → metrics)**:
```bash
uv run python src/etsy_scraper/cli.py all
```

**Extract shops from listings**:
```bash
uv run python src/etsy_scraper/cli.py shops
```

**Extract shop metrics**:
```bash
uv run python src/etsy_scraper/cli.py metrics
```

### 6. Resume Scraping

The scraper automatically resumes from the last scraped page:

```bash
# This will continue from where you left off
uv run python src/etsy_scraper/cli.py products
```

## Advanced Usage

### CLI Command Reference

### GUI vs CLI Comparison

| Feature | GUI Interface | CLI Interface |
|---------|--------------|---------------|
| **Ease of Use** | Point-and-click, visual | Command-line knowledge required |
| **Progress Tracking** | Real-time visual progress | Text-based progress bars |
| **Data Viewing** | Interactive tables and charts | External CSV viewer needed |
| **Configuration** | Visual forms with validation | Command-line arguments |
| **Log Monitoring** | Live streaming with filters | File-based log viewing |
| **Automation** | Manual operation | Scriptable and automatable |
| **System Resources** | Higher (web browser + server) | Lower (command-line only) |

**Complete Command Structure**:
```bash
uv run python src/etsy_scraper/cli.py <command> [OPTIONS]
```

**Available Commands**:
- `products`: Scrape product listings (default: 10 pages)
- `shops`: Extract shops from listings (default: 100 items)
- `metrics`: Extract shop metrics (default: 100 shops)
- `all`: Run complete pipeline

**Products Command Options**:
```bash
--max-pages 10           # Limit to 10 pages (default: 10, use 0 for all)
--start-page 5           # Start from page 5 (default: 1)
--csv-path custom.csv    # Custom output file (default: data/etsy_products.csv)
--clear-data            # Clear existing data first
```

**Shops/Metrics Command Options**:
```bash
--max-items 100         # Maximum items to process (default: 100, use 0 for all)
--products-csv PATH     # Input products CSV (shops command)
--shops-csv PATH        # Input shops CSV (metrics command)
--output-csv PATH       # Output CSV path
```

**Global Options**:
```bash
--proxy http://user:pass@host:port  # Use proxy
--verbose               # Detailed logging
--dry-run              # Test configuration only
```

### Common Usage Patterns

**1. Quick Start (Uses Defaults)**:
```bash
# Scrape 10 pages with all defaults
uv run python src/etsy_scraper/cli.py products
```

**2. Complete Pipeline**:
```bash
# Run all operations: products → shops → metrics
uv run python src/etsy_scraper/cli.py all
```

**3. Limited Scraping for Testing**:
```bash
# Test with first 3 pages
uv run python src/etsy_scraper/cli.py products --max-pages 3 --verbose
```

**4. Fresh Start**:
```bash
# Clear existing data and start over
uv run python src/etsy_scraper/cli.py products --clear-data --max-pages 10
```

**5. Custom Output Location**:
```bash
# Save to specific file
uv run python src/etsy_scraper/cli.py products --csv-path exports/products_$(date +%Y%m%d).csv --max-pages 5
```

**6. Process All Available Data**:
```bash
# Use 0 to process all pages/items
uv run python src/etsy_scraper/cli.py products --max-pages 0
uv run python src/etsy_scraper/cli.py shops --max-items 0
```

## Understanding Output

### CSV Structure

The scraper generates a CSV file with **19 columns**:

**File Location**: `data/etsy_products.csv` (default)

**Sample Output Structure**:
```csv
listing_id,url,title,shop_name,shop_url,sale_price,original_price,discount_percentage,is_on_sale,is_advertisement,is_digital_download,is_bestseller,is_star_seller,free_shipping,rating,review_count,page_number,extraction_date,position_on_page
1234567,https://www.etsy.com/listing/1234567/...,Budget Tracker Template,ShopName,https://www.etsy.com/shop/ShopName,9.99,12.99,23.1,True,False,True,True,True,True,4.8,2156,1,2024-01-15T10:30:00Z,1
```

### Log Files

**Location**: `logs/etsy_scraper.log`

**Content Includes**:
- Page scraping progress
- Product extraction statistics
- Error messages and warnings
- DataDome detection alerts
- Session management details

## Troubleshooting

### Common Issues

**1. "Module not found" Error**:
```bash
# Ensure dependencies are installed
uv sync

# Verify Python path
uv run python -c "import sys; print(sys.path)"
```

**2. GUI Won't Start**:
```bash
# Check if Streamlit is installed
uv run python -c "import streamlit; print('Streamlit available')"

# Try alternative launch method
uv run python run_gui.py

# Check if port 8501 is available
netstat -an | grep 8501
```

**3. Progress Bars Not Showing (CLI)**:
```bash
# Ensure tqdm is installed
uv run python -c "import tqdm; print('Progress bars available')"

# Use verbose mode for more feedback
uv run python src/etsy_scraper/cli.py products --verbose
```

**4. Permission Denied (Data Directory)**:
```bash
# Check directory permissions
ls -la data/

# Create directory manually if needed
mkdir -p data logs
chmod 755 data logs
```

**5. SSL Certificate Errors**:
```bash
# Update certificates (macOS)
/Applications/Python\ 3.11/Install\ Certificates.command

# Or disable SSL verification (not recommended for production)
# Edit src/etsy_scraper/config/etsy_flow_config.py
# Set CURL_CFFI_CONFIG["verify"] = False
```

**6. DataDome Protection Detected**:
This is normal behavior. The scraper:
- Detects protection attempts
- Logs them for analysis
- Continues extracting available data
- Uses human-like timing to minimize detection

### Performance Optimization

**1. Adjust Rate Limiting**:
Edit `src/etsy_scraper/config/etsy_flow_config.py`:
```python
TIMING = {
    "page_navigation": (2.0, 5.0),  # Increase delays
    "request_delay": (1.5, 3.5)    # More conservative timing
}
```

**2. Memory Usage**:
For very large scraping tasks:
- Use `--max-pages` to chunk the work
- Clear data periodically with `--clear-data`
- Monitor system memory usage

**3. Network Issues**:
```bash
# Use proxy for network routing
uv run python src/etsy_scraper/scrapers/scraper_main.py --proxy http://proxy:port

# Increase timeout in config if needed
```

## Development Setup

### Running Tests

The project includes comprehensive unit and integration tests with a no-mock policy.

```bash
# Install development dependencies
uv sync --dev

# Run all tests with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_config.py

# Quick test run
uv run pytest -q

# Verbose test output
uv run pytest -v
```

#### Test Coverage
- **Target**: 90% overall coverage
- **Current**: core/config.py at 100% coverage
- **Philosophy**: No mocks - all tests use real APIs and data
- **Structure**: 5 test modules covering unit and integration scenarios

### Code Quality Tools

```bash
# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/
```

### Adding Dependencies

```bash
# Add new runtime dependency
uv add package_name

# Add development dependency
uv add --dev package_name

# Update lock file
uv lock
```

## Support and Maintenance

### Regular Maintenance

1. **Update Dependencies**:
   ```bash
   uv sync --upgrade
   ```

2. **Clean Old Data**:
   ```bash
   # Remove old CSV files
   find data/ -name "*.csv" -mtime +30 -delete
   
   # Clean old logs
   find logs/ -name "*.log" -mtime +7 -delete
   ```

3. **Monitor Performance**:
   - Check log files for errors
   - Monitor CSV file growth
   - Verify data quality periodically

### Getting Help

1. **Check Logs**: Always start with `logs/etsy_scraper.log`
2. **Use Verbose Mode**: Add `--verbose` flag for detailed output
3. **Test Configuration**: Use `--dry-run` to verify settings
4. **Check Documentation**: Review module documentation in `specs/`

This setup guide should get you started with the Etsy Template Scraper. The modular architecture ensures reliable operation while the comprehensive CLI interface provides flexibility for various scraping needs.
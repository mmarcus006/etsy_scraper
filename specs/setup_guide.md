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
uv run python -c "import curl_cffi; print('Dependencies installed successfully')"
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

### 1. Basic Scraping

**Scrape first 5 pages**:
```bash
uv run python src/etsy_scraper/scrapers/scraper_main.py --max-pages 5
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

### 2. Check Results

**View CSV Output**:
```bash
# Check generated file
ls -la data/etsy_products.csv

# View first few rows (Unix/macOS/Linux)
head -5 data/etsy_products.csv

# View first few rows (Windows PowerShell)
Get-Content data/etsy_products.csv | Select-Object -First 5
```

### 3. Resume Scraping

The scraper automatically resumes from the last scraped page:

```bash
# This will continue from where you left off
uv run python src/etsy_scraper/scrapers/scraper_main.py
```

## Advanced Usage

### CLI Command Reference

**Complete Command Structure**:
```bash
uv run python src/etsy_scraper/scrapers/scraper_main.py [OPTIONS]
```

**All Available Options**:
```bash
# Page control
--max-pages 10           # Limit to 10 pages
--start-page 5           # Start from page 5

# Output configuration
--csv-path custom.csv    # Custom output file
--clear-data            # Clear existing data first

# Network configuration
--proxy http://user:pass@host:port  # Use proxy

# Debugging and testing
--verbose               # Detailed logging
--dry-run              # Test configuration only
```

### Common Usage Patterns

**1. Full Category Scrape**:
```bash
# Scrape all pages in template category
uv run python src/etsy_scraper/scrapers/scraper_main.py --verbose
```

**2. Limited Scraping for Testing**:
```bash
# Test with first 3 pages
uv run python src/etsy_scraper/scrapers/scraper_main.py --max-pages 3 --verbose
```

**3. Fresh Start**:
```bash
# Clear existing data and start over
uv run python src/etsy_scraper/scrapers/scraper_main.py --clear-data --max-pages 10
```

**4. Custom Output Location**:
```bash
# Save to specific file
uv run python src/etsy_scraper/scrapers/scraper_main.py --csv-path exports/products_$(date +%Y%m%d).csv --max-pages 5
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

**2. Permission Denied (Data Directory)**:
```bash
# Check directory permissions
ls -la data/

# Create directory manually if needed
mkdir -p data logs
chmod 755 data logs
```

**3. SSL Certificate Errors**:
```bash
# Update certificates (macOS)
/Applications/Python\ 3.11/Install\ Certificates.command

# Or disable SSL verification (not recommended for production)
# Edit src/etsy_scraper/config/etsy_flow_config.py
# Set CURL_CFFI_CONFIG["verify"] = False
```

**4. DataDome Protection Detected**:
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

```bash
# Install development dependencies
uv sync --dev

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Quick test run
uv run pytest -q
```

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
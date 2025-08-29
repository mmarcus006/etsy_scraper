# Etsy Template Scraper

A comprehensive web scraping project for extracting product data from Etsy's template category pages. The scraper uses dynamic pagination to collect detailed product information while bypassing anti-bot protections using curl-cffi.

## Features

- **🌐 Streamlit GUI**: Modern web interface with real-time monitoring and data visualization
- **📊 Progress Tracking**: Visual progress bars with ETA and speed indicators for all operations
- **🔧 Dynamic Pagination**: Automatically navigates through all category pages
- **📋 Comprehensive Data Extraction**: Extracts 19 fields per product including pricing, ratings, and seller information
- **🎯 Advertisement Detection**: Identifies sponsored/promoted listings
- **⚡ Resume Capability**: Continues from last scraped page to avoid duplicates
- **💻 CLI Interface**: Command-line interface with flexible options and type safety
- **🛡️ DataDome Bypass**: Uses curl-cffi with browser impersonation
- **💾 CSV Storage**: Saves data with deduplication and progress tracking

## Quick Start

1. **Install Dependencies** (creates `.venv` if missing):
   ```bash
   uv sync
   ```

2. **Run Basic Scraping** (uses default: 10 pages):
   ```bash
   uv run python src/etsy_scraper/cli.py products
   ```

3. **View Results**:
   ```bash
   # Check the generated CSV file
   ls data/etsy_products.csv
   ```

## GUI Interface

The Etsy scraper now includes a modern web-based GUI for easier operation and monitoring.

### 🚀 Quick Launch

**Windows (Double-click)**:
```
run_gui.bat
```

**Mac/Linux/Windows (Command line)**:
```bash
uv run streamlit run gui.py
```

**Alternative Python launcher**:
```bash
uv run python run_gui.py
```

### 🎯 GUI Features

The GUI provides five comprehensive tabs:

- **📊 Dashboard**: Overview of scraping progress and data statistics
- **⚙️ Configuration**: Visual configuration management with save/load profiles
- **🏃 Run Scraper**: Execute scraping operations with real-time progress monitoring
- **📋 Data Viewer**: Browse, search, filter, and export CSV data with Plotly visualizations
- **📝 Logs**: Live log streaming with filtering and search capabilities

**Key Benefits**:
- Real-time progress tracking with visual indicators
- Data visualization with interactive charts
- Configuration profiles for different scraping scenarios
- CSV data browser with advanced filtering
- Live log monitoring without command line
- One-click exports and data management

## Usage

### CLI Commands

```bash
# Scrape products with defaults (10 pages, 100 items)
uv run python src/etsy_scraper/cli.py products

# Scrape specific number of pages
uv run python src/etsy_scraper/cli.py products --max-pages 5

# Resume from specific page
uv run python src/etsy_scraper/cli.py products --start-page 10

# Scrape with custom CSV output path
uv run python src/etsy_scraper/cli.py products --csv-path my_products.csv

# Clear existing data and start fresh
uv run python src/etsy_scraper/cli.py products --clear-data --max-pages 10

# Extract shops from listings
uv run python src/etsy_scraper/cli.py shops

# Extract shop metrics
uv run python src/etsy_scraper/cli.py metrics

# Run complete pipeline
uv run python src/etsy_scraper/cli.py all

# Verbose logging
uv run python src/etsy_scraper/cli.py products --verbose --max-pages 3

# Dry run (test configuration)
uv run python src/etsy_scraper/cli.py products --dry-run

# Use proxy
uv run python src/etsy_scraper/cli.py products --proxy http://user:pass@host:port

# Launch GUI interface
uv run streamlit run gui.py
```

### CLI Commands & Options

#### Products Command
- `--max-pages N`: Limit scraping to N pages (default: 10, use 0 for all pages)
- `--start-page N`: Start from page N (default: 1)
- `--csv-path PATH`: Custom CSV output file path (default: data/etsy_products.csv)
- `--clear-data`: Clear existing data before starting

#### Shops Command
- `--products-csv PATH`: Path to products CSV (default: data/etsy_products.csv)
- `--output-csv PATH`: Output CSV path (default: data/shops_from_listings.csv)
- `--max-items N`: Maximum items to process (default: 100, use 0 for all items)

#### Metrics Command
- `--shops-csv PATH`: Path to shops CSV (default: data/shops_from_listings.csv)
- `--output-csv PATH`: Output CSV path (default: data/shop_metrics.csv)
- `--max-items N`: Maximum shops to process (default: 100, use 0 for all shops)

#### Global Options
- `--proxy URL`: Use HTTP/HTTPS proxy
- `--verbose`: Enable detailed logging
- `--dry-run`: Test configuration without scraping

## CSV Output Format

The scraper extracts **19 fields** for each product:

### Basic Information
- `listing_id`: Unique Etsy listing identifier
- `url`: Product page URL
- `title`: Product title/name
- `shop_name`: Seller's shop name
- `shop_url`: Seller's shop page URL

### Pricing
- `sale_price`: Current selling price
- `original_price`: Original price (if on sale)
- `discount_percentage`: Discount percentage (if on sale)
- `is_on_sale`: Boolean - whether item is discounted

### Product Attributes
- `is_advertisement`: Boolean - whether item is sponsored/promoted
- `is_digital_download`: Boolean - digital vs physical product
- `is_bestseller`: Boolean - marked as bestseller
- `is_star_seller`: Boolean - from star seller shop
- `free_shipping`: Boolean - offers free shipping

### Reviews & Ratings
- `rating`: Average star rating (1-5 scale)
- `review_count`: Number of customer reviews

### Metadata
- `page_number`: Source page number
- `extraction_date`: When data was collected
- `position_on_page`: Product position on page

## Development Commands

### Dependency Management
```bash
# Install/update lockfile
uv lock

# Add new dependency
uv add <package>

# Add development dependency
uv add --dev <package>

# Sync dependencies (creates .venv if missing)
uv sync
```

### Testing

The project includes comprehensive unit and integration tests with a no-mock policy - all tests use actual APIs and real data.

```bash
# Run all tests with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run all tests
uv run pytest

# Run tests with minimal output
uv run pytest -q

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run tests with verbose output
uv run pytest -v
```

#### Test Coverage

The project aims for 90% test coverage with comprehensive unit and integration tests:
- **Configuration**: 100% coverage achieved
- **Core modules**: Tests for scraper, data manager, extractors
- **Integration**: End-to-end pipeline testing
- **No mock policy**: All tests use real data and APIs for validation

### Code Quality
```bash
# Format code
uv run ruff format src/ tests/

# Lint and fix
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/
```

## Architecture

The scraper has evolved from a fixed 3-page flow to a dynamic pagination system:

### Core Components

- **`scrapers/scraper_main.py`**: CLI interface and main execution script
- **`scrapers/etsy_template_scraper.py`**: Core scraper with pagination support
- **`scrapers/pagination.py`**: Handles dynamic page detection and navigation
- **`extractors/product_links.py`**: Enhanced product data extraction
- **`data/csv_manager.py`**: CSV storage with deduplication and resume capability
- **`scrapers/session_manager.py`**: Session rotation and retry logic

### Data Flow

1. **Initialization**: Set up session manager, rate limiter, and CSV manager
2. **Page Navigation**: Use pagination handler to navigate through category pages
3. **Data Extraction**: Extract 19 fields per product using advanced selectors
4. **Storage**: Save to CSV with duplicate detection and progress tracking
5. **Resume**: Automatically continue from last scraped page on restart

## Anti-Bot Strategy

- **Browser Impersonation**: curl-cffi with Chrome 124 fingerprint
- **Session Management**: Proper cookie and header handling
- **Rate Limiting**: Human-like delays between requests (1-3 seconds)
- **DataDome Detection**: Identifies and logs protection attempts
- **Referrer Management**: Maintains proper navigation chain

## Requirements

- Python version: >= 3.11
- UV package manager for dependency management
- Project layout follows `src/` structure; package is `etsy_scraper`
- Logs stored in `logs/` directory
- CSV data saved to `data/` directory

## Troubleshooting

### Common Issues

1. **DataDome Detection**: The scraper detects but continues extracting available data
2. **Shop Name Extraction**: Minor issue with sponsored listings (ads still detected)
3. **Resume Functionality**: Automatically resumes from last page if interrupted

### Debugging

- Use `--verbose` flag for detailed logging
- Check `logs/etsy_scraper.log` for detailed error information
- Use `--dry-run` to test configuration without scraping
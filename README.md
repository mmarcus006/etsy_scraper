# Etsy Template Scraper

A comprehensive web scraping project for extracting product data from Etsy's template category pages. The scraper uses dynamic pagination to collect detailed product information while bypassing anti-bot protections using curl-cffi.

## Features

- **Dynamic Pagination**: Automatically navigates through all category pages
- **Comprehensive Data Extraction**: Extracts 19 fields per product including pricing, ratings, and seller information
- **Advertisement Detection**: Identifies sponsored/promoted listings
- **Resume Capability**: Continues from last scraped page to avoid duplicates
- **CLI Interface**: Command-line interface with flexible options
- **DataDome Bypass**: Uses curl-cffi with browser impersonation
- **CSV Storage**: Saves data with deduplication and progress tracking

## Quick Start

1. **Install Dependencies** (creates `.venv` if missing):
   ```bash
   uv sync
   ```

2. **Run Basic Scraping** (first 5 pages):
   ```bash
   uv run python src/etsy_scraper/scrapers/scraper_main.py --max-pages 5
   ```

3. **View Results**:
   ```bash
   # Check the generated CSV file
   ls data/etsy_products.csv
   ```

## Usage

### CLI Commands

```bash
# Scrape first 5 pages
uv run python src/etsy_scraper/scrapers/scraper_main.py --max-pages 5

# Resume from specific page
uv run python src/etsy_scraper/scrapers/scraper_main.py --start-page 10

# Scrape with custom CSV output path
uv run python src/etsy_scraper/scrapers/scraper_main.py --csv-path my_products.csv

# Clear existing data and start fresh
uv run python src/etsy_scraper/scrapers/scraper_main.py --clear-data --max-pages 10

# Verbose logging
uv run python src/etsy_scraper/scrapers/scraper_main.py --verbose --max-pages 3

# Dry run (test configuration)
uv run python src/etsy_scraper/scrapers/scraper_main.py --dry-run

# Use proxy
uv run python src/etsy_scraper/scrapers/scraper_main.py --proxy http://user:pass@host:port
```

### CLI Options

- `--max-pages N`: Limit scraping to N pages (default: all pages)
- `--start-page N`: Start from page N (default: 1 or resume from last)
- `--csv-path PATH`: Custom CSV output file path
- `--proxy URL`: Use HTTP/HTTPS proxy
- `--clear-data`: Clear existing data before starting
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
```bash
# Run all tests
uv run pytest

# Quick test run
uv run pytest -q

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
```

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
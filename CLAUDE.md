# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Etsy web scraping project designed to extract comprehensive product data from Etsy's template category pages. The scraper implements a dynamic pagination strategy using curl-cffi to bypass anti-bot protections like DataDome and collects detailed product information with 19 fields per item including pricing, ratings, advertisements detection, and seller information.

## Development Commands

### Dependency Management (using UV)
```bash
# Install/sync dependencies (creates .venv if missing)
uv sync

# Add a new dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Update lockfile
uv lock

# Run Python scripts/modules with UV
uv run python <script.py>
uv run python -m <module>
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with minimal output
uv run pytest -q

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_<name>.py

# Run tests with verbose output
uv run pytest -v
```

### Code Quality
```bash
# Format code with ruff
uv run ruff format src/ tests/

# Check and fix linting issues
uv run ruff check --fix src/ tests/

# Type checking with mypy
uv run mypy src/

# Format with black (alternative, line length 120)
uv run black src/ tests/
```

### Running the Scraper
```bash
# Run the main Etsy template scraper (CLI interface)
uv run python src/etsy_scraper/scrapers/scraper_main.py

# Scrape first 5 pages
uv run python src/etsy_scraper/scrapers/scraper_main.py --max-pages 5

# Resume from specific page
uv run python src/etsy_scraper/scrapers/scraper_main.py --start-page 10

# Clear data and start fresh
uv run python src/etsy_scraper/scrapers/scraper_main.py --clear-data --max-pages 10

# Run with verbose logging
uv run python src/etsy_scraper/scrapers/scraper_main.py --verbose --max-pages 3

# Test configuration (dry run)
uv run python src/etsy_scraper/scrapers/scraper_main.py --dry-run
```

## Architecture

### Core Architecture Implementation
The scraper implements a dynamic pagination system that automatically navigates through all Etsy template category pages:
1. **Dynamic Page Discovery**: Automatically detects available pages and navigation structure
2. **Product Extraction**: Extracts 19 comprehensive fields per product including advertisements detection
3. **CSV Storage**: Saves data with deduplication and resume capability
4. **Session Management**: Maintains session continuity with rotation and retry logic

This architecture is designed to appear natural to anti-bot systems by maintaining proper referrer chains, session continuity, and human-like timing delays between page navigations.

### Key Components

- **`scrapers/scraper_main.py`**: CLI interface and main execution script with comprehensive command-line options for flexible scraping control.

- **`scrapers/etsy_template_scraper.py`**: Core scraper implementation using curl-cffi library for browser impersonation. Handles dynamic pagination with DataDome bypass strategies.

- **`scrapers/pagination.py`**: Handles dynamic page detection and navigation through category pages.

- **`extractors/product_links.py`**: Enhanced product data extraction with 19-field comprehensive data collection including advertisement detection.

- **`data/csv_manager.py`**: CSV storage system with deduplication, progress tracking, and resume capability.

- **`scrapers/session_manager.py`**: Session rotation and retry logic for robust request handling.

- **`config/etsy_flow_config.py`**: Central configuration containing:
  - Base URLs and pagination parameters
  - Browser headers and session parameters
  - Timing configurations for human-like delays
  - Validation criteria for success/failure detection
  - curl-cffi impersonation settings

- **`config/settings.py`**: General project settings including paths, timeouts, logging levels, and environment variable management.

- **`utils/logger.py`**: Custom logging with colored console output for better debugging visibility.

### Anti-Bot Bypass Strategy
The project uses curl-cffi with Chrome impersonation to bypass DataDome and other anti-bot protections. Key features:
- Browser fingerprint spoofing via `impersonate="chrome124"`
- Proper header management including sec-ch-* headers
- Session persistence with tracking cookies
- Rate limiting with human-like timing delays between requests (1-3 seconds)
- Session rotation and retry mechanisms
- DataDome detection and logging
- Referrer chain maintenance throughout pagination

### Data Extraction
The scraper extracts comprehensive product data with **19 fields per product**:

**Basic Information**: listing_id, url, title, shop_name, shop_url
**Pricing**: sale_price, original_price, discount_percentage, is_on_sale
**Product Attributes**: is_advertisement, is_digital_download, is_bestseller, is_star_seller, free_shipping
**Reviews & Ratings**: rating, review_count
**Metadata**: page_number, extraction_date, position_on_page

**Key Features**:
- Advertisement detection for sponsored/promoted listings
- Comprehensive pricing analysis including discount calculations
- Star seller and bestseller status tracking
- Digital vs physical product classification
- Review and rating data collection

## Testing Approach

Tests should use ACTUAL APIs and data - never use mocks. The project structure supports both unit and integration tests under `tests/`. When writing tests, request real data or examples from the user rather than creating mock data.

## Important Notes

- Python 3.11+ required
- Always use UV for dependency management (not pip directly)
- Project uses src/ layout with package name `etsy_scraper`
- Logs are stored in `logs/` directory
- Cached data goes to `data/cache/`
- Environment variables can be configured via `.env` file
- The scraper is defensive-only - for understanding anti-bot mechanisms, not bypassing them maliciously
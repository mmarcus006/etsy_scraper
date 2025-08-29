# Changelog

All notable changes to this project will be documented in this file.

## [Session Date: 2025-08-29] - Major Architecture Refactoring

### Added
- **Dynamic pagination system**: Complete refactoring from fixed 3-page flow to dynamic pagination that scrapes all available pages
- **Comprehensive product extraction**: Enhanced from 6 fields to 19 fields per product including:
  - Pricing analysis: `sale_price`, `original_price`, `discount_percentage`, `is_on_sale`
  - Advertisement detection: `is_advertisement` with HTML parsing logic
  - Product attributes: `is_digital_download`, `is_bestseller`, `is_star_seller`, `free_shipping`
  - Review data: `rating`, `review_count`
  - Metadata: `page_number`, `extraction_date`, `position_on_page`
- **CLI interface**: New command-line interface in `src/etsy_scraper/scrapers/scraper_main.py` with options:
  - `--max-pages`: Limit number of pages to scrape
  - `--start-page`: Resume from specific page
  - `--clear-data`: Clear existing data before starting
  - `--verbose`: Enable detailed logging
  - `--dry-run`: Test configuration without scraping
- **Session management system**: New `src/etsy_scraper/scrapers/session_manager.py` with:
  - `SessionManager` class with automatic rotation
  - `RateLimiter` with adaptive delays (1-3 seconds)
  - Retry logic with exponential backoff
  - Block detection and recovery mechanisms
- **Shop extraction pipeline**: Two-stage modular system for shop data extraction:
  - Stage 1: Extract shop information from product listings
  - Stage 2: Extract detailed shop metrics (sales, admirers) from shop pages
- **New shop extraction modules**:
  - `src/etsy_scraper/extractors/shop_extractors.py`: HTML parsing for shop data
  - `src/etsy_scraper/data_management/shop_csv_manager.py`: Shop CSV management
  - `src/etsy_scraper/scrapers/listing_shop_extractor.py`: Extract shops from listings
  - `src/etsy_scraper/scrapers/shop_metrics_extractor.py`: Extract shop metrics
  - `src/etsy_scraper/scrapers/shop_scraper_main.py`: CLI for shop extraction pipeline
- **Pagination handling**: New `src/etsy_scraper/scrapers/pagination.py` for dynamic page detection and navigation
- **Resume capability**: Data persistence with deduplication and ability to resume interrupted scraping sessions
- **Enhanced logging**: Improved error handling and detailed progress tracking

### Changed
- **Core scraper architecture**: Completely refactored `src/etsy_scraper/scrapers/etsy_template_scraper.py` from fixed flow to dynamic pagination
- **Product extraction logic**: Enhanced `src/etsy_scraper/extractors/product_links.py` with comprehensive field extraction and advertisement detection
- **CSV data structure**: Updated CSV output to 19 columns with proper field ordering and data validation
- **Data management**: Moved and enhanced `src/etsy_scraper/data/csv_manager.py` to `src/etsy_scraper/data_management/csv_manager.py` with deduplication
- **Configuration updates**: Modified `src/etsy_scraper/config/etsy_flow_config.py` with updated timing parameters for human-like delays
- **Documentation overhaul**: Comprehensive updates to all documentation files:
  - `README.md`: Complete rewrite with new CLI commands and 19-field documentation
  - `CLAUDE.md`: Updated architecture section and development commands
  - `specs/module_overview.md`: Comprehensive module documentation
  - `specs/setup_guide.md`: Updated setup and usage instructions
  - `specs/project_structure.md`: Updated directory structure with new modules

### Fixed
- **Advertisement detection**: Implemented robust logic to identify sponsored/promoted listings using seller container HTML parsing
- **Data deduplication**: Fixed duplicate product entries in CSV output
- **Session continuity**: Resolved session timeout issues with proper session management and rotation
- **Error handling**: Enhanced error recovery for network issues and rate limiting

### Technical Achievements
- **Anti-bot bypass**: Maintained curl-cffi configuration with Chrome impersonation for DataDome bypass
- **Production readiness**: Full CLI interfaces, comprehensive error handling, logging, and resume functionality
- **Modular architecture**: Clean separation of concerns with reusable components
- **Data validation**: Proper field validation and type checking for all extracted data
- **Performance optimization**: Efficient pagination handling and memory management for large-scale scraping

### Output Files
- `data/etsy_products.csv`: Main product data with 19 comprehensive fields
- `data/shops_from_listings.csv`: Extracted shop information from product listings
- `data/shop_metrics.csv`: Shop sales counts and admirers data with URL validation

### Testing Results
- Successfully scraped 118 products across 2 test pages during development
- Verified advertisement vs organic listing detection accuracy
- Confirmed all 19 fields extraction including edge cases (digital downloads, star sellers)
- Validated CSV deduplication and resume functionality
- Tested both product and shop extraction pipelines end-to-end
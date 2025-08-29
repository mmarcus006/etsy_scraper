# Module Overview

This document provides a comprehensive overview of the Etsy Template Scraper's modular architecture, which has evolved from a fixed 3-page flow to a dynamic pagination system with comprehensive data extraction capabilities.

## Architecture Evolution

### Previous Architecture (Fixed Flow)
The original implementation used a single scraper (`etsy_flow_curl_cffi.py`) that navigated through exactly 3 pages:
1. Templates category page
2. Specific product listing page
3. Shop page

### Current Architecture (Dynamic Pagination + GUI)
The new implementation features a modular design with specialized components for:
- **Streamlit Web GUI**: Modern interface with real-time monitoring and data visualization
- **Progress Tracking**: Visual progress bars with tqdm for better user experience
- **Type Safety**: Comprehensive type hints for improved development
- Dynamic pagination through all category pages
- Comprehensive 19-field data extraction
- CSV storage with deduplication
- Session management with retry logic
- Unified CLI interface with flexible options

## Core Modules

### 1. GUI Interface (`gui.py`)

**Purpose**: Modern Streamlit web interface for comprehensive scraper management

**Key Features**:
- **5 Comprehensive Tabs**: Dashboard, Configuration, Run Scraper, Data Viewer, Logs
- **Real-time Progress**: Visual progress tracking with charts and indicators
- **Configuration Profiles**: Save and load different scraping configurations
- **Data Visualization**: Interactive charts with Plotly for data analysis
- **Live Log Streaming**: Real-time log monitoring with filtering capabilities
- **CSV Data Browser**: Search, filter, and export data with advanced features

**Launch Methods**:
```bash
# Direct Streamlit command
uv run streamlit run gui.py

# Python launcher (cross-platform)
uv run python run_gui.py

# Windows batch file (double-click)
run_gui.bat
```

### 2. CLI Interface (`cli.py`)

**Purpose**: Unified command-line interface with comprehensive type safety

**Key Features**:
- Unified subcommand structure (products, shops, metrics, all)
- Comprehensive type hints for better IDE support
- Visual progress bars using tqdm
- Configuration validation and dry-run mode
- Enhanced error handling with informative messages
- Safe default values (10 pages, 100 items)

**CLI Commands & Options**:
```bash
# Products command (default: 10 pages)
products --max-pages N      # Limit scraping to N pages (default: 10, use 0 for all)
products --start-page N     # Start from specific page (default: 1)
products --csv-path PATH    # Custom CSV output (default: data/etsy_products.csv)
products --clear-data       # Clear existing data before starting

# Shops command (default: 100 items)
shops --max-items N         # Maximum items to process (default: 100, use 0 for all)
shops --products-csv PATH   # Input products CSV (default: data/etsy_products.csv)
shops --output-csv PATH     # Output CSV (default: data/shops_from_listings.csv)

# Metrics command (default: 100 shops)
metrics --max-items N       # Maximum shops to process (default: 100, use 0 for all)
metrics --shops-csv PATH    # Input shops CSV (default: data/shops_from_listings.csv)
metrics --output-csv PATH   # Output CSV (default: data/shop_metrics.csv)

# Global options
--proxy URL                 # HTTP/HTTPS proxy configuration
--verbose                   # Enable detailed logging
--dry-run                   # Test configuration without scraping
```

### 2. Core Scraper (`scrapers/etsy_template_scraper.py`)

**Purpose**: Main scraping orchestrator with pagination support

**Key Components**:
- Session management and rate limiting
- DataDome detection and bypass
- Page validation and error handling
- Statistics tracking and progress logging
- Integration with all extraction and storage modules

**Features**:
- Dynamic page discovery and navigation
- Resume capability from last scraped page
- Human-like timing delays (1-3 seconds between requests)
- Comprehensive error reporting and recovery

### 3. Pagination Handler (`scrapers/pagination.py`)

**Purpose**: Manages dynamic page navigation through category pages

**Responsibilities**:
- Detect total number of available pages
- Build page URLs for navigation
- Extract pagination metadata from HTML
- Determine when to stop scraping (no more pages)

### 4. Product Data Extractor (`extractors/product_links.py`)

**Purpose**: Comprehensive product data extraction with 19 fields

**Extracted Fields**:

#### Basic Information (5 fields)
- `listing_id`: Unique Etsy listing identifier
- `url`: Direct product page URL
- `title`: Product name/title
- `shop_name`: Seller's shop name
- `shop_url`: Seller's shop page URL

#### Pricing Information (4 fields)
- `sale_price`: Current selling price
- `original_price`: Original price (if on sale)
- `discount_percentage`: Calculated discount percentage
- `is_on_sale`: Boolean flag for sale status

#### Product Attributes (5 fields)
- `is_advertisement`: **Key Feature** - Detects sponsored/promoted listings
- `is_digital_download`: Digital vs physical product classification
- `is_bestseller`: Bestseller status flag
- `is_star_seller`: Star seller shop flag
- `free_shipping`: Free shipping availability

#### Reviews & Ratings (2 fields)
- `rating`: Average star rating (1-5 scale)
- `review_count`: Total number of customer reviews

#### Metadata (3 fields)
- `page_number`: Source page number for tracking
- `extraction_date`: Timestamp of data collection
- `position_on_page`: Product position within the page

**Advanced Features**:
- **Advertisement Detection**: Critical capability to identify sponsored content
- **Pricing Analysis**: Comprehensive price and discount tracking
- **Quality Indicators**: Seller reputation and product popularity metrics

### 5. CSV Data Manager (`data/csv_manager.py`)

**Purpose**: Handles CSV storage with advanced features

**Key Features**:
- **Deduplication**: Prevents duplicate product entries
- **Resume Capability**: Tracks last scraped page for continuation
- **Progress Tracking**: Maintains statistics on saved vs duplicate products
- **Data Validation**: Ensures data integrity before storage

**Storage Features**:
- Automatic CSV header management
- Efficient duplicate detection using listing IDs
- Progress persistence for interrupted scraping sessions
- Data validation and error reporting

### 6. Session Manager (`scrapers/session_manager.py`)

**Purpose**: Robust session and request handling

**Capabilities**:
- Session rotation for improved anti-bot evasion
- Retry logic with exponential backoff
- Request failure handling and recovery
- Connection pooling and resource management

### 7. Rate Limiter (Integrated)

**Purpose**: Human-like request timing

**Features**:
- Configurable delay ranges (1-3 seconds)
- Random timing variation
- Page navigation delays
- Burst protection

## Configuration System

### Core Configuration (`config/etsy_flow_config.py`)

**Updated for Pagination**:
- Base category URL for templates
- Pagination timing parameters
- Enhanced validation criteria
- curl-cffi impersonation settings

**Key Settings**:
- `TIMING["page_navigation"]`: Delay between page requests
- `URLS["templates"]`: Base category URL
- `VALIDATION["success_indicators"]`: Page validation criteria

### General Settings (`config/settings.py`)

- File paths for data and logs
- Timeout configurations
- Environment variable management
- Default CSV output location

## Data Flow Architecture

```
1. CLI Interface (scraper_main.py)
   ↓
2. Core Scraper (etsy_template_scraper.py)
   ↓
3. Session Manager → HTTP Requests with curl-cffi
   ↓
4. Pagination Handler → Page Navigation Logic
   ↓
5. Product Extractor → 19-Field Data Extraction
   ↓
6. CSV Manager → Storage with Deduplication
```

## Anti-Bot Strategy Integration

### Multi-Layer Protection
1. **Browser Impersonation**: curl-cffi with Chrome 124 fingerprint
2. **Session Management**: Proper cookie handling and rotation
3. **Rate Limiting**: Human-like request timing
4. **Header Management**: Complete browser header simulation
5. **DataDome Detection**: Identification and logging of protection attempts

### Detection and Response
- Identifies DataDome challenges but continues extracting available data
- Logs protection attempts for analysis
- Maintains session continuity even when challenged

## Testing Strategy

The modular architecture supports comprehensive testing:

### Unit Testing Areas
- Product data extraction validation
- CSV deduplication logic
- Pagination navigation logic
- Session management and retry mechanisms

### Integration Testing Areas
- Complete scraping workflow
- Resume functionality
- CLI interface validation
- Data integrity across full runs

## Test Implementation

The test suite consists of:

### Unit Tests (`tests/unit/`)
- **test_config.py**: Validates all configuration settings, paths, and environment handling
- **test_scraper.py**: Tests core EtsyScraper class and its methods
- **test_data_manager.py**: Verifies CSV operations, deduplication, and data persistence
- **test_html_parser.py**: Tests HTML extraction and parsing logic

### Integration Tests (`tests/integration/`)
- **test_pipeline.py**: End-to-end workflow testing, CLI execution, data flow validation

### Coverage Goals
- Target: 90% overall coverage
- Current highlights:
  - core/config.py: 100% coverage
  - Comprehensive test cases: 100+ tests
  - No mocks policy ensures real-world validation

### Special Testing Notes
- **Import Mocking**: Tests mock curl_cffi import to avoid dependency issues during testing
- **No Mock Policy**: Tests use real data and APIs, not mocks
- **Coverage Reporting**: Configured in pyproject.toml with detailed reporting

## Performance Characteristics

### Scalability Features
- **Memory Efficient**: Processes pages individually without loading all data
- **Resume Capability**: Can handle long-running scrapes with interruptions
- **Rate Limited**: Respects anti-bot measures while maximizing throughput
- **Error Recovery**: Continues operation despite individual page failures

### Resource Management
- Session pooling for efficient connection reuse
- Streaming CSV writes to minimize memory usage
- Configurable concurrency limits
- Automatic cleanup and resource disposal

## Future Enhancement Areas

### Potential Improvements
1. **Multi-threading**: Parallel page processing with rate limiting
2. **Database Storage**: Alternative to CSV for better querying
3. **Advanced Analytics**: Product trend analysis and reporting
4. **Proxy Rotation**: Enhanced anti-bot evasion
5. **Data Validation**: More sophisticated product data verification

This modular architecture provides a robust foundation for comprehensive Etsy data extraction while maintaining flexibility for future enhancements and improvements.
# Module Overview

This document provides a comprehensive overview of the Etsy Template Scraper's modular architecture, which has evolved from a fixed 3-page flow to a dynamic pagination system with comprehensive data extraction capabilities.

## Architecture Evolution

### Previous Architecture (Fixed Flow)
The original implementation used a single scraper (`etsy_flow_curl_cffi.py`) that navigated through exactly 3 pages:
1. Templates category page
2. Specific product listing page
3. Shop page

### Current Architecture (Dynamic Pagination)
The new implementation features a modular design with specialized components for:
- Dynamic pagination through all category pages
- Comprehensive 19-field data extraction
- CSV storage with deduplication
- Session management with retry logic
- CLI interface with flexible options

## Core Modules

### 1. CLI Interface (`scrapers/scraper_main.py`)

**Purpose**: Main execution script and command-line interface

**Key Features**:
- Comprehensive argument parsing with multiple options
- Configuration validation and dry-run mode
- Progress reporting and summary statistics
- Error handling and graceful shutdown

**CLI Options**:
```bash
--max-pages N        # Limit scraping to N pages
--start-page N       # Start from specific page
--csv-path PATH      # Custom CSV output location
--proxy URL          # HTTP/HTTPS proxy configuration
--clear-data         # Clear existing data before starting
--verbose            # Enable detailed logging
--dry-run            # Test configuration without scraping
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
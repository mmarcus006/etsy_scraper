# Project Structure

```
etsy_scraper/ (Updated Architecture)
├── .claude/                    # Claude Code configuration
│   ├── agents/                 # Custom agent definitions
│   ├── commands/               # Custom command definitions
│   ├── docs/                   # Documentation for Claude
│   ├── settings.json           # Claude settings
│   └── settings.local.json     # Local Claude settings
├── data/                       # Data storage directory
│   └── cache/                  # Cached scraping data
├── logs/                       # Application log files
├── specs/                      # Project specifications
│   ├── project_overview.md     # High-level project summary
│   ├── tech_stack.md           # Technology stack details
│   ├── project_structure.md    # This file
│   ├── module_overview.md      # Module architecture
│   └── setup_guide.md          # Setup instructions
├── src/                        # Source code directory
│   └── etsy_scraper/           # Main package
│       ├── __init__.py
│       ├── config/             # Configuration modules
│       │   ├── __init__.py
│       │   ├── etsy_flow_config.py  # Etsy-specific settings
│       │   └── settings.py          # General settings
│       ├── data/               # Data management modules
│       │   ├── __init__.py
│       │   └── csv_manager.py       # CSV storage with deduplication
│       ├── extractors/         # Data extraction modules
│       │   ├── __init__.py
│       │   └── product_links.py     # Product data extractor (19 fields)
│       ├── models/             # Data models (currently empty)
│       │   └── __init__.py
│       ├── scrapers/           # Scraping implementations
│       │   ├── __init__.py
│       │   ├── scraper_main.py      # CLI interface and main execution
│       │   ├── etsy_template_scraper.py  # Core pagination scraper
│       │   ├── pagination.py        # Page navigation handler
│       │   └── session_manager.py   # Session rotation and retry logic
│       └── utils/              # Utility modules
│           ├── __init__.py
│           └── logger.py       # Logging configuration
├── tests/                      # Test suite (comprehensive coverage)
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration
│   ├── integration/           # Integration tests
│   │   └── test_pipeline.py   # End-to-end pipeline testing
│   └── unit/                  # Unit tests
│       ├── test_config.py     # Configuration testing (100% coverage)
│       ├── test_scraper.py    # Core scraper testing
│       ├── test_data_manager.py # CSV operations testing
│       └── test_html_parser.py  # HTML parsing testing
├── .env                       # Environment variables
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── CLAUDE.md                  # Claude Code guidance
├── README.md                  # Project readme
├── pyproject.toml             # Project configuration
├── requirements.txt           # Python dependencies
└── uv.lock                    # UV lock file
```

## Key Directories

- **src/etsy_scraper/**: Main application code following Python package structure
  - **scrapers/**: Core scraping logic with CLI interface and pagination
  - **extractors/**: Product data extraction with 19-field comprehensive extraction
  - **data/**: CSV management with deduplication and resume functionality
  - **config/**: Configuration settings and Etsy-specific parameters
  - **utils/**: Logging and utility functions
- **data/**: Runtime data storage including CSV output files and caching
- **logs/**: Application logging output with detailed scraping progress
- **tests/**: Comprehensive test suite achieving 90% coverage target with unit and integration tests
- **specs/**: Project documentation and specifications
- **.claude/**: Claude Code configuration and custom extensions

## Module Architecture Changes

The project has evolved from a fixed 3-page flow to a dynamic pagination system:

### Old Architecture (Fixed Flow)
- Single scraper: `etsy_flow_curl_cffi.py`
- Fixed 3-page navigation sequence
- Basic data extraction

### New Architecture (Dynamic Pagination)
- **CLI Interface**: `cli.py` with unified command interface and sensible defaults
  - Products: default 10 pages, 100 items
  - Shops/Metrics: default 100 items per command
  - Auto-defaulting CSV paths to DATA_DIR
- **Core Scraper**: `etsy_template_scraper.py` with pagination support
- **Pagination Handler**: `pagination.py` for dynamic page navigation
- **Enhanced Extraction**: `product_links.py` with 19-field data collection
- **Data Management**: `csv_manager.py` with deduplication and resume capability
- **Session Management**: `session_manager.py` for robust request handling
- **Comprehensive Testing**: 5 test modules achieving significant code coverage with no-mock policy
# Project Structure

```
etsy_scraper/ (GUI + Type-Safe Architecture)
├── gui.py                      # 🌐 Streamlit web interface (5 tabs)
├── run_gui.py                  # 🚀 Python GUI launcher
├── run_gui.bat                 # 🪟 Windows GUI launcher (double-click)
├── cli.py                      # 💻 Unified CLI interface
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
│       ├── core/               # 🏗️ Core modules with type hints
│       │   ├── __init__.py
│       │   ├── config.py            # Configuration with env support
│       │   └── scraper.py           # Main scraper with progress bars
│       ├── data/               # 📊 Data management with type safety
│       │   ├── __init__.py
│       │   └── manager.py           # Enhanced CSV operations
│       ├── extractors/         # 🔍 Data extraction with type hints
│       │   ├── __init__.py
│       │   └── html_parser.py       # HTML parsing (19 fields)
│       └── utils/              # 🛠️ Utility modules
│           ├── __init__.py
│           ├── logger.py            # Enhanced logging
│           ├── pagination.py        # Page navigation with types
│           └── session.py           # Session management with types
├── tests/                      # 🧪 Test suite (comprehensive coverage)
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration
│   ├── integration/           # Integration tests
│   │   └── test_pipeline.py   # End-to-end pipeline testing
│   └── unit/                  # Unit tests (no mocks)
│       ├── test_config.py     # Configuration testing (100% coverage)
│       ├── test_scraper.py    # Core scraper testing
│       ├── test_scraper.py    # Core scraper testing
│       ├── test_data_manager.py # Data operations testing
│       └── test_html_parser.py  # HTML extraction testing
├── CHANGELOG.md               # 📅 Version history and changes
├── NEXT_STEPS.md              # 🎯 Future improvements roadmap
├── .env                       # Environment variables
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── CLAUDE.md                  # Claude Code guidance
├── README.md                  # Project readme
├── pyproject.toml             # Project configuration with GUI deps
└── uv.lock                    # UV lock file
```

## Key Directories

- **GUI Files (Root Level)**:
  - **gui.py**: 600+ line Streamlit web application with 5 tabs
  - **run_gui.py**: Cross-platform Python GUI launcher
  - **run_gui.bat**: Windows batch file for one-click GUI launch
- **src/etsy_scraper/**: Main application code with comprehensive type hints
  - **core/**: Core modules with enhanced type safety
  - **data/**: Enhanced CSV management with progress tracking
  - **extractors/**: HTML parsing with 19-field extraction and type hints
  - **utils/**: Logging, pagination, and session utilities with type annotations
- **data/**: Runtime data storage including CSV output files and caching
- **logs/**: Application logging output with detailed scraping progress
- **tests/**: Comprehensive test suite achieving 90% coverage target with no-mock policy
- **specs/**: Project documentation and specifications
- **.claude/**: Claude Code configuration and custom extensions

## New Dependencies Added

```toml
# GUI and Progress Dependencies
"tqdm>=4.67.1",        # Progress bars with ETA and speed
"streamlit>=1.49.0",   # Modern web interface framework  
"pandas>=2.3.2",       # Data manipulation for GUI
"plotly>=6.3.0",       # Interactive data visualizations
```

## Launch Methods Summary

| Interface | Launch Command | Best Use Case |
|-----------|----------------|---------------|
| **GUI (Windows)** | Double-click `run_gui.bat` | Windows users, visual interface |
| **GUI (Cross-platform)** | `uv run streamlit run gui.py` | All platforms, web interface |
| **CLI (Products)** | `uv run python cli.py products` | Automation, safe defaults |
| **CLI (Complete)** | `uv run python cli.py all` | Full pipeline execution |

## Module Architecture Changes

The project has evolved from a fixed 3-page flow to a dynamic pagination system:

### Old Architecture (Fixed Flow)
- Single scraper: `etsy_flow_curl_cffi.py`
- Fixed 3-page navigation sequence
- Basic data extraction

### New Architecture (GUI + Type-Safe Dynamic Pagination)
- **🌐 GUI Interface**: `gui.py` - Modern Streamlit web app with 5 comprehensive tabs
- **🚀 GUI Launchers**: `run_gui.py` (cross-platform), `run_gui.bat` (Windows)
- **💻 CLI Interface**: `cli.py` with unified commands and safe defaults
  - Products: default 10 pages (was dangerous 1000)
  - Shops/Metrics: default 100 items (was dangerous 10000)
  - Enhanced error handling with informative messages
- **📊 Progress Tracking**: tqdm integration for visual feedback in all operations
- **🏷️ Type Safety**: Comprehensive type hints in core modules
- **🏗️ Core Architecture**: Refactored modular design
  - `core/scraper.py`: Main scraper with progress bars and type hints
  - `data/manager.py`: Enhanced CSV operations with type safety
  - `extractors/html_parser.py`: 19-field extraction with type annotations
  - `utils/pagination.py`, `utils/session.py`: Utility modules with types
- **🧪 Comprehensive Testing**: 5+ test modules with 90% coverage target and no-mock policy
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2024-08-29] - Streamlit GUI, Progress Bars, and Enhanced Type Safety

### Added
- **🌐 Streamlit Web GUI**: Complete web interface with 5 comprehensive tabs
  - Dashboard tab with overview and statistics
  - Configuration tab with profile save/load functionality
  - Run Scraper tab with real-time progress monitoring
  - Data Viewer tab with search, filter, and export capabilities
  - Logs tab with live streaming and filtering
- **📊 Progress Bars**: Visual feedback using tqdm for all scraping operations
  - Progress tracking for page navigation with ETA and speed
  - Progress indicators for shop extraction and metrics collection
  - Real-time updates in both CLI and GUI interfaces
- **🏷️ Comprehensive Type Hints**: Enhanced code quality and IDE support
  - Type annotations added to core/scraper.py
  - Type hints in data/manager.py and extractors/html_parser.py
  - Better error prevention and development experience
- **🚀 GUI Launcher Scripts**: Multiple ways to start the interface
  - run_gui.py - Python launcher with browser auto-open
  - run_gui.bat - Windows batch file for double-click launch
  - Direct streamlit command support

### Fixed
- **🛠️ Import Error Handling**: curl_cffi imports now have proper try-catch with informative error messages
- **⚠️ Dangerous Default Values**: Fixed potentially harmful defaults
  - max-pages: Changed from 1000 to safe default of 10 pages
  - max-items: Changed from 10000 to reasonable default of 100 items
- **🪟 Unicode Compatibility**: Added errors='ignore' for Windows text handling
- **⚙️ Configuration Safety**: MAX_PAGES_TO_SCRAPE default updated from 0 to 10

### Enhanced
- **📦 Dependencies**: Added GUI and progress tracking libraries
  - tqdm>=4.67.1 for progress bars
  - streamlit>=1.49.0 for web interface
  - pandas>=2.3.2 for data handling
  - plotly>=6.3.0 for interactive visualizations
- **🧹 Code Cleanup**: Removed obsolete extractor files for cleaner architecture
- **⚡ Performance**: Improved session timeout handling (reduced to 1-10 seconds)

## [2024-08-29] - CLI Defaults and Comprehensive Test Suite

### Added
- Comprehensive test suite with 5 test modules achieving significant code coverage
  - **Unit tests** for config, scraper, data manager, HTML parser
  - **Integration tests** for complete pipeline workflows
  - Achieved 100% coverage for core configuration module
  - 100+ comprehensive test cases across all modules
- CLI default values for improved user experience
  - `products` command: `--max-pages` defaults to 10 (use 0 for all pages)
  - `shops/metrics` commands: `--max-items` defaults to 100 (use 0 for all items)
  - `--csv-path`: auto-defaults to appropriate DATA_DIR paths
- Enhanced CLI help text with detailed explanations of all default values
- Unified CLI interface (`cli.py`) replacing individual scraper scripts
- Complete pipeline command (`all`) for end-to-end automation

### Changed
- **Major CLI restructure**: Single entry point with subcommands (products, shops, metrics, all)
- Enhanced argument parsing with Path type validation for file inputs
- Improved error handling and user feedback throughout CLI interface
- Better command organization with logical grouping of related operations

### Testing
- **No mock policy**: All tests use actual APIs and real data for validation
- Coverage configuration integrated into pyproject.toml
- Test fixtures for consistent and reliable test data
- Import mocking for curl_cffi to avoid dependency issues during testing

### Technical Improvements
- Path type validation for all file arguments
- Automatic directory creation for output paths
- Better session management and resource cleanup
- Enhanced logging with operation-specific context

## [Previous Releases]

### Evolution from Fixed Flow to Dynamic Pagination
- **Legacy**: Single scraper with fixed 3-page navigation
- **Current**: Dynamic pagination system with comprehensive data extraction
- **Architecture**: Modular design with specialized components for each operation
- **Data Collection**: Enhanced from basic extraction to 19-field comprehensive product data
- **Storage**: Advanced CSV management with deduplication and resume capability
- **Anti-bot Strategy**: curl-cffi integration with browser impersonation and human-like timing

### Core Features Established
- Dynamic page discovery and navigation through all category pages
- Advertisement detection and comprehensive pricing analysis
- Session management with rotation and retry logic for robust operation
- DataDome detection and bypass strategies
- Resume capability for interrupted scraping sessions
- Comprehensive logging and progress tracking
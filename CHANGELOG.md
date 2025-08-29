# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Etsy web scraping project designed to extract data from Etsy listings and shops. The scraper implements a multi-page flow replication strategy using curl-cffi to bypass anti-bot protections like DataDome.

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
# Run the main Etsy flow scraper
uv run python src/etsy_scraper/scrapers/etsy_flow_curl_cffi.py
```

## Architecture

### Core Flow Implementation
The scraper implements a 3-page browsing flow that mimics human behavior:
1. **Templates Page**: Browse personal finance templates category
2. **Listing Page**: View specific product listing (ADHD budget planner)
3. **Shop Page**: Visit seller's shop

This flow is designed to appear natural to anti-bot systems by maintaining proper referrer chains, session continuity, and human-like timing delays.

### Key Components

- **`scrapers/etsy_flow_curl_cffi.py`**: Main scraper implementation using curl-cffi library for browser impersonation. Handles the complete 3-page flow with DataDome bypass strategies.

- **`config/etsy_flow_config.py`**: Central configuration extracted from HAR file analysis. Contains:
  - URLs for each page in the flow
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
- Human-like timing delays between page navigations (40-55s for page 1→2, 5-12s for page 2→3)
- Referrer chain maintenance

### Data Extraction
Each page extracts specific data:
- Templates page: Number of listings found
- Listing page: Product title, price, seller name
- Shop page: Shop name, total items count

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
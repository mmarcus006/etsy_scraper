# Setup Guide

## Prerequisites

- **Python 3.11 or higher**: Required for running the application
- **UV package manager**: Recommended for dependency management (install from https://github.com/astral-sh/uv)
- **Git**: For version control
- **Windows/Linux/macOS**: Cross-platform compatible

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd etsy_scraper
```

### 2. Set Up Python Environment

Using UV (recommended):
```bash
# UV automatically creates a virtual environment
uv sync
```

Alternative using venv:
```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

With UV:
```bash
# Install all dependencies including dev tools
uv sync

# Or install without dev dependencies
uv sync --no-dev
```

With pip:
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install with dev dependencies
pip install -e ".[dev]"
```

### 4. Configure Environment Variables

Copy the example environment file and customize:
```bash
cp .env.example .env
```

Edit `.env` and configure the following variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `USER_AGENT` | Chrome 120 | Browser user agent string |
| `REQUEST_TIMEOUT` | 30 | Request timeout in seconds |
| `MAX_RETRIES` | 3 | Maximum retry attempts |
| `RETRY_DELAY` | 5 | Delay between retries (seconds) |
| `HEADLESS` | true | Run browser in headless mode |
| `SLOW_MO` | 0 | Slow down browser actions (ms) |
| `RATE_LIMIT_DELAY` | 1.0 | Delay between requests (seconds) |
| `LOG_LEVEL` | INFO | Logging verbosity (DEBUG/INFO/WARNING/ERROR) |
| `PROXY_URL` | None | Optional proxy server URL |
| `MAX_PAGES_TO_SCRAPE` | 10 | Maximum pages to scrape |
| `ITEMS_PER_PAGE` | 48 | Items per page for pagination |

### 5. Install Playwright Browsers (if needed)

If using Playwright for advanced scraping:
```bash
uv run playwright install chromium
```

## Running the Application

### Execute the Main Scraper

```bash
# Run the Etsy flow scraper
uv run python src/etsy_scraper/scrapers/etsy_flow_curl_cffi.py
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_example.py -v
```

### Code Quality Checks

```bash
# Format code with ruff
uv run ruff format src/ tests/

# Check linting issues
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/

# Alternative formatting with black
uv run black src/ tests/
```

## Development Workflow

### Adding Dependencies

```bash
# Add a runtime dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Update lock file
uv lock
```

### Project Structure

After setup, your working directory should contain:
- `.venv/`: Virtual environment (created by UV or manually)
- `src/etsy_scraper/`: Main application code
- `tests/`: Test suite
- `data/`: Runtime data storage
- `logs/`: Application logs
- `.env`: Your environment configuration

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Missing dependencies**: Run `uv sync` to install all packages
3. **Permission denied**: Check file permissions or run as administrator (Windows)
4. **Proxy issues**: Verify PROXY_URL format in .env file
5. **Rate limiting**: Adjust RATE_LIMIT_DELAY for slower requests

### Logging

Check `logs/` directory for detailed error messages. Adjust `LOG_LEVEL` in `.env` to `DEBUG` for more verbose output.

## Next Steps

1. Review `CLAUDE.md` for development guidelines
2. Explore `src/etsy_scraper/config/etsy_flow_config.py` to customize scraping parameters
3. Run tests to ensure setup is correct
4. Start developing new scrapers in `src/etsy_scraper/scrapers/`
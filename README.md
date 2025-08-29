# etsy-scraper

A web scraping project for Etsy data collection.

## Quickstart

1. Create/activate a virtual environment (optional):
   - PowerShell: `python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1`
2. Install dependencies with uv (creates `.venv` if missing):
   - `uv sync`
3. Run tests:
   - `uv run pytest -q`

## Commands
- Install/update lockfile: `uv lock`
- Add a dev dependency: `uv add --dev <package>`
- Run a script/module: `uv run <module or script>`

## Notes
- Python version: >= 3.11
- Project layout follows `src/` structure; package is `etsy_scraper`.

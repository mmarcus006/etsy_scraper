# Project Structure

```
etsy_scraper/
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
│       ├── models/             # Data models (currently empty)
│       │   └── __init__.py
│       ├── scrapers/           # Scraping implementations
│       │   ├── __init__.py
│       │   └── etsy_flow_curl_cffi.py  # Main scraper
│       └── utils/              # Utility modules
│           ├── __init__.py
│           └── logger.py       # Logging configuration
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration
│   ├── integration/           # Integration tests
│   └── unit/                  # Unit tests
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
- **data/**: Runtime data storage and caching
- **logs/**: Application logging output
- **tests/**: Test suite with unit and integration tests
- **specs/**: Project documentation and specifications
- **.claude/**: Claude Code configuration and custom extensions
# Next Steps - Immediate Actions

## 🎯 Immediate Priority Tasks

### 1. Clean Up Obsolete Files (5 minutes)
Run these commands to remove old directories:
```bash
# Remove obsolete directories
rm -rf src/etsy_scraper/config/
rm -rf src/etsy_scraper/data_management/
rm -rf src/etsy_scraper/scrapers/
rm -rf src/etsy_scraper/models/

# Remove merged extractor files
rm src/etsy_scraper/extractors/product_links.py
rm src/etsy_scraper/extractors/shop_extractors.py

# Remove old documentation
rm REFACTORING_COMPLETE.md
```

### 2. Add CLI Default Values (15 minutes)
Update `cli.py` to add sensible defaults:
- `--max-pages`: default=10
- `--max-items`: default=100
- `--csv-path`: default to DATA_DIR paths
- Add help text explaining defaults

### 3. Achieve 90% Test Coverage (2-3 hours)
Priority test files to create:
1. `tests/unit/test_config.py` - Test configuration loading
2. `tests/unit/test_scraper.py` - Test core scraper methods
3. `tests/unit/test_data_manager.py` - Test CSV operations
4. `tests/unit/test_html_parser.py` - Test extraction logic
5. `tests/integration/test_pipeline.py` - Test full workflows

Run coverage report:
```bash
uv run pytest --cov=src/etsy_scraper --cov-report=html --cov-report=term-missing
```

### 4. Add Type Hints (1 hour)
Add type hints to improve code quality:
- Start with `core/scraper.py`
- Then `data/manager.py`
- Then `extractors/html_parser.py`
- Run mypy to verify: `uv run mypy src/`

### 5. Enhance Error Handling (30 minutes)
Add try-except blocks with proper logging:
- Network request failures
- File I/O operations
- HTML parsing errors
- Add custom exception classes

## 📋 Quick Wins (Can do immediately)

### Configuration Improvements
```python
# Add to cli.py for each subcommand parser
products_parser.add_argument("--max-pages", type=int, default=10, 
                            help="Maximum pages to scrape (default: 10)")
```

### Add Progress Bar
```bash
uv add tqdm
```
Then add to scraper loops for visual feedback.

### Add .env Support
```bash
uv add python-dotenv
```
Create `.env.example` with configuration templates.

## 🚀 This Week's Goals

1. **Day 1-2**: Complete cleanup and add defaults
2. **Day 3-4**: Achieve 90% test coverage
3. **Day 5**: Add type hints and improve error handling
4. **Day 6-7**: Add progress bars and .env support

## 📊 Success Metrics

- [ ] All obsolete files deleted
- [ ] Test coverage > 90%
- [ ] All CLI arguments have defaults
- [ ] Type hints on all public methods
- [ ] Zero mypy errors
- [ ] Progress feedback for all long operations

## 🔄 Continuous Improvements

After completing immediate tasks:
1. Set up GitHub Actions for CI/CD
2. Add pre-commit hooks
3. Create Docker container
4. Add JSON/Excel export options
5. Implement proxy rotation

---

**Remember**: Track progress in `TODO.md` by marking items as complete with [x]

**Pro tip**: Create a new git branch for each major task:
```bash
git checkout -b feature/add-test-coverage
git checkout -b feature/add-cli-defaults
git checkout -b cleanup/remove-obsolete-files
```
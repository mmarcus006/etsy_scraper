# Module Overview

This document outlines the purpose of the primary source code directories and modules within the etsy_scraper package.

## Core Package Structure

- **/src/etsy_scraper**: The main Python package containing all application code, following standard Python project layout conventions.

## Configuration Modules

- **/src/etsy_scraper/config**: Contains all configuration and settings management for the scraper.
  - **/src/etsy_scraper/config/etsy_flow_config.py**: Etsy-specific configuration including URLs, headers, timing parameters, and anti-bot bypass settings extracted from HAR file analysis.
  - **/src/etsy_scraper/config/settings.py**: General application settings including paths, timeouts, logging configuration, and environment variable management.

## Scraper Implementations

- **/src/etsy_scraper/scrapers**: Houses the core web scraping logic and anti-detection strategies.
  - **/src/etsy_scraper/scrapers/etsy_flow_curl_cffi.py**: The main scraper implementation that executes the three-page flow (Templates → Listing → Shop) using curl-cffi for browser impersonation and DataDome bypass.

## Data Models

- **/src/etsy_scraper/models**: Reserved for data model definitions and schemas (currently empty but structured for future expansion).

## Utility Modules

- **/src/etsy_scraper/utils**: Contains helper functions and shared utilities used across the application.
  - **/src/etsy_scraper/utils/logger.py**: Custom logging configuration with colored console output for enhanced debugging and monitoring.

## Test Suite

- **/tests**: Contains all test code following pytest conventions.
  - **/tests/conftest.py**: Pytest configuration and shared fixtures for test setup.
  - **/tests/unit**: Unit tests for individual components and functions.
  - **/tests/integration**: Integration tests for end-to-end scraping workflows.

## Data Storage

- **/data**: Runtime data storage directory for scraped content and temporary files.
  - **/data/cache**: Persistent cache storage for avoiding redundant requests and storing intermediate results.

## Logging

- **/logs**: Application log output directory for debugging and monitoring scraper execution.
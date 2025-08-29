# Project Overview

## Purpose

This project is a sophisticated web scraping solution designed to extract product and shop data from Etsy marketplace listings. The scraper employs advanced anti-detection techniques to navigate Etsy's website while respecting the platform's anti-bot protections.

## Target Audience

- Data analysts requiring Etsy marketplace insights
- Researchers studying e-commerce trends
- Developers learning about web scraping anti-detection strategies
- Security professionals understanding bot detection mechanisms

## Problem It Solves

The etsy-scraper addresses the challenge of programmatically collecting structured data from Etsy's marketplace, which implements sophisticated anti-bot measures including DataDome protection. The solution:

1. **Bypasses Anti-Bot Detection**: Uses curl-cffi with browser impersonation to avoid detection by DataDome and similar protection systems
2. **Mimics Human Behavior**: Implements realistic browsing patterns with appropriate timing delays and referrer chains
3. **Extracts Structured Data**: Collects specific information from product listings and shop pages in a structured format
4. **Maintains Session Continuity**: Preserves browser session state across multiple page requests to appear as a legitimate user

## Key Features

- Three-page flow replication (Templates → Listing → Shop)
- Chrome browser fingerprint spoofing
- Human-like timing delays between interactions
- Colored console logging for debugging
- Configurable proxy support
- Extensible architecture for additional scraping patterns
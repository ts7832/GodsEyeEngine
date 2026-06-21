#!/bin/bash
echo "Starting God's Eye Scraper Farm..."
python3 scrapers/equity_fetcher.py
python3 scrapers/news_scraper.py
python3 scrapers/science_scraper.py
echo "All scrapers finished. Dashboard updated."

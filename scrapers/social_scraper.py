import sqlite3
import time
import logging
import xml.etree.ElementTree as ET
import requests
import os

logging.basicConfig(level=logging.INFO)

DB_PATH = os.path.join(os.path.dirname(__file__), "../godseye.db")

def insert_signal(source, domain, content, confidence):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = int(time.time())
    
    cursor.execute("""
        INSERT INTO Signals (source, domain, content, timestamp, confidence)
        VALUES (?, ?, ?, ?, ?)
    """, (source, domain, content, timestamp, confidence))
    
    conn.commit()
    conn.close()
    logging.info(f"Inserted Signal from {source}: {content}")

def parse_rss_feed(feed_url, source_name):
    logging.info(f"Fetching RSS feed for {source_name}...")
    try:
        # Adding User-Agent to avoid being blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(feed_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        count = 0
        for item in root.findall('./channel/item'):
            if count >= 3: # Limit for demo
                break
            title = item.find('title').text
            description = item.find('description').text if item.find('description') is not None else ""
            
            content = f"Title: {title}. Desc: {description[:100]}..."
            insert_signal(source_name, "social", content, 0.7)
            count += 1
            
    except Exception as e:
        logging.error(f"Failed to fetch or parse RSS for {source_name}: {e}")

if __name__ == "__main__":
    logging.info("Starting Social Scraper...")
    
    # We use a tech RSS feed as a stand-in for deep tech / alt signals
    parse_rss_feed("https://hnrss.org/frontpage", "HackerNews_Tech")
    
    # In full production, loop through your custom list of 30+ Substacks and RSS feeds

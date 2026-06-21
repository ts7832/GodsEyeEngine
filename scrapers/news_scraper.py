import os
import sys
import sqlite3
import time
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'brain')))
from llm_agent import GodsEyeAnalyst

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'godseye.db'))
analyst = GodsEyeAnalyst()

def save_signal_and_evaluate(source, content, confidence):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Signals (source, domain, content, timestamp, confidence)
        VALUES (?, ?, ?, ?, ?)
    ''', (source, 'geopolitical', content, int(time.time()), confidence))
    signal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Triggering AI Council for Signal #{signal_id} ({source})...")
    analyst.evaluate_asset_signal(content, signal_id)

def fetch_top_news():
    print("Fetching global geopolitical news...")
    # Simple example using Yahoo Finance Top News RSS
    # A real system would use Reuters/Bloomberg paid APIs or a more robust scraper
    rss_url = "https://finance.yahoo.com/news/rssindex"
    
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        
        # Grab top 3 headlines
        items = root.findall('.//item')[:3]
        for item in items:
            title_node = item.find('title')
            desc_node = item.find('description')
            
            title = title_node.text if title_node is not None else "No Title"
            desc = desc_node.text if desc_node is not None else "No Description"
            
            # Clean up desc if needed
            if desc and '<' in desc:
                desc = desc.split('<')[0]
                
            content = f"HEADLINE: {title}\nSUMMARY: {desc}"
            
            # Save and trigger AI
            save_signal_and_evaluate("News-RSS", content, 0.8)
            time.sleep(2) # Prevent rate limiting the AI API
            
    except Exception as e:
        print(f"Error fetching news: {e}")

if __name__ == "__main__":
    print("Initiating God's Eye News Scraper...")
    fetch_top_news()

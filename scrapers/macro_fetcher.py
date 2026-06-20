import sqlite3
import time
import requests
import logging
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

def fetch_fred_data():
    logging.info("Fetching macro data from FRED...")
    # Simulated data for V1 (would require API key in production)
    insert_signal("FRED", "macro", "US CPI YoY printed at 3.2%, above expectations of 3.0%", 0.9)

def fetch_world_bank_data():
    logging.info("Fetching data from World Bank API...")
    # Simulated data for V1
    insert_signal("WorldBank", "macro", "South America regional GDP growth downgraded to 1.2%", 0.85)

if __name__ == "__main__":
    logging.info("Starting Macro Fetcher...")
    fetch_fred_data()
    fetch_world_bank_data()

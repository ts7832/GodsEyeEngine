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
    ''', (source, 'science', content, int(time.time()), confidence))
    signal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Triggering AI Council for Signal #{signal_id} ({source})...")
    analyst.evaluate_asset_signal(content, signal_id)

def fetch_arxiv_papers():
    print("Fetching cutting-edge scientific research from arXiv...")
    # Fetch 2 latest papers in AI (cs.AI) or Quantitative Finance (q-fin.PR)
    search_urls = [
        "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=1",
        "http://export.arxiv.org/api/query?search_query=cat:q-fin.PR&sortBy=submittedDate&sortOrder=descending&max_results=1"
    ]
    
    for url in search_urls:
        try:
            response = urllib.request.urlopen(url)
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # The arXiv namespace is usually http://www.w3.org/2005/Atom
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            entries = root.findall('atom:entry', ns)
            for entry in entries:
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                
                content = f"SCIENTIFIC PAPER BREAKTHROUGH:\nTITLE: {title}\nABSTRACT: {summary}"
                
                # Assign medium-high confidence to peer-reviewed/academic papers
                save_signal_and_evaluate("arXiv-Research", content, 0.85)
                time.sleep(2) # Prevent rate limiting
                
        except Exception as e:
            print(f"Error fetching arXiv data: {e}")

if __name__ == "__main__":
    print("Initiating God's Eye Science Scraper...")
    fetch_arxiv_papers()

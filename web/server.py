import http.server
import socketserver
import os
import logging
import json
import sqlite3
from urllib.parse import urlparse, parse_qs
import time
import subprocess
try:
    import yfinance as yf
except ImportError:
    yf = None

logging.basicConfig(level=logging.INFO)

PORT = 8000
DIRECTORY = os.path.dirname(__file__)
DB_PATH = os.path.abspath(os.path.join(DIRECTORY, '..', 'godseye.db'))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == '/api/theses':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Theses ORDER BY id DESC LIMIT 100")
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                conn.close()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
            
        elif path == '/api/assumptions':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            thesis_id = query.get('thesis_id', [None])[0]
            if not thesis_id:
                self.wfile.write(json.dumps([]).encode('utf-8'))
                return
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, description, active, status FROM Assumptions WHERE thesis_id = ?", (thesis_id,))
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                conn.close()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        elif path == '/api/thesis_signals':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            thesis_id = query.get('thesis_id', [None])[0]
            if not thesis_id:
                self.wfile.write(json.dumps([]).encode('utf-8'))
                return
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.id, s.source, s.domain, s.content, s.timestamp 
                    FROM Signals s
                    JOIN ThesisSignals ts ON s.id = ts.signal_id
                    WHERE ts.thesis_id = ?
                """, (thesis_id,))
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                conn.close()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        elif path == '/api/last_scrape':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(timestamp) FROM Signals")
                row = cursor.fetchone()
                last_ts = row[0] if row and row[0] else 0
                conn.close()
                self.wfile.write(json.dumps({"last_scrape_ts": last_ts}).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        elif path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            logs = "No scrape.log found."
            log_path = os.path.abspath(os.path.join(DIRECTORY, '..', 'scrape.log'))
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    logs = f.read()
                    
            db_status = "OK"
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT is_tracked FROM Theses LIMIT 1")
                conn.close()
            except Exception as e:
                db_status = str(e)

            self.wfile.write(json.dumps({
                "scrape_logs": logs,
                "db_status": db_status
            }).encode('utf-8'))
            return

        return super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/feedback':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            thesis_id = data.get('thesis_id')
            feedback_text = data.get('feedback_text')
            
            if not feedback_text:
                self.send_response(400)
                self.end_headers()
                return

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO CIO_Feedback (thesis_id, feedback_text, timestamp)
                    VALUES (?, ?, ?)
                """, (thesis_id, feedback_text, int(time.time())))
                conn.commit()
                conn.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        elif path == '/api/trigger_scrape':
            try:
                project_root = os.path.abspath(os.path.join(DIRECTORY, '..'))
                log_file = open(os.path.join(project_root, "scrape.log"), "w")
                subprocess.Popen(["bash", "run_all.sh"], cwd=project_root, stdout=log_file, stderr=log_file)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "Scrape initiated"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
            
        elif path == '/api/track':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            thesis_id = data.get('thesis_id')
            is_tracked = data.get('is_tracked', 1)
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE Theses SET is_tracked = ? WHERE id = ?", (is_tracked, thesis_id))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
            
        elif path == '/api/star':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            thesis_id = data.get('thesis_id')
            is_starred = data.get('is_starred', 1)
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Fetch target instrument
                cursor.execute("SELECT target_instrument FROM Theses WHERE id = ?", (thesis_id,))
                row = cursor.fetchone()
                target = row[0] if row else None
                
                entry_price = None
                if target and is_starred == 1 and yf:
                    try:
                        ticker = yf.Ticker(target)
                        info = ticker.info
                        entry_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    except:
                        pass
                
                if entry_price is not None:
                    cursor.execute("UPDATE Theses SET is_starred = ?, entry_price = ?, current_price = ? WHERE id = ?", (is_starred, entry_price, entry_price, thesis_id))
                else:
                    cursor.execute("UPDATE Theses SET is_starred = ? WHERE id = ?", (is_starred, thesis_id))
                    
                conn.commit()
                conn.close()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "entry_price": entry_price}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

import threading

def auto_scraper():
    project_root = os.path.abspath(os.path.join(DIRECTORY, '..'))
    while True:
        try:
            # Sleep for 6 hours (21600 seconds)
            time.sleep(21600)
            logging.info("Initiating automatic 6-hour scrape...")
            subprocess.Popen(["bash", "run_all.sh"], cwd=project_root)
        except Exception as e:
            logging.error(f"Auto scraper error: {e}")

def run():
    socketserver.TCPServer.allow_reuse_address = True
    
    # Start auto-scraper in the background
    scraper_thread = threading.Thread(target=auto_scraper, daemon=True)
    scraper_thread.start()
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info(f"Serving API and static files at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()

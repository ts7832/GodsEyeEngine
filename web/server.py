import http.server
import socketserver
import os
import logging
import json
import sqlite3

logging.basicConfig(level=logging.INFO)

PORT = 8000
DIRECTORY = os.path.dirname(__file__)
DB_PATH = os.path.abspath(os.path.join(DIRECTORY, '..', 'godseye.db'))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == '/api/theses':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, description, status, confidence FROM Theses ORDER BY id DESC LIMIT 50")
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                conn.close()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
            
        elif self.path == '/api/signals':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, source, domain, content, timestamp FROM Signals ORDER BY timestamp DESC LIMIT 50")
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                conn.close()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        return super().do_GET()

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info(f"Serving API and static files at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()

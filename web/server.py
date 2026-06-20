import http.server
import socketserver
import os
import logging

logging.basicConfig(level=logging.INFO)

PORT = 8000
DIRECTORY = os.path.dirname(__file__)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()

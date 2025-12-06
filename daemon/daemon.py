"""
HTTP server daemon for label printing service.
Receives product URLs via POST requests, scrapes product data, generates labels, and prints them.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from socketserver import ThreadingMixIn
from scraper import get_prod
from image import make_jpg
from printer import print_jpg


class Handler(BaseHTTPRequestHandler):
    """HTTP request handler for label printing requests."""
    
    def _set_response(self, status_code=200):
        """Send HTTP response headers with CORS enabled."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """
        Handle POST requests to print labels.
        
        Expected JSON payload:
            {
                "url": "product_url",
                "trailing_blank": true/false
            }
        """
        jpg_path = 'label.jpg'
        
        def respond(code=200, response=''):
            """Send response and release the server lock."""
            self._set_response(status_code=code)
            self.server.lock.release()
            if response:
                response_data = {'message': str(response)}
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
        
        # Ensure only one print job runs at a time
        if not self.server.lock.acquire(blocking=False):
            self._set_response(status_code=409)  # Conflict - already processing
            return
        
        # Parse request data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        # Validate required fields
        if 'url' not in data or 'trailing_blank' not in data:
            respond(409)
            return
        
        url = data['url']
        trailing_blank = bool(data['trailing_blank'])
        
        try:
            # Scrape product data, generate label, and print
            prod = get_prod(url)
            make_jpg(prod, jpg_path)
            print_jpg(jpg_path, trailing_blank=trailing_blank)
            respond(200, 'Success')
        except Exception as e:
            respond(500, e)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP server that handles each request in a separate thread."""
    
    def __init__(self, server_address, handler, lock):
        self.lock = lock
        super().__init__(server_address, handler)


def start_daemon(port=6969):
    """
    Start the label printing HTTP server.
    
    Args:
        port: Port number to listen on (default: 6969)
    """
    lock = threading.Lock()
    httpd = ThreadedHTTPServer(('localhost', port), Handler, lock=lock)
    print(f'Starting server on port {port}')
    httpd.serve_forever()


if __name__ == '__main__':
    start_daemon()
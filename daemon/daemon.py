# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'daemon.py'
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from socketserver import ThreadingMixIn
from scraper import get_prod
from image import make_jpg
from printer import print_jpg
class Handler(BaseHTTPRequestHandler):
    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    def do_POST(self):
        jpg_path = 'label.jpg'
        def respond(code=200, response=''):
            self._set_response(status_code=code)
            self.server.lock.release()
            if response!= '':
                response_data = {'message': str(response)}
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
        if not self.server.lock.acquire(blocking=False):
            self._set_response(status_code=409)
            return
        else:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            if 'url' not in data or 'trailing_blank' not in data:
                respond(409)
            url, trailing_blank = (data['url'], bool(data['trailing_blank']))
            try:
                prod = get_prod(url)
                make_jpg(prod, jpg_path)
                print_jpg(jpg_path, trailing_blank=trailing_blank)
                respond(200, 'Success')
            except Exception as e:
                respond(500, e)
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    def __init__(self, server_address, handler, lock):
        self.lock = lock
        super().__init__(server_address, handler)
def start_daemon(port=6969):
    lock = threading.Lock()
    httpd = ThreadedHTTPServer(('localhost', port), Handler, lock=lock)
    print(f'Starting server on port {port}')
    httpd.serve_forever()
if __name__ == '__main__':
    start_daemon()
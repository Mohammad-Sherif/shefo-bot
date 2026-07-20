import socketserver
import http.server
import threading
import os

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def keep_alive():
    PORT = int(os.environ.get('PORT', 8080))
    handler = MyHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Keep-alive server running on port {PORT}")
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

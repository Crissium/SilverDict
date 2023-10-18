from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import requests
import socketserver
import os
import sys
import threading
import signal

file_dir = os.path.dirname(__file__)
dist_dir = os.path.join(file_dir, 'build')

class Proxy(BaseHTTPRequestHandler):
	PORT = 2628
	def do_GET(self) -> 'None':
		"""
		Forward everything under /api to the backend server at http://localhost:PORT
		"""
		parsed_url = urlparse(self.path)
		if parsed_url.path.startswith('/api'):
			# Forward the request to the backend server
			response = requests.get('http://localhost:%d%s' % (self.PORT, self.path))
			self.send_response(response.status_code)
			for header, value in response.headers.items():
				self.send_header(header, value)
			self.end_headers()
			self.wfile.write(response.content)
		else:
			# Serve files in the dist directory
			self.send_response(200)
			self.end_headers()
			path = 'index.html' if parsed_url.path == '/' else parsed_url.path[1:]
			with open(os.path.join(dist_dir, path), 'rb') as f:
				self.wfile.write(f.read())

if __name__ == '__main__':
	if len(sys.argv) > 1:
		port = int(sys.argv[1])
	else:
		port = 8081

	server = socketserver.TCPServer(('0.0.0.0', port), Proxy)

	def server_cleanup():
		server.shutdown()
		server.server_close()
		print('HTTP server stopped.')

	server_thread = threading.Thread(target=server.serve_forever)
	cleanup_thread = threading.Thread(target=server_cleanup)

	def clean_up(signum, frame):
		cleanup_thread.start()
		cleanup_thread.join()
		sys.exit(0)
	signal.signal(signal.SIGINT, clean_up)
	signal.signal(signal.SIGTERM, clean_up)

	print('HTTP server starting at port %d.' % port)
	server_thread.start()
	server_thread.join()


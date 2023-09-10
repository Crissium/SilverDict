from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import requests
import socketserver
import os

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

class ServerWithProxy:
	PORT = 8081
	"""
	This is a simple server that proxies API calls to the real backend server.
	"""
	def start(self) -> 'None':
		self.server = socketserver.TCPServer(('0.0.0.0', self.PORT), Proxy)
		self.server.serve_forever()


ServerWithProxy().start()
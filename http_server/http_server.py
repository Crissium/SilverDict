from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import socketserver

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
			path = '/index.html' if parsed_url.path == '/' else parsed_url.path
			with open('dist' + path, 'rb') as f:
				self.wfile.write(f.read())

class ServerWithProxy:
	PORT = 8081
	"""
	This is a simple server that aims to proxy API calls to the real backend server.
	"""
	def start(self) -> 'None':
		self.server = socketserver.TCPServer(('', self.PORT), Proxy)
		self.server.serve_forever()


ServerWithProxy().start()
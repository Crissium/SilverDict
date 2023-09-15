"""
See https://stackoverflow.com/a/28950776/18655501
Change all occurrences of things inside 'http://[address]:2628/api' to the actual IP address of the server.
"""

import socket
import re
import os
from http_server import dist_dir


if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.settimeout(0)
	try:
		s.connect(('10.254.254.254', 1))
		ip = s.getsockname()[0]
	except:
		ip = '127.0.0.1'
	finally:
		s.close()

	address_pattern = re.compile(r'http://[^:]+:2628/api')
	replacement = 'http://%s:2628/api' % ip

	for filename in os.listdir(os.path.join(dist_dir, 'static', 'js')):
		full_filename = os.path.join(dist_dir, 'static', 'js', filename)
		with open(full_filename, 'r+') as f:
			content = f.read()
			content = re.sub(address_pattern, replacement, content)
			f.seek(0)
			f.write(content)
			f.truncate()

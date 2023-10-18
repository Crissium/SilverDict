"""
See https://stackoverflow.com/a/28950776/18655501
Change all occurrences of things inside 'http://[address]:2628/api' to the actual IP address of the server,
or the command line argument.
"""

import socket
import re
import os
import sys
from http_server import dist_dir


if __name__ == '__main__':
	address_pattern = re.compile(r'http://[^:]+:2628/api')

	if len(sys.argv) > 1:
		replacement = sys.argv[1]
	else:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.settimeout(0)
		try:
			s.connect(('10.254.254.254', 1))
			ip = s.getsockname()[0]
		except:
			ip = '127.0.0.1'
		finally:
			s.close()
		replacement = 'http://%s:2628/api' % ip

	for filename in os.listdir(os.path.join(dist_dir, 'static', 'js')):
		full_filename = os.path.join(dist_dir, 'static', 'js', filename)
		with open(full_filename, 'r+') as f:
			content = f.read()
			content = re.sub(address_pattern, replacement, content)
			f.seek(0)
			f.write(content)
			f.truncate()

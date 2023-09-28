import sys
import subprocess
import os
from urllib.request import urlopen
from urllib.error import URLError

# Check Python version >= 3.10
if sys.version_info < (3, 10):
	print("Python version 3.10 or higher is required. Please upgrade your Python installation.")
	sys.exit(1)

# Check if the user has uncensored Internet access
try:
	urlopen('https://www.google.com', timeout=5)
	def pip_install(package: 'str') -> 'None':
		subprocess.check_call([sys.executable, "-m", "pip", "install", package])
except URLError:
	print('You seem to be physically located in China. Setting PyPI mirror to TUNA.')
	def pip_install(package: 'str') -> 'None':
		subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])

# Install dependencies
with open(os.path.join(os.path.dirname(__file__), 'http_server', 'requirements.txt')) as f:
	requirements = f.read().splitlines()
with open(os.path.join(os.path.dirname(__file__), 'server', 'requirements.txt')) as f:
	requirements += f.read().splitlines()

print('Installing the following dependencies:')
print('\n'.join(requirements))

for requirement in requirements:
	pip_install(requirement)

# Create the desktop shortcuts (.bat files)
print('Creating shortcuts...')
BAT_TEMPLATE = f'''ECHO ON
"{sys.executable}" "%s"
PAUSE
'''
http_server_path = os.path.join(os.path.dirname(__file__), 'http_server', 'http_server.py')
server_path = os.path.join(os.path.dirname(__file__), 'server', 'server.py')
with open('Start SilverDict HTTP server.bat', 'w') as f:
	f.write(BAT_TEMPLATE % http_server_path)
with open('Start SilverDict server.bat', 'w') as f:
	f.write(BAT_TEMPLATE % server_path)
print('Two shortcuts (.bat files) have been created in this folder. Please move them wherever you find convenient.')
print('Double click them to start the servers, then access SilverDict at http://localhost:8081/')
print('Warning: the servers will stop when you close the command prompt window.')
print('Optionally, run the script "change_server_address.py" inside "http_server" to make SilverDict accessible from other devices on the same network.')
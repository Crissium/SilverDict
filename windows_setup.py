import sys
import subprocess
import os
import io
from zipfile import ZipFile

def pip_install(package: 'str') -> 'None':
	subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Check Python version >= 3.10
if sys.version_info < (3, 10):
	print("Python version 3.10 or higher is required. Please upgrade your Python installation.")
	sys.exit(1)

# Install dependencies
with open(os.path.join(os.path.dirname(__file__), 'http_server', 'requirements.txt')) as f:
	requirements = f.read().splitlines()
with open(os.path.join(os.path.dirname(__file__), 'server', 'requirements.txt')) as f:
	requirements += f.read().splitlines()

print('Installing the following dependencies:')
print('\n'.join(requirements))

for requirement in requirements:
	pip_install(requirement)

# Install winshell for accessing the desktop directory
pip_install('winshell')

# At this point, requests should be available
try:
	import requests
except ImportError:
	print('requests is not installed. Please install it manually.')
	sys.exit(1)

# Now download the zip archive containing the web app
url = 'https://github.com/Crissium/SilverDict/releases/download/v0.1.0/build.zip'
print('Downloading %s' % url)

# Check if the user specified http proxy in the command line arguments
if len(sys.argv) > 1:
	proxy = sys.argv[1]
	r = requests.get(url, allow_redirects=True, proxies={'http': proxy, 'https': proxy})
else:
	r = requests.get(url, allow_redirects=True)
zip_file = ZipFile(io.BytesIO(r.content))
zip_file.extractall(os.path.join(os.path.dirname(__file__), 'http_server'))
zip_file.close()
print('Done.')

# Create the desktop shortcuts (.bat files)
print('Creating desktop shortcuts...')
from winshell import desktop
BAT_TEMPLATE = '''ECHO ON
python "%s"
PAUSE
'''
http_server_path = os.path.join(os.path.dirname(__file__), 'http_server', 'http_server.py')
server_path = os.path.join(os.path.dirname(__file__), 'server', 'server.py')
desktop_path = desktop(False)
with open(os.path.join(desktop_path, 'Start SilverDict HTTP server.bat'), 'w') as f:
	f.write(BAT_TEMPLATE % http_server_path)
with open(os.path.join(desktop_path, 'Start SilverDict server.bat'), 'w') as f:
	f.write(BAT_TEMPLATE % server_path)
print('Two shortcuts have been created on your desktop.')
print('Double click them to start the servers, then access SilverDict at http://localhost:8081/')
print('Warning: the servers will stop when you close the command prompt window.')
print('Optionally, run the script "change_server_address.py" inside "http_server" to make SilverDict accessible from other devices on the same network.')
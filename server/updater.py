import requests
import xml.etree.ElementTree as ET
import sys
import os

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

timeout = 5
release_atom_url = 'https://github.com/Crissium/SilverDict/releases.atom'
windows_download_url = 'https://github.com/Crissium/SilverDict/releases/download/%s/SilverDict-windows.zip'
unix_download_url = 'https://github.com/Crissium/SilverDict/releases/download/%s/SilverDict.zip'
project_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
windows_save_path = os.path.join(os.path.dirname(project_directory), 'SilverDict-windows.zip')
unix_save_path = os.path.join(project_directory, 'SilverDict.zip')
current_version = 'v0.12.2'

def _get_latest_version_and_release_note() -> 'tuple[str, str]':
	response = requests.get(release_atom_url, timeout=timeout)
	if response.status_code != 200:
		raise Exception('Cannot get release atom')

	root = ET.fromstring(response.content)
	latest_version = root[5][3].text

	try:
		from lxml import html
		release_note = html.fromstring(root[5][4].text).text_content()
	except ImportError:
		release_note = root[5][4].text

	return latest_version, release_note

def _download_release(version: 'str') -> 'None':
	if sys.platform.startswith('win'):
		download_url = windows_download_url % version
	else:
		download_url = unix_download_url % version
	response = requests.get(download_url, timeout=timeout)
	if response.status_code != 200:
		raise Exception('Cannot download release.')
	with open(windows_save_path if sys.platform.startswith('win') else unix_save_path, 'wb') as f:
		f.write(response.content)

def update() -> 'None':
	try:
		latest_version, release_note = _get_latest_version_and_release_note()
		if latest_version == current_version:
			return
		logger.info('Found new version %s' % latest_version)
		logger.info('Release note:\n%s' % release_note)
		_download_release(latest_version)
		logger.info('Update downloaded to %s' % (windows_save_path if sys.platform.startswith('win') else unix_save_path))
	except requests.exceptions.Timeout:
		logger.error('Timeout while connecting to GitHub.')

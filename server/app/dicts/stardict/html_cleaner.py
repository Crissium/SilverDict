import re

class HtmlCleaner:
	"""
	Cleans up HTML-formatted StarDict dictionaries. Does the following:
	- convert href="bword://Bogen" to href="/api/lookup/OxfordDuden/Bogen"
	"""
	def __init__(self, dictionary_name: 'str') -> 'None':
		self._href_root = '/api/cache/' + dictionary_name + '/'
		self._lookup_url_root = '/api/lookup/' + dictionary_name + '/'
		self._cross_ref_pattern = r'href="bword://([^"]+)"'
		self._cross_ref_replacement = r'href="' + self._lookup_url_root + r'\1"'

	def clean(self, html: 'str') -> 'str':
		html = re.sub(self._cross_ref_pattern, self._cross_ref_replacement, html)
		return html

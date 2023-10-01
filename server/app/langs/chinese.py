import unicodedata

def is_chinese(s: 'str') -> 'bool':
	"""
	Check if a string contains Chinese characters.
	The current implementation could break Japanese dictionaries.
	"""
	for c in s:
		if unicodedata.name(c).startswith('CJK'):
			return True
	return False

try:
	from opencc import OpenCC

	_to_traditional = OpenCC('s2twp.json')
	_to_simplified = OpenCC('tw2sp.json')
	def transliterate(s: 'str') -> 'list[str]':
		"""
		Two-way conversion of Chinese characters.
		Returns Traditional and Simplified Chinese.
		"""
		return [_to_traditional.convert(s), _to_simplified.convert(s)]
except ImportError:
	def transliterate(s: 'str') -> 'list[str]':
		"""
		No conversion.
		"""
		return [s]
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

	opencc_found = True
	to_traditional = OpenCC('s2twp.json')
	to_simplified = OpenCC('tw2sp.json')
	def transliterate(s: 'str') -> 'list[str]':
		"""
		Two-way conversion of Chinese characters.
		Returns Traditional and Simplified Chinese.
		"""
		return [to_traditional.convert(s), to_simplified.convert(s)]
except ImportError:
	opencc_found = False
	def transliterate(s: 'str') -> 'list[str]':
		"""
		No conversion.
		"""
		return [s]
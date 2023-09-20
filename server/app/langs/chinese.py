from opencc import OpenCC
import unicodedata

to_traditional = OpenCC('s2twp.json')
to_simplified = OpenCC('tw2sp.json')

def is_chinese(s: 'str') -> 'bool':
	"""
	Check if a string contains Chinese characters.
	The current implementation could break Japanese dictionaries.
	"""
	for c in s:
		if unicodedata.name(c).startswith('CJK'):
			return True
	return False

def transliterate(s: 'str') -> 'list[str]':
	"""
	Two-way conversion of Chinese characters.
	Returns Traditional and Simplified Chinese.
	"""
	return [to_traditional.convert(s), to_simplified.convert(s)]
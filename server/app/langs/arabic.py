"""
This module provides one-way transliteration support for the Arabic script. The scheme used
is the Buckwalter transliteration scheme (https://en.wikipedia.org/wiki/Buckwalter_transliteration#Buckwalter_transliteration_table):
"""

_ASCII_TO_AR_TRANSLITERATION_TABLE = str.maketrans(
	"'|>&<}AbptvjHxd*rzs$SDTZEg_fqklmnhwYyFNKaui~o`{",
	'\u0621\u0622\u0623\u0624\u0625\u0626\u0627\u0628\u0629\u062a\u062b\u062c\u062d\u062e\u062f\u0630\u0631\u0632\u0633\u0634\u0635\u0636\u0637\u0638\u0639\u063a\u0640\u0641\u0642\u0643\u0644\u0645\u0646\u0647\u0648\u0649\u064a\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670\u0671'
)


def is_arabic_transliterated(s: str) -> bool:
	"""
	Check if a string contains the ASCII characters used in the transliteration scheme.
	"""
	return all(ord(c) in _ASCII_TO_AR_TRANSLITERATION_TABLE.keys() for c in s)


def transliterate(ascii: str) -> list[str]:
	"""
	Transliterate from ASCII to Arabic script.
	"""
	return [ascii.translate(_ASCII_TO_AR_TRANSLITERATION_TABLE)]


if __name__ == '__main__':
	# TODO: add tests
	assert is_arabic_transliterated('yuwladu')

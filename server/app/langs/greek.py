"""
This module provides transliteration support for Greek, ancient and modern.
The transliteration scheme is 'Beta Code', which defines a bijective mapping from Greek to Latin letters:
α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ ς τ υ φ χ ψ ω
a b g d e z h q i k l m n c o p r s s t u f x y w

(It is indeed bijective, ς is used only at the end of a word.)
"""

import unicodedata
import re

_EL_TO_LA_TRANSLITERATION_TABLE = str.maketrans(
	'\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8\u03b9\u03ba\u03bb\u03bc\u03bd\u03be\u03bf\u03c0\u03c1\u03c3\u03c2\u03c4\u03c5\u03c6\u03c7\u03c8\u03c9',
	'abgdezhqiklmncoprsstufxyw'
)

_LA_TO_EL_TRANSLITERATION_TABLE = str.maketrans(
	'abgdezhqiklmncoprstufxyw',
	'\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8\u03b9\u03ba\u03bb\u03bc\u03bd\u03be\u03bf\u03c0\u03c1\u03c3\u03c4\u03c5\u03c6\u03c7\u03c8\u03c9'
)

_FINAL_SIGMA_PATTERN = re.compile(r'\u03c3\b|\u03c3$')


def _transliterate_latin_into_greek(s: str) -> str:
	s = s.translate(_LA_TO_EL_TRANSLITERATION_TABLE)
	# Replace all σ's that are at the end of a word with ς
	s = _FINAL_SIGMA_PATTERN.sub('\u03c2', s)
	return s


def is_greek(s: str) -> bool:
	"""
	Check if a string contains Greek or Latin letters.
	"""
	for c in s:
		if unicodedata.name(c).startswith('GREEK') or unicodedata.name(c).startswith('LATIN'):
			return True
	return False


def transliterate(s: str) -> list[str]:
	"""
	Bidirectional transliteration between Greek and Latin letters.
	"""
	return [_transliterate_latin_into_greek(s), s.translate(_EL_TO_LA_TRANSLITERATION_TABLE)]


if __name__ == '__main__':
	assert is_greek('αγαθος')
	assert 'agaqos' in transliterate('αγαθος')
	assert is_greek('ψυχη')
	assert 'yuxh' in transliterate('ψυχη')
	assert is_greek('agaqos')
	assert 'αγαθος' in transliterate('agaqos')
	assert is_greek('yuxh')
	assert 'ψυχη' in transliterate('yuxh')

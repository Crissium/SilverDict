"""
This module provides transliteration support for Greek, ancient and modern.
The transliteration scheme is 'Beta Code', as recommended by Jiang Qian.
It defines an injective mapping between Greek and Latin letters:
α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ ς τ υ φ χ ψ ω
a b g d e z h q i k l m n c o p r s s t u f x y w

Note that it is only to be used to transliterate Greek into Latin, not the other way around.
The idea is, sometimes a Greek lexicon's headwords are written in Latin, and we desire
to query with Greek letters. This module provides a way to do that.
"""

import unicodedata

TRANSLITERATION_TABLE = str.maketrans(
	'αβγδεζηθικλμνξοπρσςτυφχψω',
	'abgdezhqiklmncoprsstufxyw'
)

def is_greek(s: 'str') -> 'bool':
	"""
	Check if a string contains Greek letters.
	"""
	for c in s:
		if unicodedata.name(c).startswith('GREEK'):
			return True
	return False

def transliterate(greek: 'str') -> 'str':
	"""
	Transliterates Greek into Latin.
	"""
	return greek.translate(TRANSLITERATION_TABLE)

if __name__ == '__main__':
	assert is_greek('αγαθος')
	assert transliterate('αγαθος') == 'agaqos'
	assert is_greek('ψυχη')
	assert transliterate('ψυχη') == 'yuxh'
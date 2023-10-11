import os
from pathlib import Path
from . import greek
from . import chinese
from .chinese import convert_chinese
from ..settings import Settings
from ..dicts.base_reader import BaseReader

simplify = BaseReader.simplify

is_lang = {
	'el': greek.is_greek,
	'zh': chinese.is_chinese
}

transliterate = {
	'el': greek.transliterate,
	'zh': chinese.transliterate
}

try:
	from hunspell import HunSpell

	HUNSPELL_DIR = os.path.join(Settings.APP_RESOURCES_ROOT, 'hunspell')
	# Let the users link/copy the dictionary files themselves to ensure cross-platform compatibility
	Path(HUNSPELL_DIR).mkdir(parents=True, exist_ok=True)
	_spellers = dict()
	for lang in Settings.LANGS:
		aff_file = os.path.join(HUNSPELL_DIR, '%s.aff' % lang)
		dic_file = os.path.join(HUNSPELL_DIR, '%s.dic' % lang)
		if os.path.isfile(aff_file) and os.path.isfile(dic_file):
			_spellers[lang] = HunSpell(dic_file, aff_file)

	def stem(key: 'str', langs: 'set[str]') -> 'list[str]':
		stems = []
		for lang in langs:
			if lang in _spellers.keys():
				stems.extend([s.decode('utf-8') for s in _spellers[lang].stem(key)]) # Hunspell returns an empty list when encoutering gibberish
		return stems

	def spelling_suggestions(key: 'str', langs: 'set[str]') -> 'list[str]':
		suggestions = []
		for lang in langs:
			if lang in _spellers.keys():
				raw_suggestions = _spellers[lang].suggest(key)
				# We need to get the stems of the suggestions.
				# e.g. if the input is deplacons, the suggestion merely gets the diacritics back,
				# but we want déplacer.
				# Well, seems `stem()` has been superceded here. Maybe we should make it private?
				for suggestion in raw_suggestions:
					suggestions.extend(stem(suggestion, {lang}))
		return list(set(suggestions))
	
	def orthographic_forms(key_simplified: 'str', langs: 'set[str]') -> 'list[str]':
		"""
		Given a simplified key, return all words 'desimplified.'
		For example, in Portuguese, avo -> [avo, avô, avó]
		"""
		forms = []
		for lang in langs:
			if lang in _spellers.keys():
				forms.extend([suggestion for suggestion in _spellers[lang].suggest(key_simplified) if simplify(suggestion) == key_simplified and ' ' not in suggestion])
		return list(set(forms))

except ImportError:
	def stem(key: 'str', langs: 'set[str]') -> 'list[str]':
		return []

	def spelling_suggestions(key: 'str', langs: 'set[str]') -> 'list[str]':
		return []
	
	def orthographic_forms(key_simplified: 'str', langs: 'set[str]') -> 'list[str]':
		return []

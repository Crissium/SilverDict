from hunspell import HunSpell
import os
from pathlib import Path
from . import greek
from ..settings import Settings

is_lang = {
	'el': greek.is_greek
}

transliterate = {
	'el': greek.transliterate
}

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
	"""
	The key here should be the original query.
	"""
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

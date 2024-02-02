import os
from pathlib import Path
from . import greek
from . import arabic
from . import chinese
from .chinese import convert_chinese
from ..settings import Settings
from ..dicts.base_reader import BaseReader

available_speller = ''
try:
	from sibel import Speller
	available_speller = 'Sibel'
except ImportError:
	try:
		from hunspell import HunSpell
		available_speller = 'Hunspell'
	except ImportError:
		pass

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if available_speller:
	logger.info(f'Using speller {available_speller}')
else:
	logger.warning('No spellchecking library found.')

simplify = BaseReader.simplify

is_lang = {
	'ar': arabic.is_arabic_transliterated,
	'el': greek.is_greek,
	'zh': chinese.is_chinese
}

transliterate = {
	'ar': arabic.transliterate,
	'el': greek.transliterate,
	'zh': chinese.transliterate
}

if available_speller:
	HUNSPELL_DIR = os.path.join(Settings.APP_RESOURCES_ROOT, 'hunspell')
	# Let the users link/copy the dictionary files themselves to ensure cross-platform compatibility
	Path(HUNSPELL_DIR).mkdir(parents=True, exist_ok=True)
	_spellers = dict()
	if available_speller == 'Sibel':
		for lang in Settings.LANGS:
			aff_file = os.path.join(HUNSPELL_DIR, '%s.aff' % lang)
			dic_file = os.path.join(HUNSPELL_DIR, '%s.dic' % lang)
			if os.path.isfile(aff_file) and os.path.isfile(dic_file):
				_spellers[lang] = Speller(HUNSPELL_DIR, lang)

		def stem(key: str, langs: set[str]) -> list[str]:
			stems = set()
			for lang in langs:
				if lang in _spellers.keys():
					stems.update(_spellers[lang].stem(key))
			return list(stems)
		
		def spelling_suggestions(key: str, langs: set[str]) -> list[str]:
			suggestions = set()
			for lang in langs:
				if lang in _spellers.keys():
					suggestions_inflected = _spellers[lang].suggest(key)
					for suggestion in suggestions_inflected:
						suggestions.update(_spellers[lang].stem(suggestion))
			return list(suggestions)
		
		def orthographic_forms(key_simplified: str, langs: set[str]) -> list[str]:
			forms = set()
			for lang in langs:
				if lang in _spellers.keys():
					forms.update(_spellers[lang].orthographic_forms(key_simplified))
			return list(forms)

	elif available_speller == 'Hunspell':
		EXCLUDED_CHARACTERS = (' ', '-', "'", "’")

		for lang in Settings.LANGS:
			aff_file = os.path.join(HUNSPELL_DIR, '%s.aff' % lang)
			dic_file = os.path.join(HUNSPELL_DIR, '%s.dic' % lang)
			if os.path.isfile(aff_file) and os.path.isfile(dic_file):
				_spellers[lang] = HunSpell(dic_file, aff_file)

		def stem(key: str, langs: set[str]) -> list[str]:
			stems = set()
			for lang in langs:
				if lang in _spellers.keys():
					# Hunspell returns an empty list when encoutering gibberish
					stems.update([s.decode('utf-8') for s in _spellers[lang].stem(key)])
			return list(stems)

		def spelling_suggestions(key: str, langs: set[str]) -> list[str]:
			suggestions = set()
			for lang in langs:
				if lang in _spellers.keys():
					suggestions_inflected = _spellers[lang].suggest(key)
					# We need to get the stems of the suggestions.
					# e.g. if the input is deplacons, the suggestion merely gets the diacritics back,
					# but we want déplacer.
					for suggestion in suggestions_inflected:
						suggestions.update(stem(suggestion, {lang}))
			return list(suggestions)

		def orthographic_forms(key_simplified: str, langs: set[str]) -> list[str]:
			"""
			Given a simplified key, return all words 'desimplified.'
			For example, in Portuguese, avo -> [avo, avô, avó]
			"""
			forms = set()
			for lang in langs:
				if lang in _spellers.keys():
					forms.update([
						suggestion
						for suggestion in _spellers[lang].suggest(key_simplified)
						if simplify(suggestion) == key_simplified\
							and all(excluded_character not in suggestion
								for excluded_character in EXCLUDED_CHARACTERS)
					])
			return list(forms)

else: # No available speller
	def stem(key: str, langs: set[str]) -> list[str]:
		return []

	def spelling_suggestions(key: str, langs: set[str]) -> list[str]:
		return []

	def orthographic_forms(key_simplified: str, langs: set[str]) -> list[str]:
		return []

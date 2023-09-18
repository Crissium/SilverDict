from flask import Flask
import concurrent.futures
import re
from .settings import Settings
from . import db_manager
from .dicts.base_reader import BaseReader
from .dicts.mdict_reader import MDictReader
from .dicts.stardict_reader import StarDictReader
from .dicts.dsl_reader import DSLReader
from .langs import is_lang, transliterate, stem, spelling_suggestions, convert_chinese
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

simplify = BaseReader.simplify

class Dictionaries:
	_LEGACY_LOOKUP_API_PATTERN = r'/api/lookup/([^/]+)/([^/]+)'

	def _load_dictionary(self, dictionary_info: 'dict') -> 'None':
		match dictionary_info['dictionary_format']:
			case 'MDict (.mdx)':
				self.dictionaries[dictionary_info['dictionary_name']] = MDictReader(dictionary_info['dictionary_name'], dictionary_info['dictionary_filename'], dictionary_info['dictionary_display_name'])
			case 'StarDict (.ifo)':
				self.dictionaries[dictionary_info['dictionary_name']] = StarDictReader(dictionary_info['dictionary_name'], dictionary_info['dictionary_filename'], dictionary_info['dictionary_display_name'])
			case 'DSL (.dsl/.dsl.dz)':
				if self.settings.preferences['running_mode'] == 'normal':
					self.dictionaries[dictionary_info['dictionary_name']] = DSLReader(dictionary_info['dictionary_name'], dictionary_info['dictionary_filename'], dictionary_info['dictionary_display_name'])
				elif self.settings.preferences['running_mode'] == 'preparation':
					self.dictionaries[dictionary_info['dictionary_name']] = DSLReader(dictionary_info['dictionary_name'], dictionary_info['dictionary_filename'], dictionary_info['dictionary_display_name'], True, True)
				else: # 'server' mode
					self.dictionaries[dictionary_info['dictionary_name']] = DSLReader(dictionary_info['dictionary_name'], dictionary_info['dictionary_filename'], dictionary_info['dictionary_display_name'])
			case _:
				raise ValueError('Dictionary format %s not supported' % dictionary_info['dictionary_format'])

	def __init__(self, app: 'Flask') -> 'None':
		app.extensions['dictionaries'] = self

		self.settings = Settings()

		db_manager.create_table_entries()

		self.dictionaries : 'dict[str, BaseReader]' = dict()
		for dictionary_info in self.settings.dictionaries_list:
			self._load_dictionary(dictionary_info)
		logger.info('Dictionaries loaded into memory.')

	def add_dictionary(self, dictionary_info: 'dict') -> 'None':
		self._load_dictionary(dictionary_info)
		self.settings.add_dictionary(dictionary_info)
		logger.info('Added dictionary %s' % dictionary_info['dictionary_name'])

	def remove_dictionary(self, dictionary_info: 'dict') -> 'None':
		self.settings.remove_dictionary(dictionary_info)
		self.dictionaries.pop(dictionary_info['dictionary_name'])
		db_manager.delete_dictionary(dictionary_info['dictionary_name'])
		logger.info('Removed dictionary %s' % dictionary_info['dictionary_name'])

	def reload_dictionaries(self, dictionaries_info: 'list[dict]') -> 'None':
		# First find removed dictionaries
		removed_dictionaries = [dictionary_info for dictionary_info in self.settings.dictionaries_list if not dictionary_info in dictionaries_info]
		for dictionary_info in removed_dictionaries:
			self.remove_dictionary(dictionary_info)

		# Then find added dictionaries
		added_dictionaries = [dictionary_info for dictionary_info in dictionaries_info if not dictionary_info in self.settings.dictionaries_list]
		for dictionary_info in added_dictionaries:
			self.add_dictionary(dictionary_info)

	def _transliterate_key(self, key: 'str', langs: 'set[str]') -> 'list[str]':
		keys = []
		for lang in langs:
			if lang in transliterate.keys():
				if lang in is_lang.keys() and is_lang[lang](key):
					keys.extend(transliterate[lang](key))
		return keys

	def get_spelling_suggestions(self, group_name: 'str', key: 'str') -> 'list[str]':
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		suggestions = [simplify(suggestion) for suggestion in spelling_suggestions(key, self.settings.group_lang(group_name)) if db_manager.entry_exists_in_dictionaries(simplify(suggestion), names_dictionaries_of_group)]
		return db_manager.select_entries_with_keys(suggestions, names_dictionaries_of_group, [], self.settings.misc_configs['num_suggestions'])

	def suggestions(self, group_name: 'str', key: 'str') -> 'list[str]':
		"""
		Return matched headwords if the key is found;
		Otherwise return spelling suggestions or word stems.
		"""
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		key_simplified = simplify(key)
		if any(wildcard in key_simplified for wildcard in self.settings.WILDCARDS.keys()):
			# If key has any wildcards, search as is
			key_simplified = Settings.transform_wildcards(key_simplified)
			candidates = db_manager.select_entries_like(key_simplified, names_dictionaries_of_group, self.settings.misc_configs['num_suggestions'])
		else:
			keys = self._transliterate_key(key_simplified, self.settings.group_lang(group_name))
			# First search for entries beginning with `key`, as is common sense
			candidates_beginning_with_key = db_manager.select_entries_beginning_with(keys, names_dictionaries_of_group, self.settings.misc_configs['num_suggestions'])
			if self.settings.preferences['suggestions_mode'] == 'right-side':
				candidates = candidates_beginning_with_key
			elif self.settings.preferences['suggestions_mode'] == 'both-sides':
				keys_expanded = []
				for key_simplified in keys:
					keys_expanded.extend(db_manager.expand_key(key_simplified))
				candidates_containing_key = db_manager.select_entries_with_keys(keys_expanded, names_dictionaries_of_group, candidates_beginning_with_key, self.settings.misc_configs['num_suggestions'])
				candidates = candidates_beginning_with_key + candidates_containing_key
			if len(candidates) == 0:
				# Now try some spelling suggestions, which is slower than the above
				candidates = self.get_spelling_suggestions(group_name, key)
		# Fill the list with blanks if there are fewer than the specified number of candidates
		while len(candidates) < self.settings.misc_configs['num_suggestions']:
			candidates.append('')
		return candidates

	def lookup(self, dictionary_name: 'str', key: 'str') -> 'str':
		"""
		Returns HTML article
		"""
		return self.dictionaries[dictionary_name].entry_definition(key)

	def query(self, group_name: 'str', key: 'str') -> 'list[tuple[str, str, str]]':
		"""
		Returns a list of tuples (dictionary name, dictionary display name, HTML article)
		"""
		key_simplified = simplify(key)
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		group_lang = self.settings.group_lang(group_name)
		keys = [simplify(s) for s in stem(key, group_lang)] + self._transliterate_key(key_simplified, group_lang)
		autoplay_found = False
		articles = []
		def replace_legacy_lookup_api(match: 're.Match') -> 'str':
			return '/api/query/%s/%s' % (group_name, match.group(2))
		def extract_articles_from_dictionary(dictionary_name: 'str') -> 'None':
			nonlocal autoplay_found
			keys_found = [key for key in keys if db_manager.entry_exists_in_dictionary(key, dictionary_name)]
			article = self.dictionaries[dictionary_name].entries_definitions(keys_found)
			if article:
				article = re.sub(self._LEGACY_LOOKUP_API_PATTERN, replace_legacy_lookup_api, article)
				# if 'zh' in group_lang:
				# 	article = convert_chinese(article, self.settings.preferences['chinese_preference'])
				if not autoplay_found and article.find('autoplay') != -1:
					autoplay_found = True
					articles.append((dictionary_name, self.settings.display_name_of_dictionary(dictionary_name), article))
				else:
					articles.append((dictionary_name, self.settings.display_name_of_dictionary(dictionary_name), article.replace('autoplay', '')))

		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.map(extract_articles_from_dictionary, names_dictionaries_of_group)

		if len(articles) > 0:
			self.settings.add_word_to_history(key)

		# The articles may be out of order after parellel processing, so we reorder them by the order of dictionaries in the group
		articles = [article for dictionary_name in names_dictionaries_of_group for article in articles if article[0] == dictionary_name]
		return articles

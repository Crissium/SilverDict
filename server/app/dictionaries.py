from flask import Flask
from .settings import Settings
from . import db_manager
from .dicts.base_reader import BaseReader
from .dicts.mdict_reader import MDictReader
from .dicts.stardict_reader import StarDictReader
from .dicts.dsl_reader import DSLReader
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

simplify = BaseReader.simplify

class Dictionaries:
	def _load_dictionary(self, dictionary_info: 'dict') -> 'None':
		match dictionary_info['dictionary_format']:
			case 'MDict (.mdx)':
				self.dictionaries[dictionary_info['dictionary_name']] = MDictReader(dictionary_info['dictionary_name'], dictionary_info['dictionary_filename'], dictionary_info['dictionary_display_name'])
			case 'StarDict (.ifo)':
				self.dictionaries[dictionary_info['dictionary_name']] = StarDictReader(dictionary_info['dictionary_name'], dictionary_info['dictionary_filename'], dictionary_info['dictionary_display_name'])
			case 'DSL (.dsl/.dsl.dz)':
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

	def suggestions(self, group_name: 'str', key: 'str') -> 'list[str]':
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		key = simplify(key)
		if any(wildcard in key for wildcard in self.settings.WILDCARDS.keys()):
			# If key has any wildcards, search as is
			key = Settings.transform_wildcards(key)
			candidates = db_manager.select_entries_like(key, names_dictionaries_of_group)
		else:
			# First search for entries beginning with `key`, as is common sense
			candidates_beginning_with_key = db_manager.select_entries_beginning_with(key, names_dictionaries_of_group)
			# Then it's just 'contains' searching
			candidates_containing_key = db_manager.select_entries_containing(key, names_dictionaries_of_group, candidates_beginning_with_key)
			candidates = candidates_beginning_with_key + candidates_containing_key
		# Fill the list with blanks if there are less than 10 candidates
		while len(candidates) < 10:
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
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		autoplay_found = False
		articles = []
		for dictionary_name in names_dictionaries_of_group:
			if db_manager.entry_exists_in_dictionary(key, dictionary_name):
				article = self.dictionaries[dictionary_name].entry_definition(key)
				if not autoplay_found and article.find('autoplay') != -1:
					autoplay_found = True
					articles.append((dictionary_name, self.settings.display_name_of_dictionary(dictionary_name), article))
				else:
					articles.append((dictionary_name, self.settings.display_name_of_dictionary(dictionary_name), article.replace('autoplay', '')))
		return articles

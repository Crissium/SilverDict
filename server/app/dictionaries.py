from flask import Flask
import concurrent.futures
import os
import re
from .settings import Settings
from . import db_manager
from .dicts import BaseReader, DSLReader, StarDictReader, MDictReader
from .langs import is_lang, transliterate, stem, spelling_suggestions, orthographic_forms, convert_chinese
from . import transformation
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

simplify = BaseReader.simplify


class Dictionaries:
	_re_legacy_lookup_api = re.compile(r'/api/lookup/([^/]+)/([^/]+)')
	re_cache_api = re.compile(r'/api/cache/([^/]+)/([^/]+)')
	_REPLACEMENT_TEXT = '!!@@SUBSTITUTION@@!!'
	re_img = re.compile(r'<img[^>]*>')
	re_audio = re.compile(r'<audio.*?>.*?</audio>')
	re_video = re.compile(r'<video.*?>.*?</video>')
	re_link_opening = re.compile(r'<a[^>]*>')
	re_link_closing = re.compile('</a>')
	re_headword = re.compile(r'<h3 class="headword">([^<]+)</h3>')

	def _load_dictionary(self, dictionary_info: 'dict') -> 'None':
		# First check if the dictionary file has changed. If so, re-index it.
		# Won't do if running under 'server' mode
		if self.settings.preferences['running_mode'] != 'server':
			prev_time_modified = self.settings.saved_dictionary_modification_time(dictionary_info['dictionary_name'])
			cur_time_modified = os.path.getmtime(dictionary_info['dictionary_filename'])
			if prev_time_modified and prev_time_modified < cur_time_modified:
				db_manager.delete_dictionary(dictionary_info['dictionary_name'])
				logger.info(f'Entries of {dictionary_info["dictionary_display_name"]} deleted from database,'
							'ready for re-indexing.')
				self.settings.update_dictionary_modification_time(dictionary_info['dictionary_name'],
													  			  cur_time_modified)
		match dictionary_info['dictionary_format']:
			case 'MDict (.mdx)':
				self.dictionaries[dictionary_info['dictionary_name']] =\
					MDictReader(dictionary_info['dictionary_name'],
				 				dictionary_info['dictionary_filename'],
								dictionary_info['dictionary_display_name'],
								load_content_into_memory=self.settings.dictionary_is_in_group(
									dictionary_info['dictionary_name'],
									Settings.NAME_GROUP_LOADED_INTO_MEMORY))
			case 'StarDict (.ifo)':
				self.dictionaries[dictionary_info['dictionary_name']] =\
					StarDictReader(dictionary_info['dictionary_name'],
								   dictionary_info['dictionary_filename'],
								   dictionary_info['dictionary_display_name'],
								   load_synonyms=self.settings.preferences['stardict_load_syns'],
								   load_content_into_memory=self.settings.dictionary_is_in_group(
									   dictionary_info['dictionary_name'],
									   Settings.NAME_GROUP_LOADED_INTO_MEMORY))
			case 'DSL (.dsl/.dsl.dz)':
				if self.settings.preferences['running_mode'] == 'normal':
					self.dictionaries[dictionary_info['dictionary_name']] =\
						DSLReader(dictionary_info['dictionary_name'],
								  dictionary_info['dictionary_filename'],
								  dictionary_info['dictionary_display_name'],
								  load_content_into_memory=self.settings.dictionary_is_in_group(
									dictionary_info['dictionary_name'],
									Settings.NAME_GROUP_LOADED_INTO_MEMORY))
				elif self.settings.preferences['running_mode'] == 'preparation':
					self.dictionaries[dictionary_info['dictionary_name']] =\
						DSLReader(dictionary_info['dictionary_name'],
								  dictionary_info['dictionary_filename'],
								  dictionary_info['dictionary_display_name'],
								  True,
								  True)
				else:  # 'server' mode
					self.dictionaries[dictionary_info['dictionary_name']] =\
						DSLReader(dictionary_info['dictionary_name'],
								  dictionary_info['dictionary_filename'],
								  dictionary_info['dictionary_display_name'])
			case _:
				raise ValueError(f'Dictionary format {dictionary_info["dictionary_format"]} not supported.')

	def __init__(self, app: 'Flask') -> 'None':
		app.extensions['dictionaries'] = self

		self.settings = Settings()

		db_manager.create_table_entries()

		self.dictionaries: 'dict[str, BaseReader]' = dict()
		# on HDD it would confuse the I/O scheduler to load the dictionaries in parallel
		if len(self.settings.dictionaries_of_group(Settings.NAME_GROUP_LOADED_INTO_MEMORY)) > 0:
			for dictionary_info in self.settings.dictionaries_list:
				self._load_dictionary(dictionary_info)
		else:
			with concurrent.futures.ThreadPoolExecutor() as executor:
				executor.map(self._load_dictionary, self.settings.dictionaries_list)

		logger.info('Dictionaries loaded.')

	def add_dictionary(self, dictionary_info: 'dict') -> 'None':
		dictionary_info['dictionary_filename'] =\
			self.settings.parse_path_with_env_variables(dictionary_info['dictionary_filename'])
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
		removed_dictionaries = [dictionary_info for dictionary_info in self.settings.dictionaries_list
								if not dictionary_info in dictionaries_info]
		for dictionary_info in removed_dictionaries:
			self.remove_dictionary(dictionary_info)

		# Then find added dictionaries
		added_dictionaries = [dictionary_info for dictionary_info in dictionaries_info
							  if not dictionary_info in self.settings.dictionaries_list]
		for dictionary_info in added_dictionaries:
			self.add_dictionary(dictionary_info)

	def _transliterate_key(self, key: 'str', langs: 'set[str]') -> 'list[str]':
		keys = []
		for lang in langs:
			if lang in transliterate.keys():
				if lang in is_lang.keys() and is_lang[lang](key):
					keys.extend(transliterate[lang](key))
		if len(keys) == 0:
			keys.append(key)
		keys = [simplify(k) for k in keys]
		return keys

	def get_spelling_suggestions(self, group_name: 'str', key: 'str') -> 'list[str]':
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		suggestions = [simplify(suggestion)
				 	for suggestion in spelling_suggestions(key,
											 			   self.settings.group_lang(group_name))
					if db_manager.entry_exists_in_dictionaries(simplify(suggestion),
															   names_dictionaries_of_group)]
		return db_manager.select_entries_with_keys(suggestions,
											 	   names_dictionaries_of_group,
												   [],
												   self.settings.misc_configs['num_suggestions'])

	def _safely_convert_chinese_article(self, article: 'str') -> 'str':
		"""
		A direct call to convert_chinese() converts things like API references.
		Now only cache API calls are protected.
		"""
		# First replace all API calls with the substitution string, then convert the article, and finally restore the API calls
		matches = self.re_cache_api.findall(article)
		article = self.re_cache_api.sub(self._REPLACEMENT_TEXT, article)
		article = convert_chinese(article, self.settings.preferences['chinese_preference'])
		for match in matches:
			article = article.replace(self._REPLACEMENT_TEXT, '/api/cache/%s/%s' % match, 1)
		return article

	def suggestions(self, group_name: 'str', key: 'str') -> 'list[str]':
		"""
		Return matched headwords if the key is found;
		Otherwise return spelling suggestions or word stems.
		"""
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		group_lang = self.settings.group_lang(group_name)
		# edge case for transliterated Arabic, which contains special symbols
		if 'ar' in group_lang and is_lang['ar'](key):
			key_simplified = key
		else:
			key_simplified = simplify(key)
		if any(wildcard in key_simplified for wildcard in self.settings.WILDCARDS.keys()):
			# If key has any wildcards, search as is
			key_simplified = Settings.transform_wildcards(key_simplified)
			suggestions = db_manager.select_entries_like(key_simplified,
														 names_dictionaries_of_group,
														 self.settings.misc_configs['num_suggestions'])
		else:
			keys = self._transliterate_key(key_simplified, group_lang)
			# First determine if any of the keys is a headword in an inflected form
			suggestions = []
			for key_simplified_transliterated in keys:
				key_orthographic_forms = [w
							  			  for w in orthographic_forms(key_simplified_transliterated,
										  							  group_lang)
										  if any(db_manager.entry_exists_in_dictionaries(
											  simplify(w_stem),
											  names_dictionaries_of_group) for w_stem in stem(w, group_lang))]
				suggestions.extend(key_orthographic_forms)
			# Then search for entries beginning with `key`, as is common sense
			suggestions.extend(db_manager.select_entries_beginning_with(keys,
															   			names_dictionaries_of_group,
																		suggestions,
																		self.settings.misc_configs['num_suggestions']))
			if self.settings.preferences['suggestions_mode'] == 'both-sides' and\
				len(suggestions) < self.settings.misc_configs['num_suggestions']:
				keys_expanded = []
				for key_simplified in keys:
					keys_expanded.extend(db_manager.expand_key(key_simplified,
															   self.settings.preferences['ngram_stores_keys']))
				suggestions.extend(db_manager.select_entries_with_keys(keys_expanded,
														   			   names_dictionaries_of_group,
																	   suggestions,
																	   self.settings.misc_configs['num_suggestions']))
			if len(suggestions) == 0:
				# Now try some spelling suggestions, which is slower than the above
				suggestions = self.get_spelling_suggestions(group_name, key)
		# Fill the list with blanks if there are fewer than the specified number of candidates
		while len(suggestions) < self.settings.misc_configs['num_suggestions']:
			suggestions.append('')
		return suggestions

	def lookup(self, dictionary_name: 'str', key: 'str') -> 'str':
		"""
		Returns HTML article
		"""
		return self.dictionaries[dictionary_name].get_definition_by_key(key)

	def query(self, group_name: 'str', key: 'str') -> 'list[tuple[str, str, str]]':
		"""
		Returns a list of tuples (dictionary name, dictionary display name, HTML article)
		"""
		key_simplified = simplify(key)
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		group_lang = self.settings.group_lang(group_name)
		keys = [simplify(s) for s in stem(key, group_lang)] + self._transliterate_key(key_simplified, group_lang)
		keys = list(set(keys))
		autoplay_found = False
		articles = []

		def replace_legacy_lookup_api(match: 're.Match') -> 'str':
			return '/api/query/%s/%s' % (group_name, match.group(2))

		def extract_articles_from_dictionary(dictionary_name: 'str') -> 'None':
			nonlocal autoplay_found
			keys_found = [key for key in keys if db_manager.entry_exists_in_dictionary(key, dictionary_name)]
			article = self.dictionaries[dictionary_name].get_definitions_by_keys(keys_found)
			if article:
				if 'zh' in group_lang:
					article = self._safely_convert_chinese_article(article)
				article = self._re_legacy_lookup_api.sub(replace_legacy_lookup_api, article)
				if dictionary_name in transformation.transform.keys():
					article = transformation.transform[dictionary_name](article)
				if not autoplay_found and (pos_autoplay := article.find('autoplay')) != -1:
					autoplay_found = True
					# Only preserve the first autoplay
					pos_autoplay += len('autoplay')
					article = article[:pos_autoplay] + article[pos_autoplay:].replace('autoplay', '')
					articles.append(
						(dictionary_name,
	   					self.settings.display_name_of_dictionary(dictionary_name),
						article))
				else:
					articles.append(
						(dictionary_name,
	   					self.settings.display_name_of_dictionary(dictionary_name),
						article.replace('autoplay', '')))

		with concurrent.futures.ThreadPoolExecutor(len(names_dictionaries_of_group)) as executor:
			executor.map(extract_articles_from_dictionary, names_dictionaries_of_group)

		if len(articles) > 0:
			self.settings.add_word_to_history(key)

		# The articles may be out of order after parellel processing, so we reorder them by the order of dictionaries in the group
		articles = [article
			  		for dictionary_name in names_dictionaries_of_group
					for article in articles
					if article[0] == dictionary_name]
		return articles

	def query_anki(self, group_name: 'str', word: 'str') -> 'str':
		"""
		Returns HTML article in a format suitable for Anki:
		1) media removed
		2) links removed
		3) without dictionary name or headword
		The `word` here is not simplified.
		"""
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		group_lang = self.settings.group_lang(group_name)
		articles = []

		def extract_article_from_dictionary(dictionary_name: 'str') -> 'None':
			if db_manager.headword_exists_in_dictionary(word, dictionary_name):
				article = self.dictionaries[dictionary_name].get_definition_by_word(word)
				if article:
					article = self.re_img.sub('', article)
					article = self.re_audio.sub('', article)
					article = self.re_video.sub('', article)
					article = self.re_link_opening.sub('', article)
					article = self.re_link_closing.sub('', article)
					article = self.re_headword.sub('', article)
					if 'zh' in group_lang:
						article = convert_chinese(article, self.settings.preferences['chinese_preference'])
					if dictionary_name in transformation.transform.keys():
						article = transformation.transform[dictionary_name](article)
					articles.append((article, dictionary_name))

		with concurrent.futures.ThreadPoolExecutor(len(names_dictionaries_of_group)) as executor:
			executor.map(extract_article_from_dictionary, names_dictionaries_of_group)

		# Sort the articles by the order of dictionaries in the group (only the articles are preserved)
		articles = [article[0]
					for dictionary_name in names_dictionaries_of_group
					for article in articles if article[1] == dictionary_name]

		return BaseReader._ARTICLE_SEPARATOR.join(articles)

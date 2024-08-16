from flask import Flask
import concurrent.futures
import os
import shutil
import re
import threading # FIXME: lock all list operations in case of the GIL being ditched
from .settings import Settings
from . import db_manager
from .dicts import BaseReader, DSLReader, StarDictReader, MDictReader
from .langs import is_lang, transliterate, stem, spelling_suggestions, orthographic_forms, convert_chinese
from . import transformation
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

simplify = BaseReader.simplify


try:
	import xapian
	xapian_found = True

	try:
		import lxml.html # In order to convert HTML articles to plain text
		lxml_found = True
	except ImportError:
		lxml_found = False
		logger.warning('lxml is recommended to get better full-text search results.')
	
	def _simplify_index(s: str) -> str:
		"""
		Strip diacritics, expand ligatures, and then case-fold.
		"""
		return BaseReader.expand_ligatures(BaseReader.strip_diacritics(s)).casefold()

except ImportError:
	xapian_found = False


class Dictionaries:
	_re_illegal_css_selector_chars =\
		re.compile('[\\~!@\\$%\\^\\&\\*\\(\\)\\+=,\\./\';:"\\?><\\[\\]\\\\\\{\\}\\|`\\#]')
	_re_legacy_lookup_api = re.compile(r'/api/lookup/([^/]+)/([^/]+)')
	_re_cache_api = re.compile(r'/api/cache/([^/]+)/([^/]+)')
	_REPLACEMENT_TEXT = '!!@@SUBSTITUTION@@!!'
	_re_img = re.compile(r'<img[^>]*>')
	_re_audio = re.compile(r'<audio.*?>.*?</audio>')
	_re_video = re.compile(r'<video.*?>.*?</video>')
	_re_link_opening = re.compile(r'<a[^>]*>')
	_re_link_closing = re.compile('</a>')
	_re_headword = re.compile(r'<h3 class="headword">([^<]+)</h3>')

	_XAPIAN_DICTNAME_WORD_SEP = '_*_'

	def _load_dictionary(self, dictionary_info: dict) -> None:
		# First check if the dictionary file has changed. If so, re-index it.
		# Won't do if running under 'server' mode
		if self.settings.preferences['running_mode'] != 'server':
			prev_time_modified =\
				self.settings.saved_dictionary_modification_time(dictionary_info['dictionary_name'])
			cur_time_modified = os.path.getmtime(dictionary_info['dictionary_filename'])
			if prev_time_modified and prev_time_modified < cur_time_modified:
				db_manager.delete_dictionary(dictionary_info['dictionary_name'])
				logger.info(f'Entries of {dictionary_info["dictionary_display_name"]} deleted from database,'
							'ready for re-indexing.')

		match dictionary_info['dictionary_format']:
			case 'MDict (.mdx)':
				self._dictionaries[dictionary_info['dictionary_name']] =\
					MDictReader(dictionary_info['dictionary_name'],
				 				dictionary_info['dictionary_filename'],
								dictionary_info['dictionary_display_name'],
								load_content_into_memory=self.settings.dictionary_is_in_group(
									dictionary_info['dictionary_name'],
									Settings.NAME_GROUP_LOADED_INTO_MEMORY))
			case 'StarDict (.ifo)':
				self._dictionaries[dictionary_info['dictionary_name']] =\
					StarDictReader(dictionary_info['dictionary_name'],
								   dictionary_info['dictionary_filename'],
								   dictionary_info['dictionary_display_name'],
								   load_synonyms=self.settings.preferences['stardict_load_syns'],
								   load_content_into_memory=self.settings.dictionary_is_in_group(
									   dictionary_info['dictionary_name'],
									   Settings.NAME_GROUP_LOADED_INTO_MEMORY))
			case 'DSL (.dsl/.dsl.dz)':
				if self.settings.preferences['running_mode'] == 'normal':
					self._dictionaries[dictionary_info['dictionary_name']] =\
						DSLReader(dictionary_info['dictionary_name'],
								  dictionary_info['dictionary_filename'],
								  dictionary_info['dictionary_display_name'],
								  load_content_into_memory=self.settings.dictionary_is_in_group(
									dictionary_info['dictionary_name'],
									Settings.NAME_GROUP_LOADED_INTO_MEMORY))
				elif self.settings.preferences['running_mode'] == 'preparation':
					self._dictionaries[dictionary_info['dictionary_name']] =\
						DSLReader(dictionary_info['dictionary_name'],
								  dictionary_info['dictionary_filename'],
								  dictionary_info['dictionary_display_name'],
								  True,
								  True)
				else:  # 'server' mode
					self._dictionaries[dictionary_info['dictionary_name']] =\
						DSLReader(dictionary_info['dictionary_name'],
								  dictionary_info['dictionary_filename'],
								  dictionary_info['dictionary_display_name'])
			case _:
				raise ValueError(f'Dictionary format {dictionary_info["dictionary_format"]} not supported.')

		if self.settings.preferences['running_mode'] != 'server':
			if dictionary_info['dictionary_filename'].endswith('.dsl'):
				dictionary_info['dictionary_filename'] += '.dz'
			cur_time_modified = os.path.getmtime(dictionary_info['dictionary_filename'])
			if prev_time_modified and prev_time_modified < cur_time_modified:
				self.settings.update_dictionary_modification_time(dictionary_info['dictionary_name'],
																  cur_time_modified)

	def __init__(self, app: Flask) -> None:
		app.extensions['dictionaries'] = self

		self.settings = Settings()

		db_manager.init_db()

		self._dictionaries: dict[str, BaseReader] = dict()
		# on HDD it would confuse the I/O scheduler to load the dictionaries in parallel
		if len(self.settings.dictionaries_of_group(Settings.NAME_GROUP_LOADED_INTO_MEMORY)) > 0:
			for dictionary_info in self.settings.dictionaries_list:
				self._load_dictionary(dictionary_info)
		else:
			with concurrent.futures.ThreadPoolExecutor() as executor:
				executor.map(self._load_dictionary, self.settings.dictionaries_list)

		logger.info('Dictionaries loaded.')

		self._xapian_indexing_lock = threading.Lock()

	def add_dictionary(self, dictionary_info: dict) -> None:
		dictionary_info['dictionary_name'] =\
			self._re_illegal_css_selector_chars.sub('', dictionary_info['dictionary_name'])
		# Remove whitespace and prepend '__' to make it a valid CSS selector
		dictionary_info['dictionary_name'] = '__' + ''.join(dictionary_info['dictionary_name'].split())

		dictionary_info['dictionary_filename'] =\
			self.settings.parse_path_with_env_variables(dictionary_info['dictionary_filename'])
		
		# Prohibit duplicate physical dictionaries but allow dictionaries with the same name
		if any(d['dictionary_filename'] == dictionary_info['dictionary_filename']
			   for d in self.settings.dictionaries_list):
			raise ValueError('Duplicate dictionary file.')
		
		while any(d['dictionary_name'] == dictionary_info['dictionary_name']
				  for d in self.settings.dictionaries_list):
			dictionary_info['dictionary_name'] += '_dup'

		self._load_dictionary(dictionary_info)
		self.settings.add_dictionary(dictionary_info)
		logger.info('Added dictionary %s' % dictionary_info['dictionary_name'])

	def remove_dictionary(self, dictionary_info: dict) -> None:
		self.settings.remove_dictionary(dictionary_info)
		self._dictionaries.pop(dictionary_info['dictionary_name'])
		db_manager.delete_dictionary(dictionary_info['dictionary_name'])
		logger.info('Removed dictionary %s' % dictionary_info['dictionary_name'])

	def reload_dictionaries(self, dictionaries_info: list[dict]) -> None:
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

	def _transliterate_key(self, key: str, langs: set[str]) -> list[str]:
		keys = []
		for lang in langs:
			if lang in transliterate.keys():
				if lang in is_lang.keys() and is_lang[lang](key):
					keys.extend(transliterate[lang](key))
		if len(keys) == 0:
			keys.append(key)
		keys = [simplify(k) for k in keys]
		return keys

	def get_spelling_suggestions(self, group_name: str, key: str) -> list[str]:
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

	def recreate_xapian_index(self) -> None:
		if not xapian_found:
			logger.warning('Refusing to build xapian index without installing the module.')
			return
		
		if self._xapian_indexing_lock.locked():
			logger.warning('Xapian index is being rebuilt.')
			return
		
		with self._xapian_indexing_lock:
			if os.path.isdir(self.settings.XAPIAN_DIR):
				shutil.rmtree(self.settings.XAPIAN_DIR)
			
			xapian_db = xapian.WritableDatabase(f'{self.settings.XAPIAN_DIR}_part', xapian.DB_CREATE_OR_OPEN)
			indexer = xapian.TermGenerator()
			indexer.set_flags(xapian.TermGenerator.FLAG_CJK_NGRAM)

			for dict_name in self.settings.dictionaries_of_group(self.settings.XAPIAN_GROUP_NAME):
				for word in db_manager.select_words_of_dictionary(dict_name):
					article = self._dictionaries[dict_name].get_definition_by_word(word)
					if lxml_found:
						article = lxml.html.fromstring(article).text_content()
					doc = xapian.Document()
					doc.set_data(self._XAPIAN_DICTNAME_WORD_SEP.join((dict_name, word)))

					indexer.set_document(doc)
					indexer.index_text(article)

					if self.settings.preferences['full_text_search_diacritic_insensitive']:
						indexer.index_text(_simplify_index(article))

					xapian_db.add_document(doc)
			
			xapian_db.commit()
			xapian_db.compact(self.settings.XAPIAN_DIR)
			xapian_db.close()
			
			shutil.rmtree(f'{self.settings.XAPIAN_DIR}_part')

		logger.info('Xapian index recreated.')

	def full_text_search(self, query_str: str) -> list[tuple[str, str, str, str]]:
		"""
		Returns all matched articles (dictionary name, word, dictionary display name, HTML article).
		Using the language features of the 'Xapian' group here.
		"""
		if not os.path.isdir(self.settings.XAPIAN_DIR):
			raise ValueError('Xapian index not found.')

		xapian_db = xapian.Database(self.settings.XAPIAN_DIR)
		enquire = xapian.Enquire(xapian_db)
		parser = xapian.QueryParser()
		parser.set_database(xapian_db)
		parser.set_default_op(xapian.Query.OP_AND)
		flag = xapian.QueryParser.FLAG_DEFAULT |\
			xapian.QueryParser.FLAG_PURE_NOT |\
			xapian.QueryParser.FLAG_CJK_NGRAM
		if '*' in query_str: # FIXME: detect trailing * only
			flag |= xapian.QueryParser.FLAG_WILDCARD
			parser.set_max_expansion(1)
		query = parser.parse_query(query_str, flag)
		
		enquire.set_query(query)
		matches = enquire.get_mset(0, self.settings.XAPIAN_MAX_RESULTS)

		def replace_legacy_lookup_api(match: re.Match) -> str:
			return f'/api/query/{self.settings.XAPIAN_GROUP_NAME}/{match.group(2)}'

		group_lang = self.settings.group_lang(self.settings.XAPIAN_GROUP_NAME)
		autoplay_found = False
		articles = []

		def extract_article(m: xapian.MSetItem) -> None:
			nonlocal autoplay_found
			dict_name, word = m.document.get_data().decode('utf-8').split(self._XAPIAN_DICTNAME_WORD_SEP)
			article = self._dictionaries[dict_name].get_definition_by_word(word)
			if article:
				if 'zh' in group_lang:
					article = self._safely_convert_chinese_article(article)
				article = self._re_legacy_lookup_api.sub(replace_legacy_lookup_api, article)
				if dict_name in transformation.transform.keys():
					article = transformation.transform[dict_name](article)
				if not autoplay_found and (pos_autoplay := article.find('autoplay')) != -1:
					autoplay_found = True
					# Only preserve the first autoplay
					pos_autoplay += len('autoplay')
					article = article[:pos_autoplay] + article[pos_autoplay:].replace('autoplay', '')
					articles.append(
						(m.rank,
						dict_name,
						word,
						self.settings.display_name_of_dictionary(dict_name),
						article))
				else:
					articles.append(
						(m.rank,
						dict_name,
						word,
						self.settings.display_name_of_dictionary(dict_name),
						article.replace('autoplay', '')))
				
				self.settings.add_to_history(word)
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.map(extract_article, matches)
		
		xapian_db.close()

		articles.sort(key=lambda x: x[0])
		articles = [(article[1], article[2], article[3], article[4]) for article in articles]

		return articles

	def _safely_convert_chinese_article(self, article: str) -> str:
		"""
		A direct call to convert_chinese() converts things like API references.
		Now only cache API calls are protected.
		"""
		# First replace all API calls with the substitution string, then convert the article, and finally restore the API calls
		matches = self._re_cache_api.findall(article)
		article = self._re_cache_api.sub(self._REPLACEMENT_TEXT, article)
		article = convert_chinese(article, self.settings.preferences['chinese_preference'])
		for match in matches:
			article = article.replace(self._REPLACEMENT_TEXT, '/api/cache/%s/%s' % match, 1)
		return article

	def suggestions(self, group_name: str, key: str) -> list[str]:
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
			suggestions = set()
			for key_simplified_transliterated in keys + [key]:
				key_orthographic_forms = [w
							  			  for w in orthographic_forms(key_simplified_transliterated,
										  							  group_lang)
										  if any(db_manager.entry_exists_in_dictionaries(
											  simplify(w_stem),
											  names_dictionaries_of_group) for w_stem in stem(w, group_lang))]
				suggestions.update(key_orthographic_forms)
			suggestions = list(suggestions)

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

		return suggestions

	def lookup(self, dictionary_name: str, key: str) -> str:
		"""
		Returns HTML article
		"""
		key = key.strip()
		self.settings.add_to_history(key)
		return self._dictionaries[dictionary_name].get_definition_by_key(key)

	def query(self, group_name: str, key: str) -> list[tuple[str, str, str]]:
		"""
		Returns a list of tuples (dictionary name, dictionary display name, HTML article)
		"""
		key = key.strip()
		key_simplified = simplify(key)
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		group_lang = self.settings.group_lang(group_name)
		keys = [simplify(s) for s in stem(key, group_lang)] + self._transliterate_key(key_simplified, group_lang)
		keys = list(set(keys))
		autoplay_found = False
		articles = []

		def replace_legacy_lookup_api(match: re.Match) -> str:
			return '/api/query/%s/%s' % (group_name, match.group(2))

		def extract_articles_from_dictionary(dictionary_name: str) -> None:
			nonlocal autoplay_found
			keys_found = [key for key in keys if db_manager.entry_exists_in_dictionary(key, dictionary_name)]
			article = self._dictionaries[dictionary_name].get_definitions_by_keys(keys_found)
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
			self.settings.add_to_history(key)

		# The articles may be out of order after parellel processing,
		# so we reorder them by the order of dictionaries in the group
		articles = [article
			  		for dictionary_name in names_dictionaries_of_group
					for article in articles
					if article[0] == dictionary_name]
		return articles

	def query_anki(self, group_name: str, word: str) -> list[tuple[str, str]]:
		"""
		Returns HTML article in a format suitable for Anki:
		- media removed
		- links removed
		- without dictionary name or headword
		The `word` here is not simplified.
		"""
		names_dictionaries_of_group = self.settings.dictionaries_of_group(group_name)
		group_lang = self.settings.group_lang(group_name)
		articles = []

		def extract_article_from_dictionary(dictionary_name: 'str') -> 'None':
			if db_manager.headword_exists_in_dictionary(word, dictionary_name):
				article = self._dictionaries[dictionary_name].get_definition_by_word(word)
				if article:
					article = self._re_img.sub('', article)
					article = self._re_audio.sub('', article)
					article = self._re_video.sub('', article)
					article = self._re_link_opening.sub('', article)
					article = self._re_link_closing.sub('', article)
					article = self._re_headword.sub('', article)
					if 'zh' in group_lang:
						article = convert_chinese(article, self.settings.preferences['chinese_preference'])
					if dictionary_name in transformation.transform.keys():
						article = transformation.transform[dictionary_name](article)
					articles.append((article, dictionary_name))

		with concurrent.futures.ThreadPoolExecutor(len(names_dictionaries_of_group)) as executor:
			executor.map(extract_article_from_dictionary, names_dictionaries_of_group)

		# Sort the articles by the order of dictionaries in the group (only the articles are preserved)
		articles = [(article[1], article[0])
					for dictionary_name in names_dictionaries_of_group
					for article in articles if article[1] == dictionary_name]

		return articles

import os
import sys
import shutil
from pathlib import Path
import yaml
import threading
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
	from yaml import CSafeLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import SafeLoader as Loader, Dumper
	logger.warning('Using pure Python YAML parser. Consider installing libyaml for faster speed.')

class Settings:
	PORT = '2628' # deliberately the same as the default port of dictd, meaning to supersede it
				  # Well, certainly I have not reached its production level yet, but one day...
	HOMEDIR = str(Path.home())
	try:
		CACHE_ROOT = os.path.join(HOMEDIR, '.cache', 'SilverDict') if HOMEDIR else '/tmp/SilverDict'
		APP_RESOURCES_ROOT = os.path.join(HOMEDIR, '.silverdict') if HOMEDIR else '/tmp/SilverDict'
		Path(CACHE_ROOT).mkdir(parents=True, exist_ok=True)
		Path(APP_RESOURCES_ROOT).mkdir(parents=True, exist_ok=True)
	except PermissionError:
		# Fix permission error on iOS (with a-Shell)
		CACHE_ROOT = os.path.join(HOMEDIR, 'Documents', '.cache', 'SilverDict')
		APP_RESOURCES_ROOT = os.path.join(HOMEDIR, 'Documents', '.silverdict')
		Path(CACHE_ROOT).mkdir(parents=True, exist_ok=True)
		Path(APP_RESOURCES_ROOT).mkdir(parents=True, exist_ok=True)

	SUPPORTED_DICTIONARY_FORMATS = {
		'MDict (.mdx)': ['.mdx', '.MDX'],
		'StarDict (.ifo)': ['.ifo'],
		'DSL (.dsl/.dsl.dz)': ['.dsl', '.dz']
	}

	PREFERENCES_FILE = os.path.join(APP_RESOURCES_ROOT, 'preferences.yaml')
	# a dict with three fields: listening_address, suggestions_mode, running_mode

	DICTIONARIES_LIST_FILE = os.path.join(APP_RESOURCES_ROOT, 'dictionaries.yaml')
	# a sample dictionary list :
	# [
	# 	{
	# 		"dictionary_display_name": "Oxford Dictionary of English",
	# 		"dictionary_name": "oxford_dictionary_of_english",
	# 		"dictionary_format": "MDict (.mdx)",
	# 		"dictionary_filename": "/home/alice/Documents/Dictionaries/oxford_dictionary_of_english.mdx"
	# 	},
	# 	{
	# 		"dictionary_display_name": "Collins English-French French-English Dictionary",
	# 		"dictionary_name": "collinse22f",
	# 		"dictionary_format": "MDict (.mdx)",
	# 		"dictionary_filename": "/home/alice/Documents/Dictionaries/collinse22f.mdx"
	# 	}
	# ]

	LANGS = ['aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'ar', 'as', 'av', 'ay', 'az', 'ba', 'be', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'br', 'bs', 'ca', 'ce', 'ch', 'co', 'cr', 'cs', 'cu', 'cv', 'cy', 'da', 'de', 'dv', 'dz', 'ee', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'ff', 'fi', 'fj', 'fo', 'fr', 'fy', 'ga', 'gd', 'gl', 'gn', 'gu', 'gv', 'ha', 'he', 'hi', 'ho', 'hr', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'io', 'is', 'it', 'iu', 'ja', 'jv', 'ka', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ku', 'kv', 'kw', 'ky', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'mg', 'mh', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'na', 'nb', 'nd', 'ne', 'ng', 'nl', 'nn', 'no', 'nr', 'nv', 'ny', 'oc', 'oj', 'om', 'or', 'os', 'pa', 'pi', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'rw', 'sa', 'sc', 'sd', 'se', 'sg', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi', 'vo', 'wa', 'wo', 'xh', 'yi', 'yo', 'za', 'zh', 'zu']

	GROUPS_FILE = os.path.join(APP_RESOURCES_ROOT, 'groups.yaml')
	# [
	# 	{
	# 		"name": "Default Group",
	# 		"lang": {}
	# 	},
	# 	{
	# 		"name": "English Dictionaries",
	# 		"lang": {"en", "zh"}
	# 	},
	# 	{
	# 		"name": "French Dictionaries",
	# 		"lang": {"en", "fr", "zh"}
	# 	}
	# ]

	JUNCTION_TABLE_FILE = os.path.join(APP_RESOURCES_ROOT, 'junction_table.yaml')
	# {
	# 	"oxford_dictionary_of_english": {"Default Group"},
	# 	"collinse22f": {"French Dictionaries"}
	# }

	HISTORY_FILE = os.path.join(APP_RESOURCES_ROOT, 'history.yaml')
	# Use list instead of deque

	MISC_CONFIGS_FILE = os.path.join(APP_RESOURCES_ROOT, 'misc.yaml')
	if sys.platform == 'win32':
		project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
		DEFAULT_SOURCE_DIR = os.path.join(project_root_dir, 'source')
	else:
		DEFAULT_SOURCE_DIR = os.path.join(APP_RESOURCES_ROOT, 'source')

	Path(DEFAULT_SOURCE_DIR).mkdir(parents=True, exist_ok=True)

	SQLITE_DB_FILE = os.path.join(APP_RESOURCES_ROOT, 'dictionaries.db')
	SQLITE_LIMIT_VARIABLE_NUMBER = 30000 # The real limit seems to be an arbitrary number choosen by SQLite people: 0x7ffe

	WILDCARDS = {'^': '%', '+': '_'}

	NGRAM_LEN = 4

	NAME_GROUP_LOADED_INTO_MEMORY = 'Memory'

	def _preferences_valid(self) -> 'bool':
		return all(key in self.preferences.keys() for key in ['listening_address', 'suggestions_mode', 'running_mode']) and self.preferences['suggestions_mode'] in ('right-side', 'both-sides') and self.preferences['running_mode'] in ('normal', 'preparation', 'server')

	@staticmethod
	def transform_wildcards(key: 'str') -> 'str':
		for wildcard, sql_wildcard in Settings.WILDCARDS.items():
			key = key.replace(wildcard, sql_wildcard)
		return key

	def _dictionary_format(self, filename: 'str') -> 'str | None':
		"""
		Returns one of the keys of SUPPORTED_DICTIONARY_FORMATS if it is a dictionary file,
		Otherwise returns None.
		"""
		base, extension = os.path.splitext(filename)
		# It's pretty complicated. Have to check manually.
		# First check if it is an MDict dictionary
		if extension in self.SUPPORTED_DICTIONARY_FORMATS['MDict (.mdx)']:
			return 'MDict (.mdx)'
		# Then check for StarDict
		if extension in self.SUPPORTED_DICTIONARY_FORMATS['StarDict (.ifo)']:
			return 'StarDict (.ifo)'
		# Then check for DSL, whose filename has to be either 'name.dsl' or 'name.dsl.dz'
		if extension == '.dsl':
			return 'DSL (.dsl/.dsl.dz)'
		if extension == '.dz' and os.path.splitext(base)[1] == '.dsl':
			return 'DSL (.dsl/.dsl.dz)'
		return None

	@staticmethod
	def _save_settings_to_file(settings: 'list | dict', filename: 'str') -> 'None':
		with open(filename, 'w') as settings_file:
			yaml.dump(settings, settings_file, Dumper=Dumper)

	@staticmethod
	def _read_settings_from_file(filename: 'str') -> 'list | dict':
		with open(filename) as settings_file:
			return yaml.load(settings_file, Loader=Loader)

	def _save_dictionary_list(self) -> 'None':
		# Check DSL dictionaries, whose filenames must end with '.dz'.
		for dictionary_info in self.dictionaries_list:
			if dictionary_info['dictionary_format'] == 'DSL (.dsl/.dsl.dz)' and not dictionary_info['dictionary_filename'].endswith('.dz'):
				dictionary_info['dictionary_filename'] += '.dz'
		self._save_settings_to_file(self.dictionaries_list, self.DICTIONARIES_LIST_FILE)

	def _save_groups(self) -> 'None':
		self._save_settings_to_file(self.groups, self.GROUPS_FILE)

	def _save_junction_table(self) -> 'None':
		self._save_settings_to_file(self.junction_table, self.JUNCTION_TABLE_FILE)

	def _save_history(self) -> 'None':
		self._save_settings_to_file(self.lookup_history, self.HISTORY_FILE)

	def _save_misc_configs(self) -> 'None':
		self._save_settings_to_file(self.misc_configs, self.MISC_CONFIGS_FILE)

	def change_suggestions_mode_from_right_side_to_both_sides(self) -> 'None':
		self.preferences['suggestions_mode'] = 'both-sides'
		with open(self.PREFERENCES_FILE) as preferences_file:
			preferences = preferences_file.read()
		preferences = preferences.replace('suggestions_mode: right-side', '# suggestions_mode: right-side').replace('# suggestions_mode: both-sides', 'suggestions_mode: both-sides')
		with open(self.PREFERENCES_FILE, 'w') as preferences_file:
			preferences_file.write(preferences)

	def __init__(self) -> 'None':
		if not os.path.isfile(self.PREFERENCES_FILE):
			with open(self.PREFERENCES_FILE, 'w') as preferences_file:
				preferences_file.write('''listening_address: 127.0.0.1
suggestions_mode: right-side # instantaneous
# suggestions_mode: both-sides # slow
running_mode: normal # suitable for running locally
# running_mode: preparation # use before deploying to a server
# running_mode: server # to be used in a resource-constrained environment
# chinese_preference: cn
# chinese_preference: tw
chinese_preference: none''')
		self.preferences : 'dict[str, str]' = self._read_settings_from_file(self.PREFERENCES_FILE)
		if 'chinese_preference' not in self.preferences.keys(): # Backward compatibility
			self.preferences['chinese_preference'] = 'none'
		if not self._preferences_valid():
			raise ValueError('Invalid preferences file.')

		if os.path.isfile(self.DICTIONARIES_LIST_FILE):
			self.dictionaries_list : 'list[dict[str, str]]' = self._read_settings_from_file(self.DICTIONARIES_LIST_FILE)
		else:
			self.dictionaries_list : 'list[dict[str, str]]' = []
			self._save_dictionary_list()

		if os.path.isfile(self.GROUPS_FILE):
			self.groups : 'list[dict[str, str | set[str]]]' = self._read_settings_from_file(self.GROUPS_FILE)
		else:
			self.groups = [
				{
					'name': 'Default Group',
					'lang': set()
				}
			]
			self._save_groups()

		if os.path.isfile(self.JUNCTION_TABLE_FILE):
			self.junction_table : 'dict[str, set[str]]' = self._read_settings_from_file(self.JUNCTION_TABLE_FILE)
			for dictionary_info in self.dictionaries_list:
				if not dictionary_info['dictionary_name'] in self.junction_table.keys():
					self.junction_table[dictionary_info['dictionary_name']] = {'Default Group'}
			self._save_junction_table()
		else:
			self.junction_table = {
				dictionary_info['dictionary_name']: {'Default Group'} for dictionary_info in self.dictionaries_list
			}
			self._save_junction_table()

		if os.path.isfile(self.HISTORY_FILE):
			self.lookup_history : 'list[str]' = self._read_settings_from_file(self.HISTORY_FILE)
		else:
			self.lookup_history :'list[str]' = []
			self._save_history()

		if os.path.isfile(self.MISC_CONFIGS_FILE):
			self.misc_configs : 'dict' = self._read_settings_from_file(self.MISC_CONFIGS_FILE)
			if 'history_size' not in self.misc_configs.keys():
				self.misc_configs['history_size'] = 100
			if 'sources' not in self.misc_configs.keys():
				self.misc_configs['sources'] = [
					self.DEFAULT_SOURCE_DIR
				]
			if 'num_suggestions' not in self.misc_configs.keys():
				self.misc_configs['num_suggestions'] = 10
			self._save_misc_configs()
		else:
			self.misc_configs = {
				'history_size': 100,
				'sources': [
					self.DEFAULT_SOURCE_DIR
				],
				'num_suggestions': 10
			}
			self._save_misc_configs()
		
		self.scan_lock = threading.Lock()

	def dictionary_info_valid(self, dictionary_info: 'dict') -> 'bool':
		return all(key in dictionary_info.keys() for key in ['dictionary_display_name', 'dictionary_name', 'dictionary_format', 'dictionary_filename']) and dictionary_info['dictionary_format'] in self.SUPPORTED_DICTIONARY_FORMATS.keys() and os.access(dictionary_info['dictionary_filename'], os.R_OK) and os.path.isfile(dictionary_info['dictionary_filename']) and os.path.splitext(dictionary_info['dictionary_filename'])[1] in self.SUPPORTED_DICTIONARY_FORMATS[dictionary_info['dictionary_format']] and not any(dictionary_info['dictionary_name'] == dictionary['dictionary_name'] for dictionary in self.dictionaries_list)

	def group_valid(self, group: 'dict[str, str | set[str]]') -> 'bool':
		return all(key in group.keys() for key in ['name', 'lang']) and all(lang in self.LANGS for lang in group['lang'])

	def source_valid(self, source: 'str') -> 'bool':
		if os.path.isfile(source):
			return False
		elif os.path.isdir(source):
			# Ensure read and write permission
			try:
				Path(os.path.join(source, 'test')).touch()
				os.remove(os.path.join(source, 'test'))
			except PermissionError:
				return False
			return True
		else:
			return False

	def add_dictionary(self, dictionary_info: 'dict', groups: 'list[str] | None'=None) -> 'None':
		self.dictionaries_list.append(dictionary_info)
		self._save_dictionary_list()
		self.junction_table[dictionary_info['dictionary_name']] = groups if groups else {'Default Group'}
		self._save_junction_table()

	def info_of_dictionary(self, dictionary_name: 'str') -> 'dict[str, str]':
		for dictionary_info in self.dictionaries_list:
			if dictionary_info['dictionary_name'] == dictionary_name:
				return dictionary_info
		raise ValueError('Dictionary %s not found' % dictionary_name)

	def display_name_of_dictionary(self, dictionary_name: 'str') -> 'str':
		for dictionary_info in self.dictionaries_list:
			if dictionary_info['dictionary_name'] == dictionary_name:
				return dictionary_info['dictionary_display_name']
		raise ValueError('Dictionary %s not found' % dictionary_name)

	def change_dictionary_display_name(self, dictionary_name: 'str', new_dictionary_display_name: 'str') -> 'None':
		for dictionary_info in self.dictionaries_list:
			if dictionary_info['dictionary_name'] == dictionary_name:
				dictionary_info['dictionary_display_name'] = new_dictionary_display_name
				logger.info('Name of dictionary %s changed to %s.' % (dictionary_info['dictionary_name'], new_dictionary_display_name))
				self._save_dictionary_list()
				break

	def remove_dictionary(self, dictionary_info: 'str') -> 'None':
		self.dictionaries_list.remove(dictionary_info)
		self._save_dictionary_list()
		self.junction_table.pop(dictionary_info['dictionary_name'])
		self._save_junction_table()
		resources_dir = os.path.join(self.CACHE_ROOT, dictionary_info['dictionary_name'])
		if os.path.islink(resources_dir):
			os.unlink(resources_dir)
		elif os.path.isdir(resources_dir):
			shutil.rmtree(resources_dir)

	def add_group(self, group: 'dict[str, str | list[str]]') -> 'None':
		group['lang'] = set(group['lang'])
		self.groups.append(group)
		self._save_groups()
		logger.info('Group %s added.' % group['name'])

	def group_lang(self, group_name: 'str') -> 'set[str]':
		for group in self.groups:
			if group['name'] == group_name:
				return group['lang']
		raise ValueError('Group %s not found' % group_name)

	def group_exists(self, group_name: 'str') -> 'bool':
		return any(group['name'] == group_name for group in self.groups)

	def get_groups(self) -> 'list[dict[str, str | list[str]]]':
		return [{
			'name': group['name'],
			'lang': list(group['lang'])
		} for group in self.groups]

	def get_dictionary_groupings(self) -> 'dict[str, list[str]]':
		"""
		Return a dict that maps group names to a set of dictionary names (reversed).
		"""
		dictionary_groupings = {group['name']: [] for group in self.groups}
		for dictionary_name, groups in self.junction_table.items():
			for group in groups:
				dictionary_groupings[group].append(dictionary_name)
		return dictionary_groupings

	def change_group_name(self, group_name: 'str', new_group_name: 'str') -> 'None':
		for group in self.groups:
			if group['name'] == group_name:
				group['name'] = new_group_name
				self._save_groups()
				break
		for dictionary_name in self.junction_table.keys():
			if group_name in self.junction_table[dictionary_name]:
				self.junction_table[dictionary_name].remove(group_name)
				self.junction_table[dictionary_name].add(new_group_name)
		self._save_junction_table()
		logger.info('Group %s changed to %s.' % (group_name, new_group_name))

	def change_group_lang(self, group_name: 'str', new_group_lang: 'list[str]') -> 'None':
		for group in self.groups:
			if group['name'] == group_name:
				group['lang'] = set(new_group_lang)
				logger.info('Languages of group %s changed to %s.' % (group_name, group['lang']))
				self._save_groups()
				break

	def reorder_groups(self, groups: 'list[dict[str, str | list[str]]]') -> 'None':
		"""
		The contents of groups must be exactly the same as self.groups.
		Only two groups can be swapped.
		"""
		# Convert list to set
		groups = [{
			'name': group['name'],
			'lang': set(group['lang'])
		} for group in groups]

		# Ensure the contents are the same
		if not all(group in groups for group in self.groups):
			raise ValueError('Modification of the group list is not allowed.')

		changed_indexes = []
		for index, group in enumerate(self.groups):
			if group != groups[index]:
				changed_indexes.append(index)

		if len(changed_indexes) == 0:
			return

		self.groups = groups
		logger.info('%d groups are reordered.' % len(changed_indexes))
		self._save_groups()

	def remove_group(self, group: 'dict[str, str | set[str]]') -> 'None':
		self.groups.remove(group)
		for dictionary_name in self.junction_table.keys():
			if group['name'] in self.junction_table[dictionary_name]:
				self.junction_table[dictionary_name].remove(group['name'])
		self._save_junction_table()
		self._save_groups()
		logger.info('Group %s removed.' % group['name'])

	def remove_group_by_name(self, name: 'str') -> 'None':
		for group in self.groups:
			if group['name'] == name:
				self.remove_group(group)
				break

	def add_dictionary_to_group(self, dictionary_name: 'str', group_name: 'str') -> 'None':
		if not group_name in self.junction_table[dictionary_name]:
			self.junction_table[dictionary_name].add(group_name)
			self._save_junction_table()
		logger.info('Dictionary %s added to group %s.' % (dictionary_name, group_name))

	def reorder_dictionaries(self, dictionaries_info: 'list[dict[str, str]]') -> 'None':
		"""
		The contents of dictionaries_info must be exactly the same as self.dictionary_list's.
		Only two dictionaries can be swapped.
		"""
		# First ensure the contents are the same
		if not all(dictionary_info in dictionaries_info for dictionary_info in self.dictionaries_list):
			raise ValueError('Modification of the dictionary list is not allowed.')

		changed_indexes = []
		for index, dictionary_info in enumerate(self.dictionaries_list):
			if dictionary_info != dictionaries_info[index]:
				changed_indexes.append(index)

		if len(changed_indexes) == 0:
			return

		self.dictionaries_list = dictionaries_info
		logger.info('%d dictionaries are reordered.' % len(changed_indexes))
		self._save_dictionary_list()

	def remove_dictionary_from_group(self, dictionary_name: 'str', group_name: 'str') -> 'None':
		self.junction_table[dictionary_name].remove(group_name)
		self._save_junction_table()
		logger.info('Dictionary %s removed from group %s.' % (dictionary_name, group_name))

	def dictionaries_of_group(self, group_name: 'str') -> 'list[str]':
		names = [dictionary_name for dictionary_name, groups in self.junction_table.items() if group_name in groups]
		# junction_table's keys are unordered, so we need to sort the list according to the order in dictionary_list
		return [dictionary_info['dictionary_name'] for dictionary_info in self.dictionaries_list if dictionary_info['dictionary_name'] in names]
	
	def dictionary_is_in_group(self, dictionary_name: 'str', group_name: 'str') -> 'bool':
		return group_name in self.junction_table[dictionary_name]

	def add_source(self, source: 'str') -> 'None':
		if not source in self.misc_configs['sources']:
			self.misc_configs['sources'].append(source)
			self._save_misc_configs()
			logger.info('New source %s added.' % source)

	def remove_source(self, source: 'str') -> 'None':
		"""
		The directory itself won't be removed
		"""
		if source in self.misc_configs['sources']:
			self.misc_configs['sources'].remove(source)
			self._save_misc_configs()
			logger.info('Source %s removed.' % source)
	
	def scan_source(self, source):
		for filename in os.listdir(source):
			full_filename = os.path.join(source, filename)
			if os.path.isfile(full_filename) and filename.find('_abrv.dsl') == -1: # see dsl_reader.py
				dictionary_format = self._dictionary_format(full_filename)
				if dictionary_format:
					if not any(dictionary_info['dictionary_filename'] == full_filename for dictionary_info in self.dictionaries_list):
						if filename.endswith('.dsl.dz'):
							name = filename[:-len('.dsl.dz')]
						else:
							name = os.path.splitext(filename)[0]
						logger.info('Found dictionary %s (%s) during re-scanning.' % (name, full_filename))
						yield {
							'dictionary_display_name': name,
							'dictionary_name': name,
							'dictionary_format': dictionary_format,
							'dictionary_filename': full_filename
						}
			elif os.path.isdir(full_filename) and filename.find('.files') == -1 and filename != 'res' and len(os.listdir(full_filename)) < 300: # arbitrary
				yield from self.scan_source(full_filename)

	def scan_sources(self):
		"""
		Scan the sources and return a list of unregistered dictionaries' info.
		"""
		with self.scan_lock:
			for source in self.misc_configs['sources']:
				yield from self.scan_source(source)

	def set_history_size(self, size: 'int') -> 'None':
		self.misc_configs['history_size'] = size
		if len(self.lookup_history) > size:
			self.lookup_history = self.lookup_history[:size]
		self._save_misc_configs()
		logger.info('History size changed to %d.' % size)

	def add_word_to_history(self, word: 'str') -> 'None':
		if word in self.lookup_history:
			self.lookup_history.remove(word)
		self.lookup_history.insert(0, word)
		if len(self.lookup_history) > int(self.misc_configs['history_size']):
			self.lookup_history.pop()
			logger.warning('History size exceeded, the oldest entry is removed')
		self._save_history()

	def clear_history(self) -> 'None':
		self.lookup_history.clear()
		self._save_history()

	def set_suggestions_size(self, new_size: 'int'):
		self.misc_configs['num_suggestions'] = int(new_size)
		self._save_misc_configs()
		logger.info('Number of suggestions changed to %d.' % new_size)
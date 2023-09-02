import os
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Config:
	PORT = '2628' # deliberately the same as the default port of dictd, meaning to supersede it
				  # Well, certainly I have not reached its production level yet, but one day...
	HOMEDIR = os.getenv('HOME')
	CACHE_ROOT = os.path.join(HOMEDIR, '.cache', 'SilverDict') if HOMEDIR else '/tmp/SilverDict'
	APP_RESOURCES_ROOT = os.path.join(HOMEDIR, '.silverdict') if HOMEDIR else '/tmp/SilverDict' # GoldenDict also uses such a directory instead of ~/.local/share
	Path(CACHE_ROOT).mkdir(parents=True, exist_ok=True)
	Path(APP_RESOURCES_ROOT).mkdir(parents=True, exist_ok=True)

	SUPPORTED_DICTIONARY_FORMATS = {
		'MDict (.mdx)': ['.mdx'],
		'StarDict (.ifo)': ['.ifo'],
		'DSL (.dsl/.dsl.dz)': ['.dsl', '.dz']
	}

	DICTIONARY_LIST_FILE = os.path.join(APP_RESOURCES_ROOT, 'dictionaries.json') # TODO: use the .config directory instead of .cache
	if os.path.isfile(DICTIONARY_LIST_FILE):
		# If the file exists, load the dictionary list from it
		with open(DICTIONARY_LIST_FILE) as dictionary_list_json:
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
			dictionary_list :'list[dict]' = json.load(dictionary_list_json)
	else:
		# If the file doesn't exist, create it
		dictionary_list :'list[dict]' = []
		with open(DICTIONARY_LIST_FILE, 'w') as dictionary_list_json:
			json.dump(dictionary_list, dictionary_list_json)
	
	HISTORY_FILE = os.path.join(APP_RESOURCES_ROOT, 'history.json')
	if os.path.isfile(HISTORY_FILE):
		with open(HISTORY_FILE) as history_json:
			# Just an array of strings
			lookup_history :'list[str]' = json.load(history_json) # Yeah, I know list is not a good idea for history, but you have to convert a deque to list to make it JSON serializable
	else:
		lookup_history :'list[str]' = []
		with open(HISTORY_FILE, 'w') as history_json:
			json.dump(lookup_history, history_json)

	MISC_CONFIGS_FILE = os.path.join(APP_RESOURCES_ROOT, 'misc.json') # for now it's just history size
	if os.path.isfile(MISC_CONFIGS_FILE):
		with open(MISC_CONFIGS_FILE) as misc_configs_json:
			misc_configs : 'dict[str, any]' = json.load(misc_configs_json)
	else:
		default_source_dir = os.path.join(APP_RESOURCES_ROOT, 'source')
		Path(default_source_dir).mkdir(parents=True, exist_ok=True)
		misc_configs : 'dict[str, any]' = {
			'history_size': 100,
			'sources': [
				default_source_dir
			]
		}
		with open(MISC_CONFIGS_FILE, 'w') as misc_configs_json:
			json.dump(misc_configs, misc_configs_json)

	SQLITE_DB_FILE = os.path.join(APP_RESOURCES_ROOT, 'dictionaries.db')

	WILDCARDS = {'^': '%', '+': '_'}
	
	def dictionary_info_valid(self, dictionary_info: 'dict') -> 'bool':
		"""
		Validate dictionary info according to the sample dictionary list above,
		And make sure the dictionary file exists.
		"""
		return all(key in dictionary_info.keys() for key in ['dictionary_display_name', 'dictionary_name', 'dictionary_format', 'dictionary_filename']) and dictionary_info['dictionary_format'] in self.SUPPORTED_DICTIONARY_FORMATS.keys() and os.access(dictionary_info['dictionary_filename'], os.R_OK) and os.path.isfile(dictionary_info['dictionary_filename']) and os.path.splitext(dictionary_info['dictionary_filename'])[1] in self.SUPPORTED_DICTIONARY_FORMATS[dictionary_info['dictionary_format']]

	def dictionary_format(self, filename: 'str') -> 'str | None':
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
		# Then check for DSL, whose filename has to be 'name.dsl' or 'name.dsl.dz'
		if extension == '.dsl':
			return 'DSL (.dsl/.dsl.dz)'
		if extension == '.dz' and os.path.splitext(base)[1] == '.dsl':
			return 'DSL (.dsl/.dsl.dz)'
		return None

	def save_history(self) -> 'None':
		with open(self.HISTORY_FILE, 'w') as history_json:
			json.dump(self.lookup_history, history_json)

	def save_dictionary_list(self) -> 'None':
		# Check DSL dictionaries, whose filenames must end with '.dz'.
		for dictionary_info in self.dictionary_list:
			if dictionary_info['dictionary_format'] == 'DSL (.dsl/.dsl.dz)' and not dictionary_info['dictionary_filename'].endswith('.dz'):
				dictionary_info['dictionary_filename'] += '.dz'
		with open(self.DICTIONARY_LIST_FILE, 'w') as dictionary_list_json:
			json.dump(self.dictionary_list, dictionary_list_json)

	def save_misc_configs(self) -> 'None':
		with open(self.MISC_CONFIGS_FILE, 'w') as misc_configs_json:
			json.dump(self.misc_configs, misc_configs_json)

	def source_valid(self, source: 'str') -> 'bool':
		"""
		Make sure the `source` is not an existing file.
		Create if not exists.
		"""
		if os.path.isfile(source):
			return False
		else:
			Path(source).mkdir(parents=True, exist_ok=True)
			return True

	def add_source(self, source: 'str') -> 'None':
		if not source in self.misc_configs['sources']:
			self.misc_configs['sources'].append(source)
			self.save_misc_configs()

	def remove_source(self, source: 'str') -> 'None':
		"""
		The directory itself won't be removed
		"""
		if source in self.misc_configs['sources']:
			self.misc_configs['sources'].remove(source)
			self.save_misc_configs()

	def scan_sources(self):
		"""
		Scan the sources and return a list of unregistered dictionaries' info.
		"""
		for source in self.misc_configs['sources']:
			for filename in os.listdir(source):
				full_filename = os.path.join(source, filename)
				if os.path.isfile(full_filename):
					dictionary_format = self.dictionary_format(full_filename)
					if dictionary_format:
						if not any(dictionary_info['dictionary_filename'] == full_filename for dictionary_info in self.dictionary_list):
							if filename.endswith('.dsl.dz'):
								name = filename[:-len('.dsl.dz')]
							else:
								name = os.path.splitext(filename)[0]
							yield {
								'dictionary_display_name': name,
								'dictionary_name': name,
								'dictionary_format': dictionary_format,
								'dictionary_filename': full_filename
							}

	def set_history_size(self, size: 'int') -> 'None':
		self.misc_configs['history_size'] = size
		self.save_misc_configs()

	def add_word_to_history(self, word: 'str') -> 'None':
		if word in self.lookup_history:
			self.lookup_history.remove(word)
		self.lookup_history.insert(0, word)
		if len(self.lookup_history) > int(self.misc_configs['history_size']):
			self.lookup_history.pop()
			logger.warning('History size exceeded, the oldest entry is removed')
		self.save_history()

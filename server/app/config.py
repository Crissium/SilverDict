import os
from pathlib import Path
import json


class Config:
	PORT = '2628' # deliberately the same as the default port of dictd, meaning to supersede it
				  # Well, certainly I have not reached its production level yet, but one day...
	HOMEDIR = os.getenv('HOME')
	CACHE_ROOT = os.path.join(HOMEDIR, '.cache', 'SilverDict') if HOMEDIR else '/tmp/SilverDict'
	Path(CACHE_ROOT).mkdir(parents=True, exist_ok=True)
	SUPPORTED_DICTIONARY_FORMATS = ['MDict (.mdx)', 'StarDict (.ifo)']

	DICTIONARY_LIST_FILE = os.path.join(CACHE_ROOT, 'dictionaries.json') # TODO: use the .config directory instead of .cache
	if os.path.isfile(DICTIONARY_LIST_FILE):
		# If the file exists, load the dictionary list from it
		with open(DICTIONARY_LIST_FILE) as dictionary_list_json:
			# a sample dictionary list :
			# [
			# 	{
			# 		"dictionary_display_name": "Oxford Dictionary of English",
			# 		"dictionary_name": "oxford_dictionary_of_english",
			# 		"dictionary_format": "MDict (.mdx)",
			# 		"dictionary_filename": "/run/media/ellis/Data/Documents/Dictionaries/oxford_dictionary_of_english.mdx"
			# 	},
			# 	{
			# 		"dictionary_display_name": "Collins English-French French-English Dictionary",
			# 		"dictionary_name": "collinse22f",
			# 		"dictionary_format": "MDict (.mdx)",
			# 		"dictionary_filename": "/run/media/ellis/Data/Documents/Dictionaries/collinse22f.mdx"
			# 	}
			# ]
			dictionary_list :'list[dict]' = json.load(dictionary_list_json)
	else:
		# If the file doesn't exist, create it
		dictionary_list :'list[dict]' = []
		with open(DICTIONARY_LIST_FILE, 'w') as dictionary_list_json:
			json.dump(dictionary_list, dictionary_list_json)
	
	HISTORY_FILE = os.path.join(CACHE_ROOT, 'history.json')
	if os.path.isfile(HISTORY_FILE):
		with open(HISTORY_FILE) as history_json:
			# Just an array of strings
			lookup_history :'list[str]' = json.load(history_json) # Yeah, I know list is not a good idea for history, but you have to convert a deque to list to make it JSON serializable
	else:
		lookup_history :'list[str]' = []
		with open(HISTORY_FILE, 'w') as history_json:
			json.dump(lookup_history, history_json)

	MISC_CONFIGS_FILE = os.path.join(CACHE_ROOT, 'misc.json') # for now it's just history size
	if os.path.isfile(MISC_CONFIGS_FILE):
		with open(MISC_CONFIGS_FILE) as misc_configs_json:
			# {"history_size": 100}
			misc_configs : 'dict[str, any]' = json.load(misc_configs_json)
	else:
		misc_configs : 'dict[str, any]' = {'history_size': 100}
		with open(MISC_CONFIGS_FILE, 'w') as misc_configs_json:
			json.dump(misc_configs, misc_configs_json)
	
	SQLITE_DB_FILE = os.path.join(CACHE_ROOT, 'dictionaries.db')
	
	def dictionary_info_valid(self, dictionary_info: 'dict') -> 'bool':
		"""
		Validate dictionary info according to the sample dictionary list above,
		And make sure the dictionary file exists.
		"""
		return all(key in dictionary_info.keys() for key in ['dictionary_display_name', 'dictionary_name', 'dictionary_format', 'dictionary_filename']) and dictionary_info['dictionary_format'] in self.SUPPORTED_DICTIONARY_FORMATS and os.path.isfile(dictionary_info['dictionary_filename'])
	
	def save_history(self) -> 'None':
		with open(self.HISTORY_FILE, 'w') as history_json:
			json.dump(self.lookup_history, history_json)

	def save_misc_configs(self) -> 'None':
		with open(self.MISC_CONFIGS_FILE, 'w') as misc_configs_json:
			json.dump(self.misc_configs, misc_configs_json)

	def add_word_to_history(self, word: 'str') -> 'None':
		if word in self.lookup_history:
			self.lookup_history.remove(word)
		self.lookup_history.insert(0, word)
		if len(self.lookup_history) > int(self.misc_configs['history_size']):
			self.lookup_history.pop()
		self.save_history()

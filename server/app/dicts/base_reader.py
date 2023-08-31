import abc
import os
from pathlib import Path
import unicodedata
from ..config import Config


class BaseReader(abc.ABC):
	"""
	Abstract base class for reading dictionaries.
	"""
	_CACHE_ROOT = Config.CACHE_ROOT
	_ARTICLE_SEPARATOR = '\n<hr>\n'

	def __init__(self,
	      		 name: 'str',
				 filename: 'str',
				 display_name: 'str',
				 dictionary_exists: 'function',
				 add_etry: 'function',
				 commit: 'function',
				 get_entries: 'function',
				 create_index: 'function',
				 drop_index: 'function') -> None:
		"""
		:param name: the name of the dictionary, deduced by removing the extension(s) from the filename, used internally
		:param filename: the name of the main file of the dictionary with extension(s)
		:param display_name: the name of the dictionary as it should be displayed to the user
		:param dictionary_exists: dictionary_exists(dictionary_name: 'str') -> 'bool'
		:param add_entry: add_entry(key: 'str', dictionary_name: 'str', word: 'str', offset: 'int', size: 'int') -> 'None'
		:param get_entries: get_entries(key: 'str', dictionary_name: 'str') -> 'list[tuple[str, int, int]]'
		:param create_index: thin wrapper around the SQL statement
		:param drop_index: thin wrapper around the SQL statement
		"""
		self.name = name
		self.filename = filename
		self.display_name = display_name
		self.dictionary_exists = dictionary_exists
		self.add_entry = add_etry
		self.commit = commit
		self.get_entries = get_entries
		self.create_index = create_index
		self.drop_index = drop_index

	def _write_to_cache_dir(self, relative_path: 'str', data: 'bytes') -> None:
		absolute_path = os.path.join(self._CACHE_ROOT, relative_path)
		Path(os.path.dirname(absolute_path)).mkdir(parents=True, exist_ok=True)
		with open(absolute_path, 'wb') as f:
			# print('Writing to %s' % absolute_path)
			f.write(data)

	@staticmethod
	def strip_diacritics(text: 'str') -> 'str':
		"""
		Tested on:
		['r̀r̂r̃r̈rŕřt̀t̂ẗţỳỹẙyy̎ýÿŷp̂p̈s̀s̃s̈s̊ss̸śŝŞşšd̂d̃d̈ďdḑf̈f̸g̀g̃g̈gģq́ĝǧḧĥj̈jḱk̂k̈k̸ǩl̂l̃l̈Łłẅẍc̃c̈c̊cc̸Çççćĉčv̂v̈vv̸b́b̧ǹn̂n̈n̊nńņňñm̀m̂m̃m̈m̊m̌ǵß', 'Česká republika', 'Bonjour ! Je suis français ! Et toi ? Je suis étudient', 'Καλημέρα! Είμαι Έλληνας! Εσύ;', '中文测试', '日本語テスト', '한국어 테스트', 'اللغة العربية اختبار', 'עברית בדיקה', 'русский тест', 'український тест', 'Charlotte Brontë', 'œ', 'ß', 'ø', 'ö', 'ð', 'ü', 'µ', 'ñ', 'æ']
		Seems that it works well for Latin, Greek and Cyrillic scripts. In addition, it leaves ligatures alone, as well as CJK characters, which is exactly what we want (I'd rather have œ expanded, though). I do not know about Arabic, Hebrew, and other scripts, but I think it should work well for them too.
		"""
		return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
	
	@staticmethod
	def remove_punctuation_and_spaces(text: 'str') -> 'str':
		"""
		Removes all punctuation and spaces from the given text.
		"""
		return ''.join(c for c in text if unicodedata.category(c)[0] not in ['P', 'Z'])
	
	@staticmethod
	def simplify(text: 'str') -> 'str':
		"""
		Removes accents and punctuation, and converts to lowercase.
		"""
		return BaseReader.remove_punctuation_and_spaces(BaseReader.strip_diacritics(text)).lower()

	# Superceded by the database
	# @abc.abstractmethod
	# def entry_list(self) -> 'list[str]':
	# 	"""
	# 	Returns the list of entries in the dictionary.
	# 	"""
	# 	pass

	# @abc.abstractmethod
	# def entry_list_simplified(self) -> 'list[str]':
	# 	"""
	# 	Returns the list of entries in the dictionary, in lowercase and without accents.
	# 	"""
	# 	pass

	# @abc.abstractmethod
	# def entry_count(self) -> 'int':
	# 	"""
	# 	Returns the number of entries in the dictionary.
	# 	"""
	# 	pass

	# @abc.abstractmethod
	# def entry_exists(self, entry: 'str') -> 'bool':
	# 	"""
	# 	Returns whether the given entry exists in the dictionary.
	# 	"""
	# 	pass

	@abc.abstractmethod
	def entry_definition(self, entry: 'str') -> 'str':
		"""
		Returns the definition of the given entry.
		"""
		pass
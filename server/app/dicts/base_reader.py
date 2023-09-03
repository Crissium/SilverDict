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
				 display_name: 'str') -> None:
		"""
		:param name: the name of the dictionary, deduced by removing the extension(s) from the filename, used internally
		:param filename: the name of the main file of the dictionary with extension(s)
		:param display_name: the name of the dictionary as it should be displayed to the user
		"""
		self.name = name
		self.filename = filename
		self.display_name = display_name

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
		['Česká republika', 'Bonjour ! Je suis français ! Et toi ? Je suis étudiant', 'Καλημέρα! Είμαι Έλληνας! Εσύ;', '中文测试', '日本語テスト', '한국어 테스트', 'اللغة العربية اختبار', 'עברית בדיקה', 'русский тест', 'український тест', 'Charlotte Brontë', 'œ', 'ß', 'ø', 'ö', 'ð', 'ü', 'µ', 'ñ', 'æ']
		Seems that it works well for Latin, Greek and Cyrillic scripts. In addition, it leaves ligatures alone, as well as CJK characters, which is exactly what we want (I'd rather have œ expanded, though). I do not know about Arabic, Hebrew, and other scripts, but I think it should work well for them too.
		"""
		return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn' and not unicodedata.combining(c))
	
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
		return BaseReader.remove_punctuation_and_spaces(BaseReader.strip_diacritics(text)).casefold()

	@abc.abstractmethod
	def entry_definition(self, entry: 'str') -> 'str':
		"""
		Returns the definition of the given entry.
		"""
		pass
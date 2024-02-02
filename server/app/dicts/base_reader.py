import abc
import unicodedata
from ..settings import Settings


class BaseReader(abc.ABC):
	"""
	Abstract base class for reading dictionaries.
	"""
	_CACHE_ROOT = Settings.CACHE_ROOT
	_ARTICLE_SEPARATOR = '\n<hr />\n'

	@staticmethod
	def strip_diacritics(text: str) -> str:
		return ''.join(c
					   for c in unicodedata.normalize('NFKD', text)
					   if unicodedata.category(c) != 'Mn' and not unicodedata.combining(c))

	@staticmethod
	def remove_punctuation_and_spaces(text: str) -> str:
		return ''.join(c
					   for c in text
					   if unicodedata.category(c)[0] not in ['P', 'Z'])

	@staticmethod
	def expand_ligatures(text: str) -> str:
		"""
		Expands the ligatures 'œ' and 'æ' to their two-letter equivalent.
		"""
		return text.replace('œ', 'oe').replace('æ', 'ae').replace('Æ', 'AE').replace('Œ', 'OE')

	@staticmethod
	def simplify(text: str) -> str:
		"""
		Removes accents and punctuation, expand ligatures, and converts to lowercase.
		"""
		text = BaseReader.strip_diacritics(text)
		text = BaseReader.remove_punctuation_and_spaces(text)
		text = BaseReader.expand_ligatures(text)
		return text.casefold()

	def __init__(self,
				 name: str,
				 filename: str,
				 display_name: str) -> None:
		"""
		:param name: the name of the dictionary, deduced by removing the extension(s) from the filename, used internally
		:param filename: the name of the main file of the dictionary with extension(s)
		:param display_name: the name of the dictionary as it should be displayed to the user
		"""
		self.name = name
		self.filename = filename
		self.display_name = display_name

	@abc.abstractmethod
	def get_definition_by_key(self, entry: str) -> str:
		"""
		:param entry: the entry to look up, must be simplified
		:return: the definition of the given entry (match by key only; that is, ignore case and diacritics).
		"""
		pass

	def get_definitions_by_keys(self, entries: list[str]) -> list[str]:
		"""
		:param entries: the entries to look up, must be simplified
		:return: the definitions of the given entries (match by key only; that is, ignore case and diacritics).
		"""
		return self._ARTICLE_SEPARATOR.join([self.get_definition_by_key(entry) for entry in entries])

	@abc.abstractmethod
	def get_definition_by_word(self, headword: str) -> str:
		"""
		:param headword: the headword to look up, must not be simplified
		:return: the definition of the given headword.
		"""
		pass

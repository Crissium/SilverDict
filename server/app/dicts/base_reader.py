import abc
import os
from pathlib import Path
from ..config import Config


class BaseReader(abc.ABC):
	"""
	Abstract base class for reading dictionaries.
	"""
	_CACHE_ROOT = Config.CACHE_ROOT

	def __init__(self, filename: 'str', display_name: 'str') -> None:
		self.filename = filename
		self.display_name = display_name

	def _write_to_cache_dir(self, relative_path: 'str', data: 'bytes') -> None:
		absolute_path = os.path.join(self._CACHE_ROOT, relative_path)
		Path(os.path.dirname(absolute_path)).mkdir(parents=True, exist_ok=True)
		with open(absolute_path, 'wb') as f:
			# print('Writing to %s' % absolute_path)
			f.write(data)

	@abc.abstractmethod
	def entry_list(self) -> 'list[str]':
		"""
		Returns the list of entries in the dictionary.
		"""
		pass

	@abc.abstractmethod
	def entry_count(self) -> 'int':
		"""
		Returns the number of entries in the dictionary.
		"""
		pass

	@abc.abstractmethod
	def entry_exists(self, entry: 'str') -> 'bool':
		"""
		Returns whether the given entry exists in the dictionary.
		"""
		pass

	@abc.abstractmethod
	def entry_definition(self, entry: 'str') -> 'str':
		"""
		Returns the definition of the given entry.
		"""
		pass
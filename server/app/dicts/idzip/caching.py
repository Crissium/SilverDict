"""
sample caches to use
"""
from random import randint

LUCKY_SIZE = 32


class OneItemCache(object):
	"""
	The simplest LRU cache.

	Sane default cache

	good for cases where you:
			open a file
			seek to an offset
			read a few bytes
			process some things
			read a few more bytes
			etc.

	"""
	def __init__(self):
		self.key = None
		self.value = None

	def get(self, key):
		if self.key == key:
			return self.value
		return None

	def put(self, key, value):
		self.key = key
		self.value = value


class ZeroCache(object):
	"""
	disables the cache

	for those with no memory but plenty of CPU cycles

	omits tossing the string in memory if it won't be used.

	good for cases where you:
			open the file,
			seek to an offset,
			read some bytes,
			close the file

	worse than OneItem in every case outside the good case.
	"""
	def __init__(self):
		return

	def get(self, key):
		return None

	def put(self, key, value):
		return None


class LuckyCache(object):
	"""
	Implements a random cache of size LUCKY_SIZE
	see test/test_lucky_cache.py for settings

	for those with extra memory but wasted CPU cycles

	only useful if you intend to thrash about the file.

	sequential reads should use OneItemCache
	"""
	def __init__(self):
		self._cache = {}
		self._cache_index = {}
		for x in range(-LUCKY_SIZE, 0):  # negative because caches positive ints
			self._cache[x] = None
			self._cache_index[x] = x
		return None

	def get(self, key):
		return self._cache.get(key, None)

	def put(self, key, value):
		if key not in self._cache:
			unlucky_index = randint(-LUCKY_SIZE, -1)
			unlucky_key = self._cache_index[unlucky_index]
			self._cache.pop(unlucky_key)
			self._cache[key] = value
			self._cache_index[unlucky_index] = key
		return None

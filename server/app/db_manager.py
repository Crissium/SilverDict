# import sqlite3
from sqlite3worker import Sqlite3Worker
import os
from .config import Config


class DatabaseManager:
	"""
	SQLite is added at a later point of development. For fear of breaking
	existing code, it will only be used to store the entries' keys, offsets,
	sizes, etc.
	"""
	def __init__(self) -> 'None':
		self.worker = Sqlite3Worker(Config.SQLITE_DB_FILE)

		self.worker.execute('''create table if not exists entries (
			key text, -- the entry in lowercase and without accents
		    dictionary_name text, -- filename of the dictionary
		    word text, -- the entry as it appears in the dictionary
		    offset integer, -- offset of the entry in the dictionary file
		    size integer -- size of the definition in bytes
		)''')

	def dictionary_exists(self, dictionary_name: 'str') -> 'bool':
		result = self.worker.execute('select count(*) from entries where dictionary_name = ?', (dictionary_name,))
		# return self.worker.fetchone()[0] > 0
		return result[0][0] > 0

	def add_entry(self, key: 'str', dictionary_name: 'str', word: 'str', offset: 'int', size: 'int') -> 'None':
		"Commit manually!"
		self.worker.execute('insert into entries values (?, ?, ?, ?, ?)', (key, dictionary_name, word, offset, size))
	
	def commit(self) -> 'None':
		pass
		# self.worker.commit()
		# commits are done in batches of 100 queries?

	def get_entry(self, key: 'str', dictionary_name: 'str') -> 'list[tuple[str, int, int]]':
		result = self.worker.execute('select word, offset, size from entries where key = ? and dictionary_name = ?', (key, dictionary_name))
		return result
		# return self.worker.fetchall()

	def delete_dictionary(self, dictionary_name: 'str') -> 'None':
		self.worker.execute('delete from entries where dictionary_name = ?', (dictionary_name,))
		# self._conn.commit()

	def create_index(self) -> 'None':
		self.worker.execute('create index idx_entry_key on entries (key)')
		self.worker.execute('create index idx_entry_word on entries (word)')
	
	def drop_index(self) -> 'None':
		self.worker.execute('drop index if exists idx_entry_key')
		self.worker.execute('drop index if exists idx_entry_word')
	
	def select_entries_beginning_with(self, key: 'str', dictionary_name: 'str') -> 'list[str]':
		"""
		Return the first ten entries (word) in the dictionary that begin with key.
		"""
		result = self.worker.execute('select distinct word from entries where key like ? and dictionary_name = ? limit 10', (key + '%', dictionary_name))
		return [row[0] for row in result]
	
	def select_entries_containing(self, key: 'str', dictionary_name: 'str', words_already_found: 'list[str]') -> 'list[tuple[str]]':
		"""
		Return the first 10 - len(words_already_found) entries (key, word) in the dictionary that contain key.
		"""
		num_words = 10 - len(words_already_found)
		result = self.worker.execute('select distinct key, word from entries where key like ? and dictionary_name = ? and word not in (%s) limit ?' % ','.join('?' * len(words_already_found)), ('%' + key + '%', dictionary_name, *words_already_found, num_words))
		return [row[0] for row in result]
	
	def entry_exists_in_dictionary(self, word: 'str', dictionary_name: 'str') -> 'bool':
		result = self.worker.execute('select count(*) from entries where word = ? and dictionary_name = ?', (word, dictionary_name))
		return result[0][0] > 0

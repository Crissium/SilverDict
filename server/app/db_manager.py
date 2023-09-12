"""
A custom database manager.
I do not use SQLAlchemy because I have not figured out how can I create and drop indexes as I need.
After all, it is efficient, thread-safe, and easy to use.
"""

"""
Performance note:
dictionary_exists(): very good with idx_dictname
get_entries(): very good with idx_key_dictname_word
select_entries_like(): I don't care, GoldenDict is also quite slow in this respect
entry_exists_in_dictionary(), entry_exists_in_dictionaries(): very good with idx_key_dictname_word

If idx_dictname exists, select_entries_beginning_with() would use it instead of idx_key_dictname_word(), which slows things down. Anyway dictionary_exists() is only used when initialising a dictionary reader, so it is not a big deal.

---

What really matters is select_entries_beginning_with():

Should record the highest UTF-8 character in the dictionary and use it to perform optimisation by hand:
select * from entries where key like "key%" => select * from entries where key >= "key" and key < "keyzzzzzzz";

But now, experimentally, I am using a lazy approach: just key < "key𱍊" (U+3134A, decimal 201546)

And select_entries_containing() should be optimised with an inverted-key table.
"""

import sqlite3
import threading
from .settings import Settings

local_storage = threading.local()

def get_connection() -> 'sqlite3.Connection':
	if not hasattr(local_storage, 'connection'):
		local_storage.connection = sqlite3.connect(Settings.SQLITE_DB_FILE)
	return local_storage.connection

def get_cursor() -> 'sqlite3.Cursor':
	if not hasattr(local_storage, 'cursor'):
		local_storage.cursor = get_connection().cursor()
	return local_storage.cursor

def create_table_entries() -> 'None':
	cursor = get_cursor()
	cursor.execute('''create table if not exists entries (
		key text, -- the entry in lowercase and without accents
	    dictionary_name text, -- filename of the dictionary
	    word text, -- the entry as it appears in the dictionary
	    offset integer, -- offset of the entry in the dictionary file
	    size integer -- size of the definition in bytes
	)''')
	get_connection().commit()

def dictionary_exists(dictionary_name: 'str') -> 'bool':
	cursor = get_cursor()
	cursor.execute('select count(*) from entries where dictionary_name = ?', (dictionary_name,))
	return cursor.fetchone()[0] > 0

def add_entry(key: 'str', dictionary_name: 'str', word: 'str', offset: 'int', size: 'int') -> 'None':
	"Commit manually!"
	cursor = get_cursor()
	cursor.execute('insert into entries values (?, ?, ?, ?, ?)', (key, dictionary_name, word, offset, size))

def commit() -> 'None':
	get_connection().commit()

def get_entries(key: 'str', dictionary_name: 'str') -> 'list[tuple[str, int, int]]':
	"""
	Returns a list of (word, offset, size).
	"""
	cursor = get_cursor()
	cursor.execute('select word, offset, size from entries where key = ? and dictionary_name = ?', (key, dictionary_name))
	return cursor.fetchall()

def delete_dictionary(dictionary_name: 'str') -> 'None':
	cursor = get_cursor()
	cursor.execute('delete from entries where dictionary_name = ?', (dictionary_name,))
	get_connection().commit()

def create_index() -> 'None':
	cursor = get_cursor()
	# cursor.execute('create index idx_dictname on entries (dictionary_name)') # This helps with dictionary_exists()
	# cursor.execute('create index idx_key_dictname on entries (key, dictionary_name)')
	# cursor.execute('create index idx_key on entries (key)')
	cursor.execute('create index idx_key_dictname_word on entries (key, dictionary_name, word)') # I'll be d-ned if this all covering index ain't work either
	get_connection().commit()

def drop_index() -> 'None':
	cursor = get_cursor()
	# cursor.execute('drop index if exists idx_dictname')
	# cursor.execute('drop index if exists idx_key_dictname')
	# cursor.execute('drop index if exists idx_key')
	cursor.execute('drop index if exists idx_key_dictname_word')
	get_connection().commit()

def select_entries_beginning_with(key: 'str', names_dictionaries: 'list[str]', limit: 'int') -> 'list[str]':
	"""
	Return the first ten entries (word) in the dictionaries that begin with key.
	"""
	cursor = get_cursor()
	cursor.execute('select distinct word from entries where key >= ? and key < ? and dictionary_name in (%s) order by key limit ?' % ','.join('?' * len(names_dictionaries)), (key, key + '\U0003134A', *names_dictionaries, limit))
	return [row[0] for row in cursor.fetchall()]

def select_entries_containing(key: 'str', names_dictionaries: 'list[str]', words_already_found: 'list[str]', limit: 'int') -> 'list[str]':
	"""
	Return the first num_suggestions - len(words_already_found) entries (word) in the dictionaries that contain key.
	"""
	num_words = limit - len(words_already_found)
	cursor = get_cursor()
	cursor.execute('select distinct word from entries where key like ? and dictionary_name in (%s) and word not in (%s) order by key limit ?' % (','.join('?' * len(names_dictionaries)), ','.join('?' * len(words_already_found))), ('%' + key + '%', *names_dictionaries, *words_already_found, num_words))
	return [row[0] for row in cursor.fetchall()]

def select_entries_like(key: 'str', names_dictionaries: 'list[str]', limit: 'int') -> 'list[str]':
	"""
	Return the first ten entries matched.
	"""
	cursor = get_cursor()
	cursor.execute('select distinct word from entries where key like ? and dictionary_name in (%s) order by key limit ?' % ','.join('?' * len(names_dictionaries)), (key, *names_dictionaries, limit))
	return [row[0] for row in cursor.fetchall()]

def entry_exists_in_dictionary(key: 'str', dictionary_name: 'str') -> 'bool':
	cursor = get_cursor()
	cursor.execute('select count(*) from entries where key = ? and dictionary_name = ?', (key, dictionary_name))
	return cursor.fetchone()[0] > 0

def entry_exists_in_dictionaries(key: 'str', names_dictionaries : 'list[str]') -> 'bool':
	cursor = get_cursor()
	cursor.execute('select count(*) from entries where key = ? and dictionary_name in (%s)' % ','.join('?' * len(names_dictionaries)), (key, *names_dictionaries))
	return cursor.fetchone()[0] > 0
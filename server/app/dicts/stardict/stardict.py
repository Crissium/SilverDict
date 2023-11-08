# This file was copied from:
# https://github.com/pysuxing/python-stardict
# Copyright (c) Su Xing <pysuxing@gmail.com>
# License GPL-3.0
# License unchanged for the modifications:
# Copyright (C) 2022 J.F.Dockes
# Copyright (C) 2023 Yi Xing <blandilyte@gmail.com>

import struct
import gzip
import os
import idzip

class IfoFileException(Exception):
	"""
	Exception while parsing the .ifo file.
	Now version error in .ifo file is the only case raising this exception.
	"""
	
	def __init__(self, description: 'str' = 'IfoFileException raised') -> 'None':
		"""
		Constructor from a description string.
		
		Arguments:
		- `description`: a string describing the exception condition.
		"""
		self._description = description

	def __str__(self) -> 'str':
		"""
		__str__ method, return the description of exception occured.
		"""
		return self._description

class IfoFileReader:
	"""
	Read infomation from .ifo file and parse the infomation a dictionary.
	The structure of the dictionary is shown below:
	{key, value}
	"""
	
	def __init__(self, filename: 'str') -> 'None':
		"""
		Constructor from filename.
		
		Arguments:
		- `filename`: the filename of .ifo file of stardict.
		May raise IfoFileException during initialization.
		"""
		self._ifo = dict()
		with open(filename) as ifo_file:
			self._ifo['dict_title'] = ifo_file.readline() # dictionary title
			line = ifo_file.readline() # version info
			key, equal, value = line.partition('=')
			key = key.strip()
			value = value.strip()
			# check version info, raise an IfoFileException if error encounted
			if key != 'version':
				raise IfoFileException('Version info expected in the second line of {!r:s}!'.
									   format(filename))
			if value != '2.4.2' and value != '3.0.0':
				raise IfoFileException('Version expected to be either 2.4.2 or 3.0.0, but {!r:s} '
									   "read!".format(value))
			self._ifo[key] = value
			# read in other infomation in the file
			for line in ifo_file:
				key, equal, value = line.partition('=')
				key = key.strip()
				value = value.strip()
				self._ifo[key] = value
			# check if idxoffsetbits should be discarded due to version info
			if self._ifo['version'] == '3.0.0' and 'idxoffsetbits' in self._ifo:
				del self._ifo['version']

	def get_ifo(self, key: 'str') -> 'bool | str':
		"""
		Get configuration value.
		
		Arguments:
		- `key`: configuration option name
		Return:
		- configuration value corresponding to the specified key if exists, otherwise False.
		"""
		if key not in self._ifo:
			return False
		return self._ifo[key]


class IdxFileReader:
	"""
	Read dictionary indexes from the .idx file and store the indexes in a list and a dictionary.
	The list contains each entry in the .idx file, with subscript indicating the entry's origin 
	index in .idx file. The dictionary is indexed by word name, and the value is an integer or a 
	list of integers pointing to the entry in the list.
	"""
	
	def __init__(self, filename: 'str', index_offset_bits : 'int' = 32) -> 'None':
		"""
		Arguments:
		- `filename`: the filename of .idx file of stardict.
		- `index_offset_bits`: the offset field length in bits.
		"""
		compressed = os.path.splitext(filename)[1] == '.gz'
		if compressed:
			with gzip.open(filename, 'rb') as index_file:
				self._content = index_file.read()
		else:
			with open(filename, 'rb') as index_file:
				self._content = index_file.read()
		self._offset = 0
		self._index = 0
		self._index_offset_bits = index_offset_bits
		self._word_idx = dict()
		self._index_idx = list()
		for word_str, word_data_offset, word_data_size, index in self:
			self._index_idx.append((word_str, word_data_offset, word_data_size))
			if word_str in self._word_idx:
				if isinstance(self._word_idx[word_str], list):
					self._word_idx[word_str].append(len(self._index_idx)-1)
				else:
					self._word_idx[word_str] = [self._word_idx[word_str], len(self._index_idx)-1]
			else:
				self._word_idx[word_str] = len(self._index_idx)-1
		del self._content
		del self._index_offset_bits
		del self._index

	def __iter__(self) -> 'IdxFileReader':
		return self

	def __next__(self) -> 'tuple[bytes, int, int, int]':
		if self._offset == len(self._content):
			raise StopIteration
		word_data_offset = 0
		word_data_size = 0
		end = self._content.find(b'\0', self._offset)
		word_str = self._content[self._offset: end]
		self._offset = end+1
		if self._index_offset_bits == 64:
			word_data_offset, = struct.unpack('!I', self._content[self._offset:self._offset+8])
			self._offset += 8
		elif self._index_offset_bits == 32:
			word_data_offset, = struct.unpack('!I', self._content[self._offset:self._offset+4])
			self._offset += 4
		else:
			raise ValueError
		word_data_size, = struct.unpack('!I', self._content[self._offset:self._offset+4])
		self._offset += 4
		self._index += 1
		return (word_str, word_data_offset, word_data_size, self._index)

	def get_index_by_num(self, number: 'int') -> 'tuple[bytes, int, int]':
		"""
		Get index infomation of a specified entry in .idx file by origin index.
		May raise IndexError if number is out of range.
		
		Arguments:
		- `number`: the origin index of the entry in .idx file
		Return:
		A tuple in form of (word_str, word_data_offset, word_data_size)
		"""
		if number >= len(self._index_idx):
			raise IndexError("Index out of range! Acessing the {:d} index but totally {:d}".
							 format(number, len(self._index_idx)))
		return self._index_idx[number]

	def get_index_by_word(self, word_str: 'bytes') -> 'bool | list[tuple[int, int]]':
		"""
		Get index infomation of a specified word entry.
		
		Arguments:
		- `word_str`: name of word entry.
		Return:
		Index infomation corresponding to the specified word if exists, otherwise False.
		The index infomation returned is a list of tuples, in form of:
		[(word_data_offset, word_data_size) ...]
		"""
		if word_str not in self._word_idx:
			return False
		number =  self._word_idx[word_str]
		index = list()
		if isinstance(number, list):
			for n in number:
				index.append(self._index_idx[n][1:])
		else:
			index.append(self._index_idx[number][1:])
		return index


class SynFileReader:
	@staticmethod
	def uint32_from_bytes(bs: 'bytes') -> 'int':
		return struct.unpack('>I', bs)[0]

	def __init__(self, filename: 'str') -> 'None':
		"""
		Constructor.

		Arguments:
		- `filename`: The filename of .syn file of stardict.
		"""
		self.syn_dict = dict()

		if os.path.isfile(filename):
			with open(filename, 'rb') as _file:
				syn_bytes = _file.read()
		elif os.path.isfile(filename + '.dz'):
			with idzip.open(filename + '.dz') as _zfile:
				syn_bytes = _zfile.read()
		else:
			self.syn_dict = dict()
			return

		self.syn_dict: 'dict[int, list[str]]' = {}
		pos = 0
		while pos < len(syn_bytes):
			beg = pos
			pos = syn_bytes.find(b'\x00', beg)
			if pos < 0:
				break
			b_alt = syn_bytes[beg:pos]  # b_alt is bytes
			pos += 1
			if pos + 4 > len(syn_bytes):
				break
			entry_index = self.uint32_from_bytes(syn_bytes[pos:pos + 4])
			pos += 4

			s_alt = b_alt.decode('utf-8')
			# s_alt is str
			try:
				self.syn_dict[entry_index].append(s_alt)
			except KeyError:
				self.syn_dict[entry_index] = [s_alt]


class DictFileReader:
	"""
	Read the .dict file, store the data in memory for querying.
	"""

	def __init__(self, filename: 'str', dict_ifo: 'IfoFileReader', dict_index: 'IdxFileReader', load_content_into_memory: 'bool'=False) -> 'None':
		"""
		Constructor.
		
		Arguments:
		- `filename`: filename of .dict file.
		- `dict_ifo`: IfoFileReader object.
		- `dict_index`: IdxFileReader object.
		"""
		self._dict_ifo = dict_ifo
		self._dict_index = dict_index
		self._offset = 0
		self._loaded_content_into_memory = load_content_into_memory
		compressed = os.path.splitext(filename)[1] == '.dz'
		if load_content_into_memory:
			if compressed:
				with idzip.open(filename) as f:
					self._content = f.read()
			else:
				with open(filename, 'rb') as f:
					self._content = f.read()
		else:
			if compressed:
				self.fd = idzip.open(filename)
			else:
				self.fd = open(filename, 'rb')
	
	def close(self) -> 'None':
		if not self._loaded_content_into_memory:
			self.fd.close()

	def _get_dict_by_offset_size_internal(self, offset: 'int', size: 'int', sametypesequence: 'str', result: 'list') -> 'None':
		if self._loaded_content_into_memory:
			self._dict_file = self._content[offset:(offset+size)]
		else:
			self.fd.seek(offset)
			self._dict_file = self.fd.read(size)
		if sametypesequence:
			result.append(self._get_entry_sametypesequence(0, size))
		else:
			result.append(self._get_entry(0, size))
			
	def get_dict_by_offset_size(self, offset: 'int', size: 'int') -> 'list':
		sametypesequence = self._dict_ifo.get_ifo('sametypesequence')
		result = list()
		self._get_dict_by_offset_size_internal(offset, size, sametypesequence, result)
		return result
		
	# def get_dict_by_word(self, word):
	# 	"""Get the word's dictionary data by it's name.
		
	# 	Arguments:
	# 	- `word`: word name.
	# 	Return:
	# 	The specified word's dictionary data, in form of dict as below:
	# 	{type_identifier: infomation, ...}
	# 	in which type_identifier can be any character in "mlgtxykwhnrWP".
	# 	"""
	# 	if type(word) != type(b""):
	# 		word = word.encode("utf-8")
	# 	indexes = self._dict_index.get_index_by_word(word)
	# 	if indexes == False:
	# 		return False
	# 	sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
	# 	result = list()
	# 	for index in indexes:
	# 		self._get_dict_by_offset_size_internal(index[0], index[1], sametypesequence, result)
	# 	return result

	# def get_dict_by_index(self, index):
	# 	"""Get the word's dictionary data by it's index infomation.
		
	# 	Arguments:
	# 	- `index`: index of a word entrt in .idx file.'
	# 	Return:
	# 	The specified word's dictionary data, in form of dict as below:
	# 	{type_identifier: infomation, ...}
	# 	in which type_identifier can be any character in "mlgtxykwhnrWP".
	# 	"""
	# 	word, offset, size = self._dict_index.get_index_by_num(index)
	# 	sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
	# 	self.fd.seek(offset)            
	# 	self._dict_file = self.fd.read(size)
	# 	if sametypesequence:
	# 		return self._get_entry_sametypesequence(0, size)
	# 	else:
	# 		return self._get_entry(0, size)

	def _get_entry(self, offset: 'int', size: 'int') -> 'dict':
		result = dict()
		read_size = 0
		start_offset = offset
		while read_size < size:
			type_identifier = struct.unpack('!c')
			if type_identifier in 'mlgtxykwhnr':
				result[type_identifier],offset = self._get_entry_field_null_trail(offset)
			else:
				result[type_identifier],offset = self._get_entry_field_size(offset, None)
			read_size = offset - start_offset
		return result
		
	def _get_entry_sametypesequence(self, offset: 'int', size: 'int') -> 'dict':
		start_offset = offset
		result = dict()
		sametypesequence = self._dict_ifo.get_ifo('sametypesequence')
		for k in range(0, len(sametypesequence)):
			if sametypesequence[k] in 'mlgtxykwhnr':
				if k == len(sametypesequence)-1:
					result[sametypesequence[k]],offset = \
						self._get_entry_field_size(offset, size - (offset - start_offset))
				else:
					result[sametypesequence[k]],offset = self._get_entry_field_null_trail(offset)
			elif sametypesequence[k] in 'WP':
				if k == len(sametypesequence)-1:
					result[sametypesequence[k]],offset = \
						self._get_entry_field_size(offset, size - (offset - start_offset))
				else:
					result[sametypesequence[k]],offset = self._get_entry_field_size(offset, None)
		return result

	def _get_entry_field_null_trail(self, offset: 'int') -> 'tuple[bytes, int]':
		end = self._dict_file.find('\0', offset)
		result = self._dict_file[offset:end]
		return (result, end + 1)
		
	def _get_entry_field_size(self, offset: 'int', size: 'int') -> 'tuple[bytes, int]':
		if size is None:
			size = struct.unpack('!I', self._dict_file[offset:(offset+4)])[0]
			offset += 4
		result = self._dict_file[offset:(offset+size)]
		return (result, offset + size)

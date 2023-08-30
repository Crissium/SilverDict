# This file was copied from:
# https://github.com/pysuxing/python-stardict
# Copyright (c) Su Xing <pysuxing@gmail.com>
# License GPL-3.0
# License unchanged for the modifications:
# Copyright (C) 2022 J.F.Dockes

import struct
import gzip
import sys
import os

from .. import idzip

class IfoFileException(Exception):
	"""Exception while parsing the .ifo file.
	Now version error in .ifo file is the only case raising this exception.
	"""
	
	def __init__(self, description = "IfoFileException raised"):
		"""Constructor from a description string.
		
		Arguments:
		- `description`: a string describing the exception condition.
		"""
		self._description = description
	def __str__(self):
		"""__str__ method, return the description of exception occured.
		
		"""
		return self._description
		

class IfoFileReader(object):
	"""Read infomation from .ifo file and parse the infomation a dictionary.
	The structure of the dictionary is shown below:
	{key, value}
	"""
	
	def __init__(self, filename):
		"""Constructor from filename.
		
		Arguments:
		- `filename`: the filename of .ifo file of stardict.
		May raise IfoFileException during initialization.
		"""
		self._ifo = dict()
		with open(filename, "r") as ifo_file:
			self._ifo["dict_title"] = ifo_file.readline() # dictionary title
			line = ifo_file.readline() # version info
			key, equal, value = line.partition("=")
			key = key.strip()
			value = value.strip()
			# check version info, raise an IfoFileException if error encounted
			if key != "version":
				raise IfoFileException("Version info expected in the second line of {!r:s}!".
									   format(filename))
			if value != "2.4.2" and value != "3.0.0":
				raise IfoFileException("Version expected to be either 2.4.2 or 3.0.0, but {!r:s} "
									   "read!".format(value))
			self._ifo[key] = value
			# read in other infomation in the file
			for line in ifo_file:
				key, equal, value = line.partition("=")
				key = key.strip()
				value = value.strip()
				self._ifo[key] = value
			# check if idxoffsetbits should be discarded due to version info
			if self._ifo["version"] == "3.0.0" and "idxoffsetbits" in self._ifo:
				del self._ifo["version"]

	def get_ifo(self, key):
		"""Get configuration value.
		
		Arguments:
		- `key`: configuration option name
		Return:
		- configuration value corresponding to the specified key if exists, otherwise False.
		"""
		if key not in self._ifo:
			return False
		return self._ifo[key]


class IdxFileReader(object):
	"""Read dictionary indexes from the .idx file and store the indexes in a list and a dictionary.
	   The list contains each entry in the .idx file, with subscript indicating the entry's origin 
	   index in .idx file. The dictionary is indexed by word name, and the value is an integer or a 
	   list of integers pointing to the entry in the list."""
	
	def __init__(self, filename, index_offset_bits = 32):
		"""
		Arguments:
		- `filename`: the filename of .idx file of stardict.
		- `compressed`: indicate whether the .idx file is compressed.
		- `index_offset_bits`: the offset field length in bits.
		"""
		compressed = os.path.splitext(filename)[1] == ".gz"
		if compressed:
			with gzip.open(filename, "rb") as index_file:
				self._content = index_file.read()
		else:
			with open(filename, "rb") as index_file:
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

	def __iter__(self):
		return self

	def __next__(self):
		if self._offset == len(self._content):
			raise StopIteration
		word_data_offset = 0
		word_data_size = 0
		end = self._content.find(b"\0", self._offset)
		word_str = self._content[self._offset: end]
		self._offset = end+1
		if self._index_offset_bits == 64:
			word_data_offset, = struct.unpack("!I", self._content[self._offset:self._offset+8])
			self._offset += 8
		elif self._index_offset_bits == 32:
			word_data_offset, = struct.unpack("!I", self._content[self._offset:self._offset+4])
			self._offset += 4
		else:
			raise ValueError
		word_data_size, = struct.unpack("!I", self._content[self._offset:self._offset+4])
		self._offset += 4
		self._index += 1
		return (word_str, word_data_offset, word_data_size, self._index)

	def get_index_by_num(self, number):
		"""Get index infomation of a specified entry in .idx file by origin index.
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


	def get_index_by_word(self, word_str):
		"""Get index infomation of a specified word entry.
		
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


class SynFileReader(object):
	"""Read infomation from .syn file and form a dictionary as below:
	{synonym_word: original_word_index}, in which 'original_word_index' could be a integer or
	a list of integers.
	"""
	def __init__(self, filename):
		"""Constructor.

		Arguments:
		- `filename`: The filename of .syn file of stardict.
		"""
		self._syn = dict()
		with open(filename, "r") as syn_file:
			content = syn_file.read()
		offset = 0
		while offset < len(content):
			end = content.find("\0", offset)
			synonym_word = content[offset:end]
			offset = end
			original_word_index = struct.unpack("!I", content[offset, offset+4])
			offset += 4
			if synonym_word in self._syn:
				if isinstance(self._syn[synonym_word], list):
					self._syn[synonym_word].append(original_word_index)
				else:
					self._syn[synonym_word] = [self._syn[synonym_word], original_word_index]
			else:
				self._syn[synonym_word] = original_word_index

	def get_syn(self, synonym_word):
		"""
		
		Arguments:
		- `synonym_word`: synonym word.
		Return:
		If synonym_word exists in the .syn file, return the corresponding indexes, otherwise False.
		"""
		if synonym_word not in self._syn:
			return False
		return self._syn[synonym_word]

			
class DictFileReader(object):
	"""Read the .dict file, store the data in memory for querying.
	"""
	
	def __init__(self, filename, dict_ifo, dict_index):
		"""Constructor.
		
		Arguments:
		- `filename`: filename of .dict file.
		- `dict_ifo`: IfoFileReader object.
		- `dict_index`: IdxFileReader object.
		"""
		self._dict_ifo = dict_ifo
		self._dict_index = dict_index
		self._offset = 0
		compressed = os.path.splitext(filename)[1] == ".dz"
		if compressed:
			#with gzip.open(filename, "rb") as dict_file:
			#    self._dict_file = dict_file.read()
			self.fd = idzip.open(filename)
		else:
			#with open(filename, "rb") as dict_file:
			#    self._dict_file = dict_file.read()
			self.fd = open(filename, "rb")


	def _get_dict_by_offset_size_internal(self, offset, size, sametypesequence, result):
		self.fd.seek(offset)            
		self._dict_file = self.fd.read(size)
		if sametypesequence:
			result.append(self._get_entry_sametypesequence(0, size))
		else:
			result.append(self._get_entry(0, size))
			
	def get_dict_by_offset_size(self, offset, size):
		sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
		result = list()
		self._get_dict_by_offset_size_internal(offset, size, sametypesequence, result)
		return result
		
	def get_dict_by_word(self, word):
		"""Get the word's dictionary data by it's name.
		
		Arguments:
		- `word`: word name.
		Return:
		The specified word's dictionary data, in form of dict as below:
		{type_identifier: infomation, ...}
		in which type_identifier can be any character in "mlgtxykwhnrWP".
		"""
		if type(word) != type(b""):
			word = word.encode("utf-8")
		indexes = self._dict_index.get_index_by_word(word)
		if indexes == False:
			return False
		sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
		result = list()
		for index in indexes:
			self._get_dict_by_offset_size_internal(index[0], index[1], sametypesequence, result)
		return result

	def get_dict_by_index(self, index):
		"""Get the word's dictionary data by it's index infomation.
		
		Arguments:
		- `index`: index of a word entrt in .idx file.'
		Return:
		The specified word's dictionary data, in form of dict as below:
		{type_identifier: infomation, ...}
		in which type_identifier can be any character in "mlgtxykwhnrWP".
		"""
		word, offset, size = self._dict_index.get_index_by_num(index)
		sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
		self.fd.seek(offset)            
		self._dict_file = self.fd.read(size)
		if sametypesequence:
			return self._get_entry_sametypesequence(0, size)
		else:
			return self._get_entry(0, size)

	def _get_entry(self, offset, size):
		result = dict()
		read_size = 0
		start_offset = offset
		while read_size < size:
			type_identifier = struct.unpack("!c")
			if type_identifier in "mlgtxykwhnr":
				result[type_identifier],offset = self._get_entry_field_null_trail(offset)
			else:
				result[type_identifier],offset = self._get_entry_field_size(offset, None)
			read_size = offset - start_offset
		return result
		
	def _get_entry_sametypesequence(self, offset, size):
		#trace("_get_entry_sametypesequence offset %d size %d" % (offset, size))
		start_offset = offset
		result = dict()
		sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
		for k in range(0, len(sametypesequence)):
			if sametypesequence[k] in "mlgtxykwhnr":
				if k == len(sametypesequence)-1:
					result[sametypesequence[k]],offset = \
						self._get_entry_field_size(offset, size - (offset - start_offset))
				else:
					result[sametypesequence[k]],offset = self._get_entry_field_null_trail(offset)
			elif sametypesequence[k] in "WP":
				if k == len(sametypesequence)-1:
					result[sametypesequence[k]],offset = \
						self._get_entry_field_size(offset, size - (offset - start_offset))
				else:
					result[sametypesequence[k]],offset = self._get_entry_field_size(offset, None)
		return result

	def _get_entry_field_null_trail(self, offset):
		end = self._dict_file.find("\0", offset)
		result = self._dict_file[offset:end]
		return (result, end+1)
		
	def _get_entry_field_size(self, offset, size):
		if size is None:
			size = struct.unpack("!I", self._dict_file[offset:(offset+4)])[0]
			offset += 4
		result = self._dict_file[offset:(offset+size)]
		return (result, offset + size)

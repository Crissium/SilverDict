import struct
import zlib
import os
from pathlib import Path
import pickle
import io
try:
	import lzo
	lzo_is_c = True
except ImportError:
	from .mdict import lzo
	lzo_is_c = False
import concurrent.futures
from .base_reader import BaseReader
from .. import db_manager
from .mdict import MDX, MDD, HTMLCleaner
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MDictReader(BaseReader):
	FILENAME_MDX_PICKLE = 'mdx.pickle'
	def _write_to_cache_dir(self, resource_filename: 'str', data: 'bytes') -> 'None':
		absolute_path = os.path.join(self._resources_dir, resource_filename)
		with open(absolute_path, 'wb') as f:
			f.write(data)

	def __init__(self,
	    		 name: 'str',
				 filename: 'str',
				 display_name: 'str',
				 extract_resources: 'bool'=True,
				 remove_resources_after_extraction: 'bool'=False,
				 load_content_into_memory: 'bool'=False) -> 'None':
		"""
		It is recommended to set remove_resources_after_extraction to True on a server when you have local backup.
		"""
		super().__init__(name, filename, display_name)
		filename_no_extension, extension = os.path.splitext(filename)
		self._resources_dir = os.path.join(self._CACHE_ROOT, name)
		Path(self._resources_dir).mkdir(parents=True, exist_ok=True)

		filename_mdx_pickle = os.path.join(self._resources_dir, self.FILENAME_MDX_PICKLE)
		if os.path.isfile(filename_mdx_pickle):
			mdx_pickled = True
			with open(filename_mdx_pickle, 'rb') as f:
				self._mdict = pickle.load(f)
			if self._mdict._fname != filename: # the pickle's off
				self._mdict = MDX(filename)
				mdx_pickled = False
		else:
			mdx_pickled = False
			self._mdict = MDX(filename)

		if not db_manager.dictionary_exists(self.name):
			db_manager.drop_index()
			for i in range(len(self._mdict._key_list)):
				offset, key = self._mdict._key_list[i]
				if i + 1 < len(self._mdict._key_list):
					length = self._mdict._key_list[i + 1][0] - offset
				else:
					length = -1
				db_manager.add_entry(self.simplify(key.decode('UTF-8')), self.name, key.decode('UTF-8'), offset, length)
			db_manager.commit()
			db_manager.create_index()
			logger.info('Entries of dictionary %s added to database' % self.name)

		if not mdx_pickled:
			del self._mdict._key_list # a hacky way to reduce memory usage without touching the library
			with open(filename_mdx_pickle, 'wb') as f:
				pickle.dump(self._mdict, f)

		self.html_cleaner = HTMLCleaner(filename, name, self._resources_dir)

		self._loaded_content_into_memory = load_content_into_memory
		if load_content_into_memory:
			with open(filename, 'rb') as f:
				self._content = io.BytesIO(f.read())

		if extract_resources and not os.path.isdir(self._resources_dir): # Only extract the files once
			# Load the resource files (.mdd), if any
			# For example, for the dictionary collinse22f.mdx, there are four .mdd files:
			# collinse22f.mdd, collinse22f.1.mdd, collinse22f.2.mdd, collinse22f.3.mdd
			resources = []
			mdd_base_filename = '%s.' % filename_no_extension
			if os.path.isfile(mdd_filename := '%smdd' % mdd_base_filename) or os.path.isfile(mdd_filename := '%s.MDD' % mdd_base_filename):
				resources.append(MDD(mdd_filename))
			i = 1
			while os.path.isfile(mdd_filename := '%s%d.mdd' % (mdd_base_filename, i)) or os.path.isfile(mdd_filename := '%s%d.MDD' % (mdd_base_filename, i)):
				resources.append(MDD(mdd_filename))
				i += 1
			
			# Extract resource files into cache directory
			for mdd in resources:
				for resource_filename, resource_file in mdd.items():
					resource_filename = resource_filename.decode('UTF-8').replace('\\', '/')
					if resource_filename.startswith('/'):
						resource_filename = resource_filename[1:]
					self._write_to_cache_dir(resource_filename, resource_file)
			
			if remove_resources_after_extraction:
				for mdd in resources:
					os.remove(mdd._fname)

	def _get_record(self, mdict_fp, offset: 'int', length: 'int') -> 'str':
		if self._mdict._version >= 3:
			return self._get_record_v3(mdict_fp, offset, length)
		else:
			return self._get_record_v1v2(mdict_fp, offset, length)

	def _get_record_v3(self, f, offset: 'int', length: 'int') -> 'str':
		f.seek(self._mdict._record_block_offset)

		num_record_blocks = self._mdict._read_int32(f)

		decompressed_offset = 0
		for j in range(num_record_blocks):
			decompressed_size = self._mdict._read_int32(f)
			compressed_size = self._mdict._read_int32(f)

			if (decompressed_offset + decompressed_size) > offset:
				break
			decompressed_offset += decompressed_size
			f.seek(compressed_size, 1)

		block_compressed = f.read(compressed_size)
		record_block = self._mdict._decode_block(block_compressed, decompressed_size)

		record_start = offset - decompressed_offset
		if length > 0:
			record_null = record_block[record_start:record_start + length]
		else:
			record_null = record_block[record_start:]

		return record_null.strip().decode(self._mdict._encoding)

	def _get_record_v1v2(self, f, offset: 'int', length: 'int') -> 'str':
		f.seek(self._mdict._record_block_offset)

		num_record_blocks = self._mdict._read_number(f)
		num_entries = self._mdict._read_number(f)
		assert(num_entries == self._mdict._num_entries)
		record_block_info_size = self._mdict._read_number(f)
		self._mdict._read_number(f)

		# record block info section
		compressed_offset = f.tell() + record_block_info_size
		decompressed_offset = 0
		for i in range(num_record_blocks):
			compressed_size = self._mdict._read_number(f)
			decompressed_size = self._mdict._read_number(f)
			if (decompressed_offset + decompressed_size) > offset:
				break
			decompressed_offset += decompressed_size
			compressed_offset += compressed_size

		f.seek(compressed_offset)
		block_compressed = f.read(compressed_size)
		block_type = block_compressed[:4]
		adler32 = struct.unpack('>I', block_compressed[4:8])[0]
		# no compression
		if block_type == b'\x00\x00\x00\x00':
			record_block = block_compressed[8:]
		# lzo compression
		elif block_type == b'\x01\x00\x00\x00':
			# LZO compression is used for engine version < 2.0
			if lzo_is_c:
				header = b'\xf0' + struct.pack('>I', decompressed_size)
				record_block = lzo.decompress(header + block_compressed[8:])
			else:
				record_block = lzo.decompress(block_compressed[8:], initSize=decompressed_size, blockSize=1308672)
		# zlib compression
		elif block_type == b'\x02\x00\x00\x00':
			# decompress
			record_block = zlib.decompress(block_compressed[8:])
		# notice that adler32 return signed value
		assert(adler32 == zlib.adler32(record_block) & 0xffffffff)
		assert(len(record_block) == decompressed_size)

		record_start = offset - decompressed_offset
		if length > 0:
			record_null = record_block[record_start:record_start + length]
		else:
			record_null = record_block[record_start:]
		return record_null.strip().decode(self._mdict._encoding)

	def _get_records_in_batch(self, locations: 'list[tuple[int, int]]') -> 'list[str]':
		if self._loaded_content_into_memory:
			mdict_fp = self._content
		else:
			mdict_fp = open(self.filename, 'rb')
		records = [self._get_record(mdict_fp, offset, length) for offset, length in locations]
		if not self._loaded_content_into_memory:
			mdict_fp.close()
		return records

	def get_definition_by_key(self, entry: 'str') -> 'str':
		locations = db_manager.get_entries(entry, self.name)
		# word is not used in mdict, which is present in the article itself.
		locations = [(offset, length) for word, offset, length in locations]
		records = self._get_records_in_batch(locations)
		# Cleaning up HTML actually takes some time to complete
		with concurrent.futures.ThreadPoolExecutor(len(records)) as executor:
			records = list(executor.map(self.html_cleaner.clean, records))
		return self._ARTICLE_SEPARATOR.join(records)

	def get_definition_by_word(self, headword: 'str') -> 'str':
		locations = db_manager.get_entries_with_headword(headword, self.name)
		records = self._get_records_in_batch([(offset, length) for offset, length in locations])
		with concurrent.futures.ThreadPoolExecutor(len(records)) as executor:
			records = list(executor.map(self.html_cleaner.clean, records))
		return self._ARTICLE_SEPARATOR.join(records)
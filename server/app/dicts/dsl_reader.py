import re
import os
import shutil
import idzip
from json import detect_encoding
from pathlib import Path
import concurrent.futures
from .base_reader import BaseReader
from .. import db_manager
from .dsl import DSLConverter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Options:  # for use with idzip
	suffix = '.dz'
	keep = False


class DSLReader(BaseReader):
	"""
	Adapted from dslutils.py by J.F. Dockes with enhancements.
	DSL dictionaries have five possible file types:
	- name.ann: annotation file, that is, dictionary metadata (unused)
	- name.bmp: dictionary icon (unused)
	- name.dsl: the main dictionary file, usually compressed (.dz)
	- name.dsl.files.zip: the resources (images, sounds, etc.) of the dictionary
	- name_abrv.dsl: some useless abbreviations, usually compressed (.dz) (unused)
	"""
	_NON_PRINTING_CHARS_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')

	@staticmethod
	def _cleanup_text(text: str) -> str:
		# Get rid of the BOM
		text = text.replace('\ufeff', '', 1)

		# Remove the {·} marker (note: this is not the same as {·}, which is used to separate syllables)
		text = text.replace('{·}', '')

		# Remove all non-printing characters
		text = DSLReader._NON_PRINTING_CHARS_PATTERN.sub('', text)

		return text

	@staticmethod
	def _clean_up_opening_whitespace(text: str) -> str:
		lines = text.splitlines()
		for i, line in enumerate(lines):
			if not line:  # empty lines are preserved
				continue
			elif line[0].isspace():
				lines[i] = ' ' + line.lstrip()
		return '\n'.join(lines)

	@staticmethod
	def _clean_up(dsl_decompressed_path: str) -> None:
		"""
		Danger zone: transforms original file to UTF-8, tinkers with it, and overwrites the original file.
		Create a back-up of the original dictionaries.
		"""
		with open(dsl_decompressed_path, 'rb') as f:
			data = f.read()
		text = data.decode(detect_encoding(data)) # TODO: json's detect_encoding() is not always reliable
		del data
		text = DSLReader._cleanup_text(text)
		text = DSLReader._clean_up_opening_whitespace(text)
		with open(dsl_decompressed_path, 'w', encoding='utf-8') as f:
			f.write(text)

	@staticmethod
	def _read_content_end_offset(f) -> int:
		"""
		Read the entry content lines, beginning with white space.
		Leave the file at the beginning of the next headword line.
		"""
		while True:
			offset = f.tell()
			# Very strange python bug: under uncertain circumstances (maybe something to do with an
			# empty line next), the offset is like 0x10000000000000074. Such an offset is impossible of
			# course (>64 bits...) --- JF Dockes
			if offset > 0x10000000000000000:
				offset -= 0x10000000000000000
			l = f.readline()
			# print('!!!', offset, l.strip(), f.tell())
			if l == '':
				# EOF
				return f.tell()
			elif l[0] == '#':
				# Header or comment
				continue
			elif l[0] != ' ' and l[0] != '\t':
				f.seek(offset)
				return offset

	def __init__(self,
				 name: str,
				 filename: str, # .dsl/.dsl.dz
				 display_name: str,
				 performs_cleanup: bool = True, # Make sure your dsl is already cleaned up if it is False
				 extract_resources: bool = False,
				 remove_resources_after_extraction: bool = True,
				 load_content_into_memory: bool = False) -> 'None':
		super().__init__(name, filename, display_name)
		filename_no_extension, extension = os.path.splitext(filename)
		is_compressed = extension == '.dz'

		if not db_manager.dictionary_exists(self.name):
			# !!! Back up before transformation
			shutil.copyfile(filename, filename + '.old')
			from idzip.command import _compress as idzip_compress, _decompress as idzip_decompress
			db_manager.drop_index()
			if is_compressed:
				idzip_decompress(filename, Options)
				# filename_no_extension is name.dsl
				dsl_decompressed_path = filename_no_extension
				if performs_cleanup:
					self._clean_up(dsl_decompressed_path)
				f = open(dsl_decompressed_path, 'r', encoding='utf-8')
			else:
				if performs_cleanup:
					self._clean_up(filename)
				f = open(filename, 'r', encoding='utf-8')
			with f:
				headwords = []
				while True:
					offset = f.tell()
					l = f.readline()
					if l == '':
						# EOF
						break
					if l[0] == '#' or l[0] == '\n':
						# Header or separator
						if '#NAME' in l and display_name in filename: # The display name is generated from the filename
							display_name = l[l.find('"')+1:l.rfind('"')]
							if len(display_name) > 0:
								self.display_name = display_name
						continue
					if l[0] != ' ' and l[0] != '\t':
						# Headword, could be separated by ' and '
						headwords.append(l.strip())
						if ' and ' in l:
							headwords.extend(l.split(' and '))
						# There also could be multiple headwords spanning several lines that share the same definition
						while True:
							offset = f.tell()
							# Test a single char, if it is a space, then we have hit the beginning of the definition
							char = f.read(1)
							f.seek(offset)
							if char == ' ' or char == '\t':
								break
							l = f.readline()
							# There cannot be a comment or an EOF here
							# Disproved by Greek Patristic Lexicon, ha ha
							if l == '':
								# EOF
								break
							headwords.append(l.strip())
							if ' and ' in l:
								headwords.extend(l.split(' and '))
						# We have reached the beginning of the definition
						# Read the definition
						# print('#', headwords, f.tell(), '\nEND HEADWORD')
						content_end_offset = self._read_content_end_offset(f)
						# print('#', content_end_offset, '\n##', f.tell(), '\nEND CONTENT')
						size = content_end_offset - offset
						for headword in headwords:
							db_manager.add_entry(self.simplify(headword), self.name, headword, offset, size)
						headwords.clear()
			db_manager.commit_new_entries(self.name)
			db_manager.create_index()
			logger.info(f'Entries of dictionary {self.name} added to database')
			# Whether compressed originally or not, we need to compress it now
			if is_compressed:
				idzip_compress(dsl_decompressed_path, Options)
				if os.path.isfile(dsl_decompressed_path):
					os.remove(dsl_decompressed_path)
			else:
				idzip_compress(filename, Options)
				if os.path.isfile(filename):
					os.remove(filename)
			# Now the filename is name.dsl.dz
			self.filename = dsl_decompressed_path + '.dz' if is_compressed else filename + '.dz'

		Path(os.path.join(self._CACHE_ROOT, self.name)).mkdir(parents=True, exist_ok=True)
		self._converter = DSLConverter(self.filename,
								 	   self.name,
									   os.path.join(self._CACHE_ROOT, self.name),
									   extract_resources)

		self._loaded_content_into_memory = load_content_into_memory
		if load_content_into_memory:
			with idzip.open(self.filename) as f:
				self._content = f.read()

		if extract_resources:
			from zipfile import ZipFile

			if is_compressed:
				resources_filename = filename_no_extension + '.files.zip'
			else:
				resources_filename = filename + '.files.zip'

			if os.path.isfile(resources_filename):
				with ZipFile(resources_filename) as zip_file:
					zip_file.extractall(os.path.join(self._CACHE_ROOT, self.name))
				if remove_resources_after_extraction:
					os.remove(resources_filename)

	def _get_record(self, f: 'idzip.api.IdzipFile', offset: int, size: int) -> str:
		"""
		Returns original DSL markup.
		"""
		f.seek(offset)
		data = f.read(size)
		assert detect_encoding(data) == 'utf-8'
		return data.decode('utf-8')

	def _get_record_from_cache(self, offset: int, size: int) -> str:
		return self._content[offset:offset+size].decode('utf-8')

	def _get_records_in_batch(self, locations: list[tuple[str, int, int]]) -> list[tuple[str, str, int]]:
		"""
		Takes a list of (word, offset, size) tuples and returns a list of (record, word, offset) tuples.
		The headword is used for the article heading and the offset is needed for sorting.
		"""
		records = []
		if self._loaded_content_into_memory:
			# for word, offset, size in locations:
			# 	records.append((self._get_record_from_cache(offset, size), word))
			with concurrent.futures.ThreadPoolExecutor(len(locations)) as executor:
				executor.map(
					lambda location: records.append(
						(
							self._get_record_from_cache(
								location[1],
								location[2]
							),
							location[0],
							location[1]
						)
					),
					locations
				)
		else:
			with idzip.open(self.filename) as f:
				for word, offset, size in locations:
					records.append((self._get_record(f, offset, size), word, offset))
		return records

	def get_definition_by_key(self, entry: str) -> str:
		locations = db_manager.get_entries(entry, self.name)
		records = self._get_records_in_batch(locations)
		# records = [self._converter.convert(*record) for record in records]
		# DSL parsing is expensive, so we'd better parallelise it
		with concurrent.futures.ThreadPoolExecutor(len(records)) as executor:
			records = list(executor.map(self._converter.convert, records))
		articles = [record[0] for record in sorted(records, key=lambda article: article[1])]
		return self._ARTICLE_SEPARATOR.join(articles)

	def get_definition_by_word(self, headword: str) -> str:
		locations = db_manager.get_entries_with_headword(headword, self.name)
		records = self._get_records_in_batch([(headword, *location) for location in locations])
		with concurrent.futures.ThreadPoolExecutor(len(records)) as executor:
			records = list(executor.map(self._converter.convert, records))
		articles = [record[0] for record in records] # order shouldn't matter here
		return self._ARTICLE_SEPARATOR.join(articles)

from .base_reader import BaseReader
from .mdict.readmdict import MDX, MDD
import struct
import zlib
from .mdict import lzo
import os
import shutil
from pathlib import Path
# import css_inline
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MDictReader(BaseReader):
	"""
	Reader for MDict dictionaries.
	"""
	def __init__(self,
	    		 name: 'str',
				 filename: 'str',
				 display_name: 'str',
				 dictionary_exists: 'function',
				 add_entry: 'function',
				 commit: 'function',
				 get_entries: 'function',
				 create_index: 'function',
				 drop_index: 'function',
				 extract_resources: 'bool'=True,
				 remove_resources_after_extraction: 'bool'=False) -> 'None':
		"""
		It is recommended to set remove_resources_after_extraction to True on a server when you have local backup.
		"""
		super().__init__(name, filename, display_name, dictionary_exists, add_entry, commit, get_entries, create_index, drop_index)

		self._mdict = MDX(filename)
		# self._entry_list = [key.decode('UTF-8') for key in self._mdict.keys()]
		# self._entry_list_simplified = [BaseReader.simplify(key) for key in self._entry_list]

		# Build fast lookup table
		# self._entry_locations : 'dict[bytes, list[tuple[int, int]]]' = dict() # key: entry, value: list of (offset, length) pairs
		# Replaced by SQLite
		if not self.dictionary_exists(self.name):
			self.drop_index() # improve insertion speed
			for i in range(len(self._mdict._key_list)):
				offset, key = self._mdict._key_list[i]
				if i + 1 < len(self._mdict._key_list):
					length = self._mdict._key_list[i + 1][0] - offset
				else:
					length = -1
				self.add_entry(BaseReader.simplify(key.decode('UTF-8')), self.name, key.decode('UTF-8'), offset, length)
			self.commit()
			self.create_index()
			logger.info('Entries of dictionary %s added to database' % self.name)

		filename_no_extension, extension = os.path.splitext(filename)
		self._relative_root_dir = filename_no_extension.split('/')[-1]
		self._resources_dir = os.path.join(self._CACHE_ROOT, self._relative_root_dir)
		self._href_root_dir = '/api/cache/' + self._relative_root_dir + '/' # to be used with flask's send_file
		self._lookup_url_root = '/api/lookup/' + self._relative_root_dir + '/' # to be used with flask's lookup API

		if extract_resources and not os.path.isdir(self._resources_dir): # Only extract the files once
			# Load the resource files (.mdd), if any
			# For example, for the dictionary collinse22f.mdx, there are four .mdd files:
			# collinse22f.mdd, collinse22f.1.mdd, collinse22f.2.mdd, collinse22f.3.mdd
			resources = []
			mdd_base_filename = '%s.' % filename_no_extension
			if os.path.isfile('%smdd' % mdd_base_filename):
				resources.append(MDD('%smdd' % mdd_base_filename))
			i = 1
			while os.path.isfile('%s%d.mdd' % (mdd_base_filename, i)):
				resources.append(MDD('%s%d.mdd' % (mdd_base_filename, i)))
				i += 1
			
			# Extract resource files into cache directory
			for mdd in resources:
				for resource_filename, resource_file in mdd.items():
					resource_filename = resource_filename.decode('UTF-8').replace('\\', '/') # G-d d-n Windows!
					if resource_filename.startswith('/'):
						resource_filename = resource_filename[1:]
					self._write_to_cache_dir(os.path.join(self._relative_root_dir, resource_filename), resource_file)
			
			if remove_resources_after_extraction:
				for mdd in resources:
					os.remove(mdd._fname)

	# def entry_list(self) -> 'list[str]':
	# 	return self._entry_list
	
	# def entry_list_simplified(self) -> 'list[str]':
	# 	return self._entry_list_simplified
	
	# def entry_count(self) -> 'int':
	# 	return len(self._entry_list)
	
	# def entry_exists(self, entry: 'str') -> 'bool':
	# 	return entry in self._entry_list

	def _get_record(self, md: 'MDD | MDX', offset: 'int', length: 'int') -> 'str':
		if md._version >= 3:
			return self._get_record_v3(md, offset, length)
		else:
			return self._get_record_v1v2(md, offset, length)

	def _get_record_v3(self, md: 'MDD | MDX', offset: 'int', length: 'int') -> 'str':
		f = open(md._fname, 'rb')
		f.seek(md._record_block_offset)

		num_record_blocks = md._read_int32(f)

		decompressed_offset = 0
		for j in range(num_record_blocks):
			decompressed_size = md._read_int32(f)
			compressed_size = md._read_int32(f)

			if (decompressed_offset + decompressed_size) > offset:
				break
			decompressed_offset += decompressed_size
			f.seek(compressed_size, 1)

		block_compressed = f.read(compressed_size)
		record_block = md._decode_block(block_compressed, decompressed_size)

		record_start = offset - decompressed_offset
		if length > 0:
			record_null = record_block[record_start:record_start + length]
		else:
			record_null = record_block[record_start:]
		f.close()
		if md._fname.endswith('.mdd'):
			return record_null
		else:
			return record_null.strip().decode(md._encoding)

	def _get_record_v1v2(self, md: 'MDD | MDX', offset: 'int', length: 'int') -> 'str':
		f = open(md._fname, 'rb')
		f.seek(md._record_block_offset)

		num_record_blocks = md._read_number(f)
		num_entries = md._read_number(f)
		assert(num_entries == md._num_entries)
		record_block_info_size = md._read_number(f)
		md._read_number(f)

		# record block info section
		compressed_offset = f.tell() + record_block_info_size
		decompressed_offset = 0
		for i in range(num_record_blocks):
			compressed_size = md._read_number(f)
			decompressed_size = md._read_number(f)
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
			# decompress
			# standard lzo (python-lzo) of c version
			# header = b'\xf0' + struct.pack('>I', decompressed_size)
			# record_block = lzo.decompress(header + block_compressed[8:])
			# lzo of python version, no header!!!
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
		f.close()
		if md._fname.endswith('.mdd'):
			return record_null
		else:
			return record_null.strip().decode(md._encoding)
	
	def _fix_file_path(self, definition_html: 'str', file_extension: 'str') -> 'str':
		extension_position = 0
		while (extension_position := definition_html.find(file_extension, extension_position)) != -1:
			filename_position = definition_html.rfind('"', 0, extension_position) + 1
			filename = definition_html[filename_position:extension_position + len(file_extension)]
			file_path_on_disk =  os.path.join(os.path.dirname(self.filename), filename)
			if os.path.isfile(file_path_on_disk):
				# Create the resource directory
				Path(self._resources_dir).mkdir(parents=True, exist_ok=True)
				# Copy the file to the resource directory
				shutil.copy(file_path_on_disk, os.path.join(self._resources_dir, filename))
				definition_html = definition_html[:filename_position] + self._href_root_dir + definition_html[filename_position:]
			extension_position += len(file_extension)
		return definition_html
	
	# def _inline_styles(self, html_content: 'str') -> 'str': # CSS path(s) is inside the HTML file
	# 	# Find all CSS references
	# 	# regex won't work. Maybe it's simply because that I haven't mastered the dark art.
	# 	css_references = []
	# 	css_extension_position = 0
	# 	while (css_extension_position := html_content.find('.css"', css_extension_position)) != -1:
	# 		css_filename_position = html_content.rfind('"', 0, css_extension_position) + 1
	# 		css_filename = html_content[css_filename_position:css_extension_position] + '.css'
	# 		css_references.append(css_filename)
	# 		# Remove the CSS reference
	# 		link_tag_start_position = html_content.rfind('<link', 0, css_filename_position)
	# 		link_tag_end_position = html_content.find('>', link_tag_start_position) + 1
	# 		html_content = html_content[:link_tag_start_position] + html_content[link_tag_end_position:]
	# 		css_extension_position = link_tag_start_position
		
	# 	for css in css_references:
	# 		# Read the CSS file
	# 		css_path = os.path.join(self._resources_dir, css.split('/')[-1])
	# 		with open(css_path) as css_file:
	# 			css_content = css_file.read()

	# 		# Inline the CSS
	# 		inliner = css_inline.CSSInliner(load_remote_stylesheets=False, extra_css=css_content)
	# 		html_content = inliner.inline(html_content)
		
	# 	return html_content
	
	def _fix_internal_href(self, definition_html: 'str') -> 'str':
		# That is, links like entry://#81305a5747ca42b28f2b50de9b762963_nav2
		return definition_html.replace('entry://#', '#')
	
	def _flatten_nested_a(self, definition_html: 'str', depth: 'int') -> 'str':
		# Sometimes there're multiple inner elements inside the <a> element, which should be removed
		# For example, in my Fr-En En-Fr Collins Dictionary, there's a <span> element inside the <a> element
		# The text within the <span> should be preserved, though
		# <a class="ref" href="/lookup/collinse22f/badly" title="Translation of badly"><span class="orth">badly</span></a>
		if depth == 0:
			return definition_html
		else:
			a_closing_tag_pos = 0
			while (a_tag_start_pos := definition_html.find('<a', a_closing_tag_pos)) != -1:
				a_tag_end_pos = definition_html.find('>', a_tag_start_pos)
				inner_html_start_pos = definition_html.find('>', a_tag_end_pos + 1) + 1
				if (a_closing_tag_pos := definition_html.find('</a>', a_tag_end_pos, inner_html_start_pos)) != -1:
					continue
				inner_html_end_pos = definition_html.find('</', inner_html_start_pos)
				inner_html = definition_html[inner_html_start_pos:inner_html_end_pos]
				a_closing_tag_pos = definition_html.find('</a>', inner_html_end_pos)
				definition_html = definition_html[:a_tag_end_pos + 1] + inner_html + definition_html[a_closing_tag_pos:]
			return self._flatten_nested_a(definition_html, depth - 1)
	
	def _fix_entry_cross_ref(self, definition_html: 'str') -> 'str':
		definition_html = definition_html.replace('entry://', self._lookup_url_root)
		return self._flatten_nested_a(definition_html, 3) # fingers crossed there are no more than three layers
	
	def _fix_sound_link(self, definition_html: 'str') -> 'str':
		# Use HTML sound element instead of the original <a> element, which looks like this:
		# <a class="hwd_sound sound audio_play_button icon-volume-up ptr fa fa-volume-up" data-lang="en_GB" data-src-mp3="https://www.collinsdictionary.com/sounds/hwd_sounds/EN-GB-W0020530.mp3" href="sound://audio/ef/7650.mp3" title="Pronunciation for "><img class="soundpng" src="/api/cache/collinse22f/img/sound.png"></a>
		sound_element_template = '<audio controls src=%s>%s</audio>'
		while (sound_link_start_pos := definition_html.find('sound://')) != -1:
			sound_link_end_pos = definition_html.find('"', sound_link_start_pos)
			original_sound_link = definition_html[sound_link_start_pos:sound_link_end_pos]
			sound_link = original_sound_link.replace('sound://', self._href_root_dir)
			inner_html_start_pos = definition_html.find('>', sound_link_end_pos) + 1
			inner_html_end_pos = definition_html.find('</a>', inner_html_start_pos)
			inner_html = definition_html[inner_html_start_pos:inner_html_end_pos]
			outer_html_start_pos = definition_html.rfind('<a', 0, sound_link_start_pos)
			outer_html_end_pos = definition_html.find('</a>', inner_html_end_pos) + len('</a>')
			definition_html = definition_html[:outer_html_start_pos] + sound_element_template % (sound_link, inner_html) + definition_html[outer_html_end_pos:]

		return definition_html
	
	def _fix_img_src(self, definition_html: 'str') -> 'str':
		img_tag_end_pos = 0
		while (img_tag_start_pos := definition_html.find('<img', img_tag_end_pos)) != -1:
			img_tag_end_pos = definition_html.find('>', img_tag_start_pos)
			img_src_start_pos = definition_html.find(' src="', img_tag_start_pos, img_tag_end_pos) + len(' src="')
			img_src_end_pos = definition_html.find('"', img_src_start_pos, img_tag_end_pos)
			img_src = definition_html[img_src_start_pos:img_src_end_pos]
			img_src = self._href_root_dir + img_src.replace('file://' , '')
			definition_html = definition_html[:img_src_start_pos] + img_src + definition_html[img_src_end_pos:]
		return definition_html
	
	def entry_definition(self, entry: 'str') -> 'str':
		# It shouldn't happen after being checked by SilverDict
		# if not entry in self._entry_list:
		# 	raise ValueError('Entry %s does not exist in dictionary %s' % (entry, self.filename))
		
		simplified_entry = self.simplify(entry)
		locations = self.get_entries(simplified_entry, self.name)
		records = []
		for word, offset, length in locations:
			if word == entry:
				record = self._get_record(self._mdict, offset, length)

				record = self._fix_file_path(record, '.css')
				record = self._fix_file_path(record, '.js')
				# record = self._inline_styles(record)
				record = self._fix_internal_href(record)
				record = self._fix_entry_cross_ref(record)
				record = self._fix_sound_link(record)
				record = self._fix_img_src(record)

				records.append(record)

		return self._ARTICLE_SEPARATOR.join(records)


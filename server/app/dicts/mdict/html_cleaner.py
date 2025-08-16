import inspect
import os
import re
import shutil
from pathlib import Path
from html.parser import HTMLParser
from ... import utils


class HTMLCleaner:
	class _Concatenator(HTMLParser):
		def __init__(self) -> None:
			super().__init__()
			self._buf = []
		
		def handle_data(self, data: str) -> None:
			self._buf.append(data)
		
		def get_text(self) -> str:
			return ''.join(self._buf)

	_re_non_printing_chars = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')
	_re_compact_html_index = re.compile(r'`(\d+)`')
	_re_single_quotes = re.compile(r"=\'([^']*)\'(?=[ >])")

	def __init__(self, filename: str, dict_name: str, resources_dir: str, styles: str = '') -> None:
		self._filename = filename
		self._id = f'#{dict_name}'
		self._resources_dir = resources_dir
		self._href_root_dir = 'api/cache/' + dict_name + '/'
		self._lookup_url_root = 'api/lookup/' + dict_name + '/'
		self._has_styles = False
		if styles:
			self._has_styles = True
			self._compact_html_rules = dict()
			for i, line in enumerate(styles.splitlines()):
				if i % 3 == 0:
					index = line
				elif i % 3 == 1:
					prefix = line
				else:
					self._compact_html_rules[index] = (prefix, line)

	def _expand_compact_html(self, compact_html: str) -> str:
		buf = []
		pos = 0
		last_end_tag = ''
		for m in self._re_compact_html_index.finditer(compact_html):
			buf.append(compact_html[pos:m.start()])
			buf.append(last_end_tag)
			buf.append(self._compact_html_rules[m.group(1)][0])
			last_end_tag = self._compact_html_rules[m.group(1)][1]
			pos = m.end()
		if len(buf) > 0:
			buf.append(last_end_tag)
			buf.append(compact_html[pos:])
			return ''.join(buf)
		else:
			return compact_html

	def _convert_single_quotes_to_double(self, html: str) -> str:
		return self._re_single_quotes.sub('="\\1"', html)

	def _fix_file_path(self, definition_html: str, file_extension: str) -> str:
		extension_position = 0
		while (extension_position := definition_html.find(file_extension, extension_position)) != -1:
			filename_position = definition_html.rfind('"', 0, extension_position) + 1
			filename = definition_html[filename_position:extension_position + len(file_extension)]

			# Check if `Path.glob` supports the `case_sensitive` argument
			if inspect.signature(Path.glob).parameters.get('case_sensitive'):
				kwargs = {'case_sensitive': False}
			else:
				kwargs = {}

			file_path_on_disk = next(Path(os.path.dirname(self._filename)).glob(filename, **kwargs), '')
			new_file_path_on_disk = next(Path(self._resources_dir).glob(filename, **kwargs), '')
			fixed_filename = filename
			if new_file_path_on_disk:
				fixed_filename = str(new_file_path_on_disk.relative_to(Path(self._resources_dir)))
			elif file_path_on_disk:
				fixed_filename = str(file_path_on_disk.relative_to(Path(os.path.dirname(self._filename))))
			if not os.path.isfile(new_file_path_on_disk):
				if os.path.isfile(file_path_on_disk):
					Path(self._resources_dir).mkdir(parents=True, exist_ok=True)
					shutil.copy(file_path_on_disk, new_file_path_on_disk)
					definition_html = definition_html[:filename_position] + \
						self._href_root_dir + fixed_filename + \
						definition_html[filename_position+len(filename):]
			else:
				if os.path.isfile(file_path_on_disk):
					if os.path.getmtime(file_path_on_disk) > os.path.getmtime(new_file_path_on_disk):
						shutil.copy(file_path_on_disk, new_file_path_on_disk)
				definition_html = definition_html[:filename_position] + \
					self._href_root_dir + fixed_filename + \
					definition_html[filename_position+len(filename):]
			extension_position += len(file_extension)
		return definition_html
	
	def _isolate_css(self) -> None:
		for filename in os.listdir(self._resources_dir):
			if filename.endswith('.css') or filename.endswith('.CSS'):
				utils.isolate_css(os.path.join(self._resources_dir, filename), self._id)

	def _fix_internal_href(self, definition_html: str) -> str:
		# That is, links like entry://#81305a5747ca42b28f2b50de9b762963_nav2
		return definition_html.replace('entry://#', '#')

	def _flatten_nested_a(self, definition_html: str) -> str:
		# Sometimes there're multiple inner elements inside the <a> element, which should be removed
		# For example, in my Fr-En En-Fr Collins Dictionary, there's a <span> element inside the <a> element
		# The text within the <span> should be preserved, though
		# <a class="ref" href="/lookup/collinse22f/badly" title="Translation of badly"><span class="orth">badly</span></a>
		a_closing_tag_pos = 0
		while (a_tag_start_pos := definition_html.find('<a', a_closing_tag_pos)) != -1:
			a_tag_end_pos = definition_html.find('>', a_tag_start_pos)
			a_closing_tag_pos = definition_html.find('</a>', a_tag_end_pos)
			a_inner_html = definition_html[a_tag_end_pos+1:a_closing_tag_pos]
			concatenator = self._Concatenator()
			concatenator.feed(a_inner_html)
			a_inner_text = concatenator.get_text()
			definition_html = definition_html[:a_tag_end_pos+1] + a_inner_text + definition_html[a_closing_tag_pos:]
		return definition_html

	def _fix_entry_cross_ref(self, definition_html: str) -> str:
		if definition_html.startswith('@@@LINK='): # strange special case
			last_non_whitespace_position = len(definition_html) - 1
			while definition_html[last_non_whitespace_position].isspace():
				last_non_whitespace_position -= 1
			entry_linked = definition_html[len('@@@LINK='):last_non_whitespace_position+1]
			return f'<a href="{self._lookup_url_root + entry_linked}">{entry_linked}</a>'
		else:
			definition_html = definition_html.replace('entry://', self._lookup_url_root)
			return self._flatten_nested_a(definition_html)

	def _fix_sound_link(self, definition_html: str) -> str:
		# Use HTML sound element instead of the original <a> element, which looks like this:
		# <a class="hwd_sound sound audio_play_button icon-volume-up ptr fa fa-volume-up" data-lang="en_GB" data-src-mp3="https://www.collinsdictionary.com/sounds/hwd_sounds/EN-GB-W0020530.mp3" href="sound://audio/ef/7650.mp3" title="Pronunciation for "><img class="soundpng" src="api/cache/collinse22f/img/sound.png"></a>
		autoplay_string = 'autoplay'
		sound_element_template = '<audio controls %s src="%s">%s</audio>'
		not_found_fallback = '<span>%s</span>'
		while (sound_link_start_pos := definition_html.find('sound://')) != -1:
			sound_link_end_pos = definition_html.find('"', sound_link_start_pos)
			original_sound_link = definition_html[sound_link_start_pos:sound_link_end_pos]
			sound_link = original_sound_link.replace('sound://', self._href_root_dir)
			sound_path = os.path.join(self._resources_dir, sound_link[len(self._href_root_dir):])

			inner_html_start_pos = definition_html.find('>', sound_link_end_pos) + 1
			inner_html_end_pos = definition_html.find('</a>', inner_html_start_pos)
			inner_html = definition_html[inner_html_start_pos:inner_html_end_pos]
			outer_html_start_pos = definition_html.rfind('<a', 0, sound_link_start_pos)
			outer_html_end_pos = definition_html.find('</a>', inner_html_end_pos) + len('</a>')

			if os.path.isfile(sound_path):
				sound_html = sound_element_template % (autoplay_string, sound_link, inner_html)
				autoplay_string = ''
			else:
				sound_html = not_found_fallback % inner_html

			definition_html = definition_html[:outer_html_start_pos] + sound_html +\
				definition_html[outer_html_end_pos:]

		return definition_html

	def _fix_img_src(self, definition_html: str) -> str:
		img_tag_end_pos = 0
		while (img_tag_start_pos := definition_html.find('<img', img_tag_end_pos)) != -1:
			img_tag_end_pos = definition_html.find('>', img_tag_start_pos)
			img_src_start_pos = definition_html.find(' src="', img_tag_start_pos, img_tag_end_pos) + len(' src="')
			img_src_end_pos = definition_html.find('"', img_src_start_pos, img_tag_end_pos)
			img_src = definition_html[img_src_start_pos:img_src_end_pos]
			img_src = self._href_root_dir + img_src.replace('file://', '')
			definition_html = definition_html[:img_src_start_pos] + img_src + definition_html[img_src_end_pos:]
		return definition_html

	def clean(self, definition_html: str) -> str:
		definition_html = self._re_non_printing_chars.sub('', definition_html)
		if self._has_styles:
			definition_html = self._expand_compact_html(definition_html)
		definition_html = self._convert_single_quotes_to_double(definition_html)
		definition_html = self._fix_file_path(definition_html, '.css')
		self._isolate_css()
		definition_html = self._fix_file_path(definition_html, '.js')
		definition_html = self._fix_internal_href(definition_html)
		definition_html = self._fix_entry_cross_ref(definition_html)
		definition_html = self._fix_sound_link(definition_html)
		definition_html = self._fix_img_src(definition_html)
		return definition_html

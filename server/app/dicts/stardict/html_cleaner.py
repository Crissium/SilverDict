import re
import os
from pathlib import Path
import shutil

class HtmlCleaner:
	"""
	Cleans up HTML-formatted StarDict dictionaries. Does the following:
	- convert href="bword://Bogen" to href="/api/lookup/OxfordDuden/Bogen"
	- fix img src paths
	"""
	def __init__(self, dictionary_name: 'str', dictionary_path: 'str', resource_dir: 'str') -> 'None':
		self._original_res_dir = os.path.join(dictionary_path, 'res')
		self._new_res_dir = resource_dir
		self._href_root = '/api/cache/' + dictionary_name + '/'
		self._lookup_url_root = '/api/lookup/' + dictionary_name + '/'

		self._non_printing_chars_pattern = r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]'

		self._single_quotes_pattern = r"\'([^']*)\'"

		self._cross_ref_pattern = r'href="bword://([^"]+)"'
		self._cross_ref_replacement = r'href="' + self._lookup_url_root + r'\1"'

	def _remove_non_printing_chars(self, html: 'str') -> 'str':
		return re.sub(self._non_printing_chars_pattern, '', html)

	def _lower_html_tags(self, html: 'str') -> 'str':
		"""
		Converts the tags I use to lowercase. (for now: img)
		"""
		return html.replace('<IMG', '<img').replace('</IMG', '</img')

	def _convert_single_quotes_to_double(self, html: 'str') -> 'str':
		return re.sub(self._single_quotes_pattern, "\"\\1\"", html)
	
	def _fix_cross_ref(self, html: 'str') -> 'str':
		return re.sub(self._cross_ref_pattern, self._cross_ref_replacement, html)
	
	def _fix_src_path(self, html: 'str') -> 'str':
		img_tag_end_pos = 0
		while (img_tag_start_pos := html.find('<img', img_tag_end_pos)) != -1:
			img_tag_end_pos = html.find('>', img_tag_start_pos)
			img_src_start_pos = html.find(' src="', img_tag_start_pos, img_tag_end_pos) + len(' src="')
			img_src_end_pos = html.find('"', img_src_start_pos, img_tag_end_pos)
			img_src = html[img_src_start_pos:img_src_end_pos]
			original_file_path_on_disk = os.path.join(self._original_res_dir, img_src)
			if os.path.isfile(original_file_path_on_disk):
				new_file_path_on_disk = os.path.join(self._new_res_dir, img_src)
				if not os.path.isfile(new_file_path_on_disk):
					Path(self._new_res_dir).mkdir(parents=True, exist_ok=True)
					shutil.copyfile(original_file_path_on_disk, new_file_path_on_disk)
				html = html[:img_src_start_pos] + self._href_root + img_src + html[img_src_end_pos:]
		source_tag_end_pos = 0
		while (source_tag_start_pos := html.find('<source', source_tag_end_pos)) != -1:
			source_tag_end_pos = html.find('>', source_tag_start_pos)
			source_src_start_pos = html.find(' src="', source_tag_start_pos, source_tag_end_pos) + len(' src="')
			source_src_end_pos = html.find('"', source_src_start_pos, source_tag_end_pos)
			source_src = html[source_src_start_pos:source_src_end_pos]
			original_file_path_on_disk = os.path.join(self._original_res_dir, source_src)
			if os.path.isfile(original_file_path_on_disk):
				new_file_path_on_disk = os.path.join(self._new_res_dir, source_src)
				if not os.path.isfile(new_file_path_on_disk):
					Path(self._new_res_dir).mkdir(parents=True, exist_ok=True)
					shutil.copyfile(original_file_path_on_disk, new_file_path_on_disk)
				html = html[:source_src_start_pos] + self._href_root + source_src + html[source_src_end_pos:]
		return html

	def clean(self, html: 'str') -> 'str':
		html = self._remove_non_printing_chars(html)
		html = self._lower_html_tags(html)
		html = self._convert_single_quotes_to_double(html)
		html = self._fix_cross_ref(html)
		html = self._fix_src_path(html)
		return html

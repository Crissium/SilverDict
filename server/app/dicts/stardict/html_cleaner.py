import re
import os
import shutil


class HtmlCleaner:
	"""
	Cleans up HTML-formatted StarDict dictionaries. Does the following:
	- convert href="bword://Bogen" to href="api/lookup/OxfordDuden/Bogen"
	- fix img src paths
	- fix hrefs defined inside lemma class spans, e.g. <span class="lemma"><a href="%E1%BC%80%CE%B3%CE%B1%CE%B8%CE%BF%CE%B5%CF%81%CE%B3%E1%BD%B7%CE%B1">ἀγαθοεργία</a></span> -> <span class="lemma"><a href="api/lookup/morphology-grc/%E1%BC%80%CE%B3%CE%B1%CE%B8%CE%BF%CE%B5%CF%81%CE%B3%E1%BD%B7%CE%B1">ἀγαθοεργία</a></span>
	- remove outer <div class="article"></div> tag if present
	"""
	_non_printing_chars_pattern = re.compile(r'[\x00-\x1f\x7f-\x9f]')
	_single_quotes_pattern = re.compile(r"=\'([^']*)\'(?=[ >])")
	_cross_ref_pattern = re.compile(r'href="bword://([^"]+)"')

	def __init__(self, dictionary_name: str, dictionary_path: str, resource_dir: str) -> None:
		self._href_root = 'api/cache/' + dictionary_name + '/'
		self._lookup_url_root = 'api/lookup/' + dictionary_name + '/'

		if os.path.isdir(resource_dir) and not os.path.islink(resource_dir):
			shutil.rmtree(resource_dir)
		elif not os.path.islink(resource_dir):
			# os.symlink(os.path.join(dictionary_path, 'res'), resource_dir)
			typical_res_dir_name = os.path.join(dictionary_path, 'res')
			if os.path.isdir(typical_res_dir_name):
				os.symlink(typical_res_dir_name, resource_dir)
			else:
				for filename in os.listdir(dictionary_path):
					full_name = os.path.join(dictionary_path, filename)
					if filename.startswith(dictionary_name) and os.path.isdir(full_name):
						os.symlink(full_name, resource_dir)
						break

		self._cross_ref_replacement = 'href="' + self._lookup_url_root + r'\1"'

	def _remove_non_printing_chars(self, html: str) -> str:
		return self._non_printing_chars_pattern.sub('', html)

	def _lower_html_tags(self, html: str) -> str:
		"""
		Converts the tags I use to lowercase.
		"""
		return html.replace('<IMG', '<img').replace('</IMG', '</img').replace(' SRC=', ' src=').replace('<A HREF=', '<a href=').replace('</A>', '</a>').replace('<A href=', '<a href=')

	def _convert_single_quotes_to_double(self, html: str) -> str:
		return self._single_quotes_pattern.sub('="\\1"', html)

	def _fix_cross_ref(self, html: str) -> str:
		return self._cross_ref_pattern.sub(self._cross_ref_replacement, html)

	def _fix_lemma_href(self, html: str) -> str:
		lemma_tag_end_pos = 0
		while (lemma_tag_start_pos := html.find('<span class="lemma">', lemma_tag_end_pos)) != -1:
			lemma_tag_end_pos = html.find('</span>', lemma_tag_start_pos)
			href_start_pos = html.find(' href="', lemma_tag_start_pos, lemma_tag_end_pos) + len(' href="')
			href_end_pos = html.find('"', href_start_pos, lemma_tag_end_pos)
			href = html[href_start_pos:href_end_pos]
			html = html[:href_start_pos] + self._lookup_url_root + href + html[href_end_pos:]
		return html

	def _fix_src_path(self, html: str) -> str:
		img_tag_end_pos = 0
		while (img_tag_start_pos := html.find('<img', img_tag_end_pos)) != -1:
			img_tag_end_pos = html.find('>', img_tag_start_pos)
			img_src_start_pos = html.find(' src="', img_tag_start_pos, img_tag_end_pos) + len(' src="')
			img_src_end_pos = html.find('"', img_src_start_pos, img_tag_end_pos)
			img_src = html[img_src_start_pos:img_src_end_pos]
			# original_file_path_on_disk = os.path.join(self._original_res_dir, img_src)
			# new_file_path_on_disk = os.path.join(self._new_res_dir, img_src)
			# if not os.path.isfile(new_file_path_on_disk):
			# 	if os.path.isfile(original_file_path_on_disk):
			# 		Path(self._new_res_dir).mkdir(parents=True, exist_ok=True)
			# 		shutil.copyfile(original_file_path_on_disk, new_file_path_on_disk)
			# else:
			# 	if os.path.getmtime(original_file_path_on_disk) > os.path.getmtime(new_file_path_on_disk):
			# 		shutil.copyfile(original_file_path_on_disk, new_file_path_on_disk)
			html = html[:img_src_start_pos] + self._href_root + img_src + html[img_src_end_pos:]
		source_tag_end_pos = 0
		while (source_tag_start_pos := html.find('<source', source_tag_end_pos)) != -1:
			source_tag_end_pos = html.find('>', source_tag_start_pos)
			source_src_start_pos = html.find(' src="', source_tag_start_pos, source_tag_end_pos) + len(' src="')
			source_src_end_pos = html.find('"', source_src_start_pos, source_tag_end_pos)
			source_src = html[source_src_start_pos:source_src_end_pos]
			# original_file_path_on_disk = os.path.join(self._original_res_dir, source_src)
			# if not os.path.isfile(new_file_path_on_disk):
			# 	if os.path.isfile(original_file_path_on_disk):
			# 		Path(self._new_res_dir).mkdir(parents=True, exist_ok=True)
			# 		shutil.copyfile(original_file_path_on_disk, new_file_path_on_disk)
			# else:
			# 	if os.path.getmtime(original_file_path_on_disk) > os.path.getmtime(new_file_path_on_disk):
			# 		shutil.copyfile(original_file_path_on_disk, new_file_path_on_disk)
			html = html[:source_src_start_pos] + self._href_root + source_src + html[source_src_end_pos:]
		return html

	def _remove_outer_article_div(self, html: str) -> str:
		if html.startswith('<div class="article">') and html.endswith('</div>'):
			return html[len('<div class="article">'):-len('</div>')]
		else:
			return html

	def _fix_img_link(self, html: str) -> str:
		a_tag_end_pos = 0
		while (a_tag_start_pos := html.find('<a href="', a_tag_end_pos)) != -1:
			a_tag_end_pos = html.find('>', a_tag_start_pos)
			href_start_pos = html.find(' href="', a_tag_start_pos, a_tag_end_pos) + len(' href="')
			href_end_pos = html.find('"', href_start_pos, a_tag_end_pos)
			href = html[href_start_pos:href_end_pos]
			if href.endswith('.jpg')\
				or href.endswith('.png')\
				or href.endswith('.gif')\
				or href.endswith('.svg')\
				or href.endswith('.bmp')\
				or href.endswith('.jpeg'):
				html = html[:href_start_pos] + self._href_root + href + html[href_end_pos:]
		return html

	def _add_headword(self, html: str, headword: str) -> str:
		return f'<h3 class="headword">{headword}</h3>{html}'

	def clean(self, html: str, headword: str) -> str:
		html = self._remove_non_printing_chars(html)
		html = self._lower_html_tags(html)
		html = self._convert_single_quotes_to_double(html)
		html = self._fix_cross_ref(html)
		html = self._fix_lemma_href(html)
		html = self._fix_src_path(html)
		html = self._remove_outer_article_div(html)
		html = self._fix_img_link(html)
		return self._add_headword(html, headword)

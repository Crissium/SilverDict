import os
import shutil
import concurrent.futures
from zipfile import ZipFile
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
	import dsl
	dsl_module_found = True
except ImportError:
	logger.warning('Using the legacy pure Python parser for DSL. Consider installing dsl2html.')
	import re
	import html
	from xml.sax.saxutils import escape, quoteattr
	from .main import DSLParser
	dsl_module_found = False

	# order matters, a lot.
	shortcuts = [
		# canonical: m > * > ex > i > c
		(
			'[m1](?:-{2,})[/m]',
			'<hr/>',
		),
		(
			'[m(\\d)](?:-{2,})[/m]',
			'<hr style="margin-left:\\g<1>em"/>',
		),
	]

	shortcuts = [
		(
			re.compile(repl.replace('[', '\\[').replace('*]', '\\*]')),
			sub,
		) for (repl, sub) in shortcuts
	]

	def apply_shortcuts(text: str) -> str:
		for pattern, sub in shortcuts:
			text = pattern.sub(sub, text)
		return text

	htmlEntityPattern = re.compile(r'&#?\w+;')

	def unescape(text: str) -> str:
		def fixup(m: 're.Match') -> str:
			text = m.group(0)
			if text[:2] == "&#":
				# character reference
				try:
					if text[:3] == "&#x":
						i = int(text[3:-1], 16)
					else:
						i = int(text[2:-1])
				except ValueError:
					pass
				else:
					try:
						return chr(i)
					except ValueError:
						# f"\\U{i:08x}", but no fb"..."
						return (b"\\U%08x" % i).decode("unicode-escape")
			else:
				# named entity
				try:
					text = chr(html.entities.name2codepoint[text[1:-1]])
				except KeyError:
					pass
			return text  # leave as is
		return htmlEntityPattern.sub(fixup, text)

	def make_a_href(s: str, href_root: str) -> str:
		return f'<a href={quoteattr(href_root + s)}>{escape(s)}</a>'

class DSLConverter:
	if not dsl_module_found:
		re_brackets_blocks = re.compile(r'\{\{[^}]*\}\}')
		re_lang_open = re.compile(r'(?<!\\)\[lang[^\]]*\]')
		re_m_open = re.compile(r'(?<!\\)\[m\d\]')
		re_c_open_color = re.compile(r'\[c (\w+)\]')
		re_m = re.compile(r'\[m(\d)\](.*?)\[/m\]')
		re_end = re.compile(r'\\$')
		re_ref = re.compile('<<(.*?)>>')
		re_remnant_m = re.compile(r'\[(?:/m|m[^]]*)\]')

		_REF_PATTERN = r'&lt;&lt;([^&]+)&gt;&gt;'

		IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'tif', 'tiff', 'ico', 'webp', 'avif', 'apng', 'jfif', 'pjpeg', 'pjp']
		IMAGE_EXTENSIONS += [extension.upper() for extension in IMAGE_EXTENSIONS]
		SOUND_EXTENSIONS = ['mp3', 'ogg', 'wav', 'wave']
		SOUND_EXTENSIONS += [extension.upper() for extension in SOUND_EXTENSIONS]
		VIDEO_EXTENSIONS = ['mp4', 'webm', 'ogv', 'ogg']
		VIDEO_EXTENSIONS += [extension.upper() for extension in VIDEO_EXTENSIONS]

		def _replace_ref_match(self, match: re.Match) -> str:
			word = match.group(1)
			return f'<a href="{self._lookup_url_root}{word}">{word}</a>'

		def ref_sub(self, x: re.Match) -> str:
			return make_a_href(unescape(x.groups()[0]), self._lookup_url_root)

		def _clean_tags(self, line: str) -> str:
			# remove {{...}} blocks
			line = self.re_brackets_blocks.sub('', line)

			# remove trn tags
			line = line.replace('[trn]', '').replace('[/trn]', '').replace('[trs]', '').replace('[/trs]','').replace('[!trn]', '').replace('[/!trn]', '').replace('[!trs]', '').replace('[/!trs]', '')

			# remove lang tags
			line = self.re_lang_open.sub('', line).replace('[/lang]', '')

			# remove com tags
			line = line.replace('[com]', '').replace('[/com]', '')

			# escape html special characters like '<' and '>'
			line = html.escape(html.unescape(line))

			# remove t tags
			line = line.replace(
				'[t]',
				'<font face="Helvetica" class="dsl_t">',
			)
			line = line.replace('[/t]', '</font>')

			line = self._parser.parse(line)

			line = self.re_end.sub('<br/>', line)

			# paragraph, part one: before shortcuts.
			line = line.replace('[m]', '[m1]')
			# if text somewhere contains "[m_]" tag like
			# "[b]I[/b][m1] [c][i]conj.[/i][/c][/m][m1]1) ...[/m]"
			# then leave it alone.  only wrap in "[m1]" when no "m" tag found at all.
			if not self.re_m_open.search(line):
				line = '[m1]%s[/m]' % line

			line = apply_shortcuts(line)

			# paragraph, part two: if any not shourcuted [m] left?
			line = self.re_m.sub(r'<div style="margin-left:\g<1>em">\g<2></div>', line)

			# text formats
			line = line.replace("[']", "<u>").replace("[/']", "</u>")
			line = line.replace("[b]", "<b>").replace("[/b]", "</b>")
			line = line.replace("[i]", "<i>").replace("[/i]", "</i>")
			line = line.replace("[u]", "<u>").replace("[/u]", "</u>")
			line = line.replace("[sup]", "<sup>").replace("[/sup]", "</sup>")
			line = line.replace("[sub]", "<sub>").replace("[/sub]", "</sub>")

			# color
			line = line.replace("[c]", "<font color=\"darkgreen\">")
			line = self.re_c_open_color.sub("<font color=\"\\g<1>\">", line)
			line = line.replace("[/c]", "</font>")

			# example zone
			line = line.replace("[ex]", "<span class=\"ex\"><font color=\"grey\">")
			line = line.replace("[/ex]", "</font></span>")

			# secondary zone
			line = line.replace("[*]", "<span class=\"sec\">")\
				.replace("[/*]", "</span>")

			# abbrev. label
			line = line.replace("[p]", "<i class=\"p\"><font color=\"green\">")
			line = line.replace("[/p]", "</font></i>")

			# cross reference
			line = line.replace("[ref]", "<<").replace("[/ref]", ">>")
			line = line.replace("[url]", "<<").replace("[/url]", ">>")
			line = self.re_ref.sub(self.ref_sub, line)

			# \[...\]
			line = line.replace("\\[", "[").replace("\\]", "]")

			# preserve newlines
			if not line.endswith('>') and not line.endswith('[/m]'):
				line += '<br/>'

			return line

		def _correct_media_references(self, html: str) -> tuple[str, list[str]]:
			files_to_be_extracted = []
			s_tag_end_position = 0
			autoplay_string = 'autoplay'
			while True:
				s_tag_begin_position = html.find('[s]', s_tag_end_position)
				if s_tag_begin_position == -1:
					break
				s_tag_end_position = html.find('[/s]', s_tag_begin_position)
				if s_tag_end_position == -1:
					break
				media_name = html[s_tag_begin_position+len('[s]'):s_tag_end_position]

				if not os.path.isfile(os.path.join(self._resources_dir, media_name)):
					files_to_be_extracted.append(media_name)
					if self._resources_extracted:
						logger.warning('Media file %s not found in resources directory %s' % (media_name, self._resources_dir))

				media_ref = self._href_root + media_name
				if media_name.split('.')[-1] in self.IMAGE_EXTENSIONS:
					proper_media_html = '<img src="%s" />' % media_ref
				elif media_name.split('.')[-1] in self.SOUND_EXTENSIONS:
					proper_media_html = '<audio controls %s src="%s">%s</audio>' % (autoplay_string, media_ref, media_name)
					autoplay_string = ''
				elif media_name.split('.')[-1] in self.VIDEO_EXTENSIONS:
					proper_media_html = '<video controls src="%s">video</video>' % media_ref
				else:
					proper_media_html = '<a href="%s">%s</a>' % (media_ref, media_name)
				html = html.replace('[s]%s[/s]' % media_name, proper_media_html)
			return html, files_to_be_extracted

		def _clean_html(self, html: str) -> tuple[str, list[str]]:
			# remove strange '\\ '
			html = html.replace('\\ ', '')

			# remove remnant [m] tags
			html = self.re_remnant_m.sub('', html)

			# make references
			html = re.sub(self._REF_PATTERN, self._replace_ref_match, html)

			html, files_to_be_extracted = self._correct_media_references(html)

			return html, files_to_be_extracted

	def __init__(self, dict_filename: str, dict_name: str, resources_dir: str, resources_extracted: bool) -> None:
		if not resources_extracted:
			base, extension = os.path.splitext(dict_filename)
			if extension == '.dz':
				base = base[:-len('.dsl')]
			dirname = os.path.dirname(dict_filename)
			for filename in os.listdir(dirname):
				full_filename = os.path.join(dirname, filename)
				if full_filename.startswith(base) and full_filename.find('.files') != -1:
					if os.path.isdir(full_filename):
						if not os.path.islink(resources_dir):
							if os.path.isdir(resources_dir):
								shutil.rmtree(resources_dir)
							elif os.path.isfile(resources_dir):
								os.remove(resources_dir)
							os.symlink(full_filename, resources_dir)
					else: # file or link of file (a zip archive)
						self._resources_filename = full_filename
					break

			try:
				self._resources_filename
			except AttributeError:
				self._resources_filename = ''

		if dsl_module_found:
			self._name_dict = dict_name
		else:
			self._href_root = '/api/cache/' + dict_name + '/'
			self._lookup_url_root = '/api/lookup/' + dict_name + '/'
			self._parser = DSLParser()

		self._resources_extracted = resources_extracted
		self._resources_dir = resources_dir

	def _extract_files(self, files_to_be_extracted: list[str]) -> None:
		files_to_be_extracted = [filename for filename in files_to_be_extracted if not os.path.isfile(os.path.join(self._resources_dir, filename))]
		if not self._resources_extracted and files_to_be_extracted and self._resources_filename and os.path.isfile(self._resources_filename):
		# ZipFile's extractall() is too slow, so we use a thread pool to extract files in parallel.
			with ZipFile(self._resources_filename) as zip_file:
				with concurrent.futures.ThreadPoolExecutor(len(files_to_be_extracted)) as executor:
					executor.map(zip_file.extract, files_to_be_extracted, [self._resources_dir] * len(files_to_be_extracted))

	def convert(self, record: tuple[str, str, int]) -> tuple[str, int]:
		text, headword, offset_in_dsl = record
		if dsl_module_found:
			text, files_to_be_extracted = dsl.to_html(text, self._name_dict)
		else:
			lines = text.splitlines()
			definition_html = []
			for line in lines:
				if line.startswith(' [m') and not line.endswith('[/m]'):
					line += '[/m]'
				definition_html.append(self._clean_tags(line))
			text, files_to_be_extracted = self._clean_html('\n'.join(definition_html))
		self._extract_files(files_to_be_extracted)
		return '<h3 class="headword">%s</h3>' % headword + text, offset_in_dsl

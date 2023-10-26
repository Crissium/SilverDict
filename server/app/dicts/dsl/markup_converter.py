import re
import os
import shutil
import html
import concurrent.futures
from zipfile import ZipFile
from xml.sax.saxutils import escape, quoteattr
from .main import DSLParser
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

def apply_shortcuts(text: 'str') -> 'str':
	for pattern, sub in shortcuts:
		text = pattern.sub(sub, text)
	return text

htmlEntityPattern = re.compile(r"&#?\w+;")

def unescape(text: str) -> str:
	def fixup(m: "re.Match") -> str:
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

def make_a_href(s: 'str', href_root: 'str') -> 'str':
	return f"<a href={quoteattr(href_root + s)}>{escape(s)}</a>"

class DSLConverter:
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

	def _replace_ref_match(self, match: 're.Match') -> 'str':
		word = match.group(1)
		return f'<a href="{self._lookup_url_root}{word}">{word}</a>'

	def ref_sub(self, x: 're.Match') -> 'str':
		return make_a_href(unescape(x.groups()[0]), self._lookup_url_root)

	def __init__(self, dict_filename: 'str', dict_name: 'str', resources_dir: 'str', resources_extracted: 'bool') -> None:
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
							os.link(full_filename, resources_dir)
					else: # file or link of file (a zip archive)
						self._resources_filename = full_filename
					break

			try:
				self._resources_filename
			except AttributeError:
				self._resources_filename = ''

		self._resources_extracted = resources_extracted
		self._resources_dir = resources_dir
		self._href_root = '/api/cache/' + dict_name + '/'
		self._lookup_url_root = '/api/lookup/' + dict_name + '/'
		self._parser = DSLParser()

	def _clean_tags(self, text: 'str') -> 'str':
		# remove {{...}} blocks
		text = self.re_brackets_blocks.sub('', text)

		# remove trn tags
		text = text.replace('[trn]', '').replace('[/trn]', '').replace('[trs]', '').replace('[/trs]','').replace('[!trn]', '').replace('[/!trn]', '').replace('[!trs]', '').replace('[/!trs]', '')

		# remove lang tags
		text = self.re_lang_open.sub('', text).replace('[/lang]', '')

		# remove com tags
		text = text.replace('[com]', '').replace('[/com]', '')

		# escape html special characters like '<' and '>'
		text = html.escape(html.unescape(text))

		# remove t tags
		text = text.replace(
			'[t]',
			'<font face="Helvetica" class="dsl_t">',
		)
		text = text.replace('[/t]', '</font>')

		text = self._parser.parse(text)

		text = self.re_end.sub('<br/>', text)

		# paragraph, part one: before shortcuts.
		text = text.replace('[m]', '[m1]')
		# if text somewhere contains "[m_]" tag like
		# "[b]I[/b][m1] [c][i]conj.[/i][/c][/m][m1]1) ...[/m]"
		# then leave it alone.  only wrap in "[m1]" when no "m" tag found at all.
		if not self.re_m_open.search(text):
			text = '[m1]%s[/m]' % text

		text = apply_shortcuts(text)

		# paragraph, part two: if any not shourcuted [m] left?
		text = self.re_m.sub(r'<div style="margin-left:\g<1>em">\g<2></div>', text)

		# text formats
		text = text.replace("[']", "<u>").replace("[/']", "</u>")
		text = text.replace("[b]", "<b>").replace("[/b]", "</b>")
		text = text.replace("[i]", "<i>").replace("[/i]", "</i>")
		text = text.replace("[u]", "<u>").replace("[/u]", "</u>")
		text = text.replace("[sup]", "<sup>").replace("[/sup]", "</sup>")
		text = text.replace("[sub]", "<sub>").replace("[/sub]", "</sub>")

		# color
		text = text.replace("[c]", "<font color=\"green\">")
		text = self.re_c_open_color.sub("<font color=\"\\g<1>\">", text)
		text = text.replace("[/c]", "</font>")

		# example zone
		text = text.replace("[ex]", "<span class=\"ex\"><font color=\"steelblue\">")
		text = text.replace("[/ex]", "</font></span>")

		# secondary zone
		text = text.replace("[*]", "<span class=\"sec\">")\
			.replace("[/*]", "</span>")

		# abbrev. label
		text = text.replace("[p]", "<i class=\"p\"><font color=\"green\">")
		text = text.replace("[/p]", "</font></i>")

		# cross reference
		text = text.replace("[ref]", "<<").replace("[/ref]", ">>")
		text = text.replace("[url]", "<<").replace("[/url]", ">>")
		text = self.re_ref.sub(self.ref_sub, text)

		# \[...\]
		text = text.replace("\\[", "[").replace("\\]", "]")

		# preserve newlines
		return text.replace('\n', '<br/>')

	def _correct_media_references(self, html: 'str') -> 'tuple[str, list[str]]':
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
	
	def _extract_files(self, files_to_be_extracted: 'list[str]') -> 'None':
		# ZipFile's extractall() is too slow, so we use a thread pool to extract files in parallel.
		with ZipFile(self._resources_filename) as zip_file:
			with concurrent.futures.ThreadPoolExecutor() as executor:
				executor.map(zip_file.extract, files_to_be_extracted, [self._resources_dir] * len(files_to_be_extracted))

	def _clean_html(self, html: 'str') -> 'str':
		# remove strange '\\ '
		html = html.replace('\\ ', '')

		# remove remnant [m] tags
		html = self.re_remnant_m.sub('', html)

		# make references
		html = re.sub(self._REF_PATTERN, self._replace_ref_match, html)

		html, files_to_be_extracted = self._correct_media_references(html)
		if not self._resources_extracted and files_to_be_extracted and self._resources_filename and os.path.isfile(self._resources_filename):
			self._extract_files(files_to_be_extracted)

		return html

	def convert(self, text: 'str', headword: 'str') -> 'str':
		for line in text.splitlines():
			if line.startswith(' [m') and not line.endswith('[/m]'):
				text = text.replace(line, line + '[/m]')

		text = self._clean_tags(text)

		text = self._clean_html(text)

		text = '<h3 class="headword">%s</h3>' % headword + text

		return text

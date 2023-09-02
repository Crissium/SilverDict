import re
from .xdxf_transform import XdxfTransformer

class XdxfCleaner:
	IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'tif', 'tiff', 'ico', 'webp', 'avif', 'apng', 'jfif', 'pjpeg', 'pjp']
	IMAGE_EXTENSIONS += [extension.upper() for extension in IMAGE_EXTENSIONS]
	SOUND_EXTENSIONS = ['mp3', 'ogg', 'wav', 'wave']
	SOUND_EXTENSIONS += [extension.upper() for extension in SOUND_EXTENSIONS]

	def __init__(self) -> 'None':
		self._rref_pattern = r'<\s*rref\s*>(.*?)<\s*/\s*rref\s*>'
		# self._rref_replacement = r'<img>$1</img>' # A hacky work-around for the fact that pyglossary does not handle <rref> well.

		self._transformer = XdxfTransformer(encoding='utf-8')

	def clean(self, xdxf: 'str') -> 'str':
		"""
		Returns HTML that should be further cleaned.
		"""
		extracted_resources_names : 'list[str]' = []
		def extract_resources(match: 're.Match[str]') -> 'str':
			extracted_resources_names.append(match.group(1))
			return f'<img>{match.group(1)}</img>'
		xdxf = re.sub(self._rref_pattern, extract_resources, xdxf)

		html = self._transformer.transformByInnerString(xdxf)

		for resource in extracted_resources_names:
			if resource.split('.')[-1] in self.IMAGE_EXTENSIONS:
				proper_resource_html = '<img src="%s" />' % resource
			elif resource.split('.')[-1] in self.SOUND_EXTENSIONS:
				proper_resource_html = '<audio controls autoplay src="%s">audio</audio>' % resource
			else:
				proper_resource_html = '<a href="%s">download media</a>' % (resource, resource)
			html = html.replace('<img></img>', proper_resource_html, 1)
		
		return html
from .stardict import IdxFileReader, IfoFileReader, SynFileReader, DictFileReader
from .html_cleaner import HtmlCleaner
try:
	from .xdxf_cleaner import XdxfCleaner
except ImportError:
	pass
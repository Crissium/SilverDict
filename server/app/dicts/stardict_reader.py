import os
from .base_reader import BaseReader
from .. import db_manager
from .stardict import IdxFileReader, IfoFileReader, DictFileReader, HtmlCleaner, XdxfCleaner
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class StarDictReader(BaseReader):
	"""
	Adapted from stardictutils.py by J.F. Dockes.
	"""
	CTTYPES = ['m', 't', 'y', 'g', 'x', 'h']

	@staticmethod
	def _stardict_filenames(base_filename: 'str') -> 'tuple[str, str, str, str]':
		ifofile = base_filename + '.ifo'
		idxfile = base_filename + '.idx'
		if not os.path.isfile(idxfile):
			idxfile += '.gz'
		dictfile = base_filename + '.dict.dz'
		synfile = base_filename + 'syn.dz'
		return ifofile, idxfile, dictfile, synfile

	def __init__(self,
	      		 name: 'str',
				 filename: 'str', # .ifo
				 display_name: 'str',) -> 'None':
		super().__init__(name, filename, display_name)
		filename_no_extension, extension = os.path.splitext(filename)
		self.ifofile, idxfile, self.dictfile, synfile = self._stardict_filenames(filename_no_extension)

		if not db_manager.dictionary_exists(self.name):
			db_manager.drop_index()
			idx_reader = IdxFileReader(idxfile)
			for word_str in idx_reader._word_idx:
				spans = idx_reader.get_index_by_word(word_str)
				word_decoded = word_str.decode('utf-8')
				for offset, size in spans:
					db_manager.add_entry(self.simplify(word_decoded), self.name, word_decoded, offset, size)
			db_manager.commit()
			db_manager.create_index()
			logger.info('Entries of dictionary %s added to database' % self.name)

		self._relative_root_dir = filename_no_extension.split('/')[-1]
		assert self._relative_root_dir == name
		self._resources_dir = os.path.join(self._CACHE_ROOT, self._relative_root_dir)

		self._html_cleaner = HtmlCleaner(self.name, os.path.dirname(self.filename), self._resources_dir)
		self._xdxf_cleaner = XdxfCleaner()

	def _get_records(self, offset: 'int', size: 'int') -> 'list[tuple[str, str]]':
		"""
		Returns a list of tuples (cttype, article).
		cttypes are:
		m, t, y: text
		g: pango, pretty HTML-like, rarely seen
		x: xdxf
		h: html
		"""
		ifo_reader = IfoFileReader(self.ifofile)
		if not os.path.isfile(self.dictfile): # it is possible that it is not dictzipped
			from .idzip.command import _compress
			class Options:
				suffix = '.dz'
				keep = False
			_compress(self.dictfile[:-len(Options.suffix)], Options)
		dict_reader = DictFileReader(self.dictfile, ifo_reader, None)
		entries = dict_reader.get_dict_by_offset_size(offset, size)
		result = []
		for entry in entries:
			for cttype, data in entry.items():
				if cttype in self.CTTYPES:
					result.append((cttype, data.decode('utf-8')))
		return result

	def _clean_up_markup(self, record: 'tuple[str, str]') -> 'str':
		"""
		Cleans up the markup according the cttype and returns valid HTML.
		"""
		cttype, article = record
		match cttype:
			case 'm' | 't' | 'y':
				# text, wrap in <p>
				return '<p>' + article.replace('\n', '<br/>') + '</p>'
			case 'g':
				# I won't work on this until I see a dictionary thus formatted
				return '<p>Warning: This dictionary uses the pango markup format, which is not supported yet. I would appreciate it if you could send me a sample dictionary so that I may work on it. Please file an issue on <a href="https://github.com/Crissium/SilverDict/issues">GitHub</a> or send me an e-mail. You can find my e-mail address in the git log.</p><hr/>' + article
			case 'x':
				article = self._xdxf_cleaner.clean(article)
				return self._html_cleaner.clean(article)
			case 'h':
				return self._html_cleaner.clean(article)
			case _:
				raise ValueError('Unknown cttype %s' % cttype)
		
	def entry_definition(self, entry: 'str') -> 'str':
		locations = db_manager.get_entries(entry, self.name)
		records = []
		for word, offset, length in locations:
			# if word == entry:
				records += self._get_records(offset, length)
		records = [self._clean_up_markup(record) for record in records]
		return self._ARTICLE_SEPARATOR.join(records)

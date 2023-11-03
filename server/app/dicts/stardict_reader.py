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
		synfile = base_filename + 'syn.dz' # not used at the moment
		return ifofile, idxfile, dictfile, synfile

	def __init__(self,
	      		 name: 'str',
				 filename: 'str', # .ifo
				 display_name: 'str',
				 load_content_into_memory: 'bool'=False) -> 'None':
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

		self._relative_root_dir = name
		# assert self._relative_root_dir == name
		# This assertion won't hold when the filename contains dots
		self._resources_dir = os.path.join(self._CACHE_ROOT, self._relative_root_dir)

		self.ifo_reader = IfoFileReader(self.ifofile)

		self._html_cleaner = HtmlCleaner(self.name, os.path.dirname(self.filename), self._resources_dir)
		self._xdxf_cleaner = XdxfCleaner()

		self._loaded_content_into_memory = load_content_into_memory
		if load_content_into_memory:
			locations_all = db_manager.get_entries_all(self.name)
			self._content : 'dict[str, list[str]]' = {} # key -> [definition_html]
			if not os.path.isfile(self.dictfile): # it is possible that it is not dictzipped
				from idzip.command import _compress
				class Options:
					suffix = '.dz'
					keep = False
				_compress(self.dictfile[:-len(Options.suffix)], Options)
			dict_reader = DictFileReader(self.dictfile, self.ifo_reader, None)
			for key, word, offset, size in locations_all:
				records = self._get_records(dict_reader, offset, size)
				self._content.setdefault(key, []).extend([self._clean_up_markup(r, word) for r in records])
			dict_reader.close()

	def _get_records(self, dict_reader: 'DictFileReader', offset: 'int', size: 'int') -> 'list[tuple[str, str]]':
		"""
		Returns a list of tuples (cttype, article).
		cttypes are:
		m, t, y: text
		g: pango, pretty HTML-like, rarely seen, tentatively treated as regular HTML as I have seen no irregularities
		x: xdxf
		h: html
		"""
		entries = dict_reader.get_dict_by_offset_size(offset, size)
		result = []
		for entry in entries:
			for cttype, data in entry.items():
				if cttype in self.CTTYPES:
					result.append((cttype, data.decode('utf-8')))
		return result

	def _clean_up_markup(self, record: 'tuple[str, str]', headword: 'str') -> 'str':
		"""
		Cleans up the markup according the cttype and returns valid HTML.
		"""
		cttype, article = record
		match cttype:
			case 'm' | 't' | 'y':
				# text, wrap in <p>
				return '<h3 class="headword">%s</h3>' % headword +\
							'<p>' + article.replace('\n', '<br/>') + '</p>'
			case 'x':
				article = self._xdxf_cleaner.clean(article)
				return self._html_cleaner.clean(article, headword)
			case 'h' | 'g':
				return self._html_cleaner.clean(article, headword)
			case _:
				raise ValueError('Unknown cttype %s' % cttype)

	def _get_records_in_batch(self, locations: 'list[tuple[str, int, int]]') -> 'list[str]':
		if not os.path.isfile(self.dictfile): # it is possible that it is not dictzipped
			from idzip.command import _compress
			class Options:
				suffix = '.dz'
				keep = False
			_compress(self.dictfile[:-len(Options.suffix)], Options)
		dict_reader = DictFileReader(self.dictfile, self.ifo_reader, None)
		records = []
		for word, offset, size in locations:
			records.extend([self._clean_up_markup(r, word) for r in self._get_records(dict_reader, offset, size)])
		dict_reader.close()
		return records

	def entry_definition(self, entry: 'str') -> 'str':
		if self._loaded_content_into_memory:
			articles = self._content.get(entry)
			return self._ARTICLE_SEPARATOR.join(articles)
		else:
			locations = db_manager.get_entries(entry, self.name)
			records = self._get_records_in_batch(locations)
			return self._ARTICLE_SEPARATOR.join(records)

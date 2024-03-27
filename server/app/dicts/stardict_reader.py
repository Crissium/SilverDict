import os
import pickle
from .base_reader import BaseReader
from .. import db_manager
from .stardict import IdxFileReader, IfoFileReader, SynFileReader, DictFileReader, HtmlCleaner
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
	import xdxf2html
	xdxf2html_found = True
except ImportError:
	logger.warning('xdxf2html not found. Using pure Python parser.'
				   'Consider installing the module to improve speed.')
	xdxf2html_found = False
	from .stardict import XdxfCleaner


class StarDictReader(BaseReader):
	"""
	Adapted from stardictutils.py by J.F. Dockes.
	"""
	CTTYPES = ['m', 't', 'y', 'g', 'x', 'h']

	@staticmethod
	def _stardict_filenames(base_filename: str) -> tuple[str, str, str, str]:
		ifofile = base_filename + '.ifo'
		idxfile = base_filename + '.idx'
		if not os.path.isfile(idxfile):
			idxfile += '.gz'
		dictfile = base_filename + '.dict.dz'
		synfile = base_filename + '.syn'
		return ifofile, idxfile, dictfile, synfile

	def __init__(self,
				 name: str,
				 filename: str, # .ifo
				 display_name: str,
				 load_synonyms: bool = False,
				 load_content_into_memory: bool = False) -> None:
		super().__init__(name, filename, display_name)
		filename_no_extension, extension = os.path.splitext(filename)
		self._ifofile, idxfile, self._dictfile, synfile = self._stardict_filenames(filename_no_extension)
		self._syn_pickle_filename = os.path.join(self._CACHE_ROOT, self.name + '.syn')
		self._load_synonyms = load_synonyms

		if not db_manager.dictionary_exists(self.name):
			db_manager.drop_index()
			idx_reader = IdxFileReader(idxfile)
			for word_str in idx_reader._word_idx:
				spans = idx_reader.get_index_by_word(word_str)
				word_decoded = word_str.decode('utf-8')
				for offset, size in spans:
					db_manager.add_entry(self.simplify(word_decoded), self.name, word_decoded, offset, size)
			db_manager.commit_new_entries(self.name)
			db_manager.create_index()
			logger.info(f'Entries of dictionary {self.name} added to database')

		if not os.path.isfile(self._syn_pickle_filename):
			synonyms: dict[str, list[str]] = dict()
			try:
				idx_reader
			except NameError:
				idx_reader = IdxFileReader(idxfile)
			for index, synonym_list in SynFileReader(synfile).syn_dict.items():
				word_str, offset, size = idx_reader.get_index_by_num(index)
				word_decoded = word_str.decode('utf-8')
				synonyms[word_decoded] = synonym_list
			with open(self._syn_pickle_filename, 'wb') as f:
				pickle.dump(synonyms, f)

		if load_synonyms:
			with open(self._syn_pickle_filename, 'rb') as f:
				self._synonyms = pickle.load(f)

		self._relative_root_dir = name
		self._resources_dir = os.path.join(self._CACHE_ROOT, self._relative_root_dir)

		self._ifo_reader = IfoFileReader(self._ifofile)

		self._loaded_content_into_memory = load_content_into_memory
		if load_content_into_memory:
			self._content_dictfile = DictFileReader(self._dictfile, self._ifo_reader, None, True)

		# The constructor of the html cleaner will link the resources directory
		self._html_cleaner = HtmlCleaner(self.name, os.path.dirname(self.filename), self._resources_dir)
		if not xdxf2html_found:
			self._xdxf_cleaner = XdxfCleaner()

	def _get_records(self, dict_reader: DictFileReader, offset: int, size: int) -> list[tuple[str, str]]:
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

	def _get_synonyms(self, word: str) -> str:
		"""
		Return HTML-formatted synonym list, in the form of:
		<div>
			Syn: <a href="/api/lookup/dict_name/word">word</a>, <a href="/api/lookup/dict_name/word2">word2</a>
		</div>
		"""
		if self._load_synonyms:
			if word in self._synonyms:
				return '<div>Syn: ' + ', '.join([f'<a href="/api/lookup/{self.name}/{synonym}">{synonym}</a>'
									 			for synonym in self._synonyms[word]]) + '</div>'
		return ''

	def _clean_up_markup(self, record: tuple[str, str], headword: str) -> str:
		"""
		Cleans up the markup according the cttype and returns valid HTML.
		"""
		cttype, article = record
		match cttype:
			case 'm' | 't' | 'y':
				# text, wrap in <p>
				return f'<h3 class="headword">{headword}</h3>' +\
					'<p>' + article.replace('\n', '<br/>') + '</p>'
			case 'x':
				if xdxf2html_found:
					return xdxf2html.convert(article, self.name) + self._get_synonyms(headword)
				else:
					return self._html_cleaner.clean(self._xdxf_cleaner.clean(article), headword) +\
						self._get_synonyms(headword)
			case 'h' | 'g':
				return self._html_cleaner.clean(article, headword) + self._get_synonyms(headword)
			case _:
				raise ValueError(f'Unknown cttype {cttype}')

	def _get_records_in_batch(self, locations: list[tuple[str, int, int]]) -> list[str]:
		if not os.path.isfile(self._dictfile): # it is possible that it is not dictzipped
			from idzip.command import _compress
			class Options:
				suffix = '.dz'
				keep = False
			_compress(self._dictfile[:-len(Options.suffix)], Options)
		if self._loaded_content_into_memory:
			dict_reader = self._content_dictfile
		else:
			dict_reader = DictFileReader(self._dictfile, self._ifo_reader, None)
		records = []
		for word, offset, size in locations:
			records.extend([self._clean_up_markup(r, word) for r in self._get_records(dict_reader, offset, size)])
		if not self._loaded_content_into_memory:
			dict_reader.close()
		return records

	def get_definition_by_key(self, entry: str) -> str:
		locations = db_manager.get_entries(entry, self.name)
		records = self._get_records_in_batch(locations)
		return self._ARTICLE_SEPARATOR.join(records)

	def get_definition_by_word(self, headword: str) -> str:
		locations = db_manager.get_entries_with_headword(headword, self.name)
		records = self._get_records_in_batch([(headword, *location) for location in locations])
		return self._ARTICLE_SEPARATOR.join(records)

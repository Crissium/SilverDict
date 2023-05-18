# TODO: Learn system programming and read the dictzip code to understand how it works.
# Now I do not know how to random-access a .dsl.dz file, and if I choose to keep the
# dictionary text in memory, it will be too inefficient.
from .base_reader import BaseReader
import os
import shutil
import re
import html
import html.entities
from zipfile import ZipFile
import gzip
from xml.sax.saxutils import escape, quoteattr


class DSLReader(BaseReader):
	"""
	Homegrown reader for DSL dictionaries.
	Fingers crossed that it works well.

	Kudos to the people at Lingvo. DSL files are very well formed, compared to MDict.
	The header, each line of which begins with '#', contains metadata.
	Then comes the body, with one or more entries occupying unindented lines, followed
	by the definition, indented by a single tab.

	The only thing that I can complain about is its uncommon encoding: UTF-16 LE.
	"""
	def _read_dictionary_text(self) -> 'str':
		with gzip.open(self._filename) as dict_gzip:
			dictionary_text = dict_gzip.read().decode('utf-16-le')
		return dictionary_text
	
	def __init__(self, filename: 'str', display_name: 'str') -> None:
		super().__init__(filename, display_name)

		# Validate file type by checking the extension
		if not filename.endswith('.dsl.dz'): # I myself have only seen .dsl.dz files
			raise ValueError('Invalid file type %s' % filename)
		
		self._entry_pos :'dict[str, int]' = {} # Maps entry to its position in the dictionary text

		dictionary_text = self._read_dictionary_text()
		current_positon = 0	
		for line in dictionary_text.splitlines():
			if not line.startswith('#') and not line.startswith('\ufeff') and not line.startswith('\t'):
				word = line.replace('{·}', '') # Remove the {·} marker
				if word:
					self._entry_pos[word] = current_positon
			current_positon += len(line) + 1 # +1 for the newline character
		

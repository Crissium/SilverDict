import os
import shutil
import dsl
import concurrent.futures
from zipfile import ZipFile
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DSLConverter:
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

		self._name_dict = dict_name
		self._resources_extracted = resources_extracted
		self._resources_dir = resources_dir

	def _extract_files(self, files_to_be_extracted: 'list[str]') -> 'None':
		if not self._resources_extracted and files_to_be_extracted and self._resources_filename and os.path.isfile(self._resources_filename):
		# ZipFile's extractall() is too slow, so we use a thread pool to extract files in parallel.
			with ZipFile(self._resources_filename) as zip_file:
				with concurrent.futures.ThreadPoolExecutor(len(files_to_be_extracted)) as executor:
					executor.map(zip_file.extract, files_to_be_extracted, [self._resources_dir] * len(files_to_be_extracted))

	def convert(self, record: 'tuple[str, str]') -> 'str':
		text, headword = record
		text, files_to_be_extracted = dsl.to_html(text, self._name_dict)
		self._extract_files(files_to_be_extracted)
		return '<h3 class="headword">%s</h3>' % headword + text

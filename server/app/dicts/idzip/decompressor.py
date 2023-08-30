import os
import struct
import zlib
import itertools
from io import BytesIO, open

from . import compressor, caching
from ._stream import IOStreamWrapperMixin

GZIP_CRC32_LEN = 4

SELECTED_CACHE = caching.OneItemCache

class IdzipReader(IOStreamWrapperMixin):
	def __init__(self, filename=None, fileobj=None):
		if filename is None:
			if fileobj:
				self._fileobj = fileobj
				self._should_close = False
				try:
					self.name = fileobj.name
				except AttributeError:
					self.name = ''
			else:
				raise ValueError("Must provide a filename or a fileobj argument")
		else:
			self.name = filename
			self._should_close = True
			self._fileobj = open(filename, "rb")
		# The current position in the decompressed data.
		self._pos = 0
		self._members = []
		self._last_zstream_end = None
		self._chunks = []
		self._cache = SELECTED_CACHE()

		self._read_member_header()

	@property
	def stream(self):
		return self._fileobj

	def _read_member_header(self):
		"""Extends self._members and self._chunks
		by the read header data.
		"""
		header = _read_gzip_header(self._fileobj)
		offset = self._fileobj.tell()
		if "RA" not in header["extra_field"]:
			try:
				if self._fileobj.seekable():
					self.stream.seek(0)
			except AttributeError:
				pass
			raise IOError("Not an idzip file: %r" % self.name)

		dictzip_field = _parse_dictzip_field(header["extra_field"]["RA"])
		num_member_chunks = len(dictzip_field["zlengths"])

		start_chunk_index = len(self._chunks)
		for zlen in dictzip_field["zlengths"]:
			self._chunks.append((offset, zlen))
			offset += zlen
		self._last_zstream_end = offset

		chlen = dictzip_field["chlen"]
		sure_size = chlen * (num_member_chunks - 1)
		self._add_member(chlen, start_chunk_index, sure_size)

	def _add_member(self, chlen, start_chunk_index, sure_size):
		if len(self._members) > 0:
			prev_member = self._members[-1]
			start_pos = prev_member.start_pos + prev_member.isize
		else:
			start_pos = 0
		self._members.append(_Member(chlen, start_pos, start_chunk_index,
			sure_size))

	def read(self, size=-1):
		"""Reads the given number of bytes.
		It returns less bytes if EOF was reached.

		A negative size means unlimited reading.
		"""
		chunk_index, prefix_size = self._index_pos(self._pos)
		prefixed_buffer = []
		try:
			if size < 0:
				while True:
					prefixed_buffer.append(self._readchunk(chunk_index))
					chunk_index += 1
			else:
				need = prefix_size + size
				while need > 0:
					chunk_data = self._readchunk(chunk_index)
					prefixed_buffer.append(chunk_data[:need])
					need -= len(chunk_data)
					chunk_index += 1

		except EOFError:
			# The read data will be returned.
			pass
		prefixed_buffer = b"".join(prefixed_buffer)
		result = prefixed_buffer[prefix_size:]
		self._pos += len(result)
		return result

	def readline(self, size=-1):
		chunk_index, prefix_size = self._index_pos(self._pos)
		line = b""
		while True:
			try:
				data = self._readchunk(chunk_index)
			except EOFError:
				break

			chunk_index += 1
			eol_pos = data.find(b"\n", prefix_size)
			if eol_pos != -1:
				line += data[prefix_size:eol_pos+1]
				break

			line += data[prefix_size:]
			prefix_size = 0
			if size >= 0 and len(line) >= size:
				break

		if size >= 0:
			line = line[:size]
		self._pos += len(line)
		return line

	def flush(self):
		"""No-op, but needed by IdzipFile.flush(), which is called
		if wrapped in TextIOWrapper."""
		pass

	def close(self):
		if self._should_close:
			self._fileobj.close()
		self._cache = None

	def _index_pos(self, pos):
		"""Returns (chunk_index, remainder) index
		for the given position in uncompressed data.
		"""
		member = self._select_member(pos)

		pos_in_member = (pos - member.start_pos)
		member_chunk_index = pos_in_member // member.chlen
		chunk_index = member.start_chunk_index + member_chunk_index
		remainder = pos_in_member % member.chlen
		return (chunk_index, remainder)

	def _select_member(self, pos):
		"""Returns a member that covers the given pos.

		If the pos is after the EOF, the last member is returned.
		The EOF will be hit when reading from it.
		"""
		try:
			for i in itertools.count():
				if i >= len(self._members):
					return self._members[-1]

				member = self._members[i]
				if pos < member.start_pos + member.sure_size:
					return member

				if member.isize is None:
					self._parse_next_member()
				if pos < member.start_pos + member.isize:
					return member

		except EOFError:
			return self._members[-1]

	def _readchunk(self, chunk_index):
		"""Reads the specified chunk or throws EOFError.
		"""
		chunk = self._cache.get(chunk_index)
		if chunk is not None:
			return chunk

		chunk = self._uncached_readchunk(chunk_index)
		self._cache.put(chunk_index, chunk)
		return chunk

	def _uncached_readchunk(self, chunk_index):
		while chunk_index >= len(self._chunks):
			self._parse_next_member()

		offset, zlen = self._chunks[chunk_index]
		self._fileobj.seek(offset)
		compressed = _read_exactly(self._fileobj, zlen)
		deobj = zlib.decompressobj(-zlib.MAX_WBITS)
		return deobj.decompress(compressed)

	def _parse_next_member(self):
		self._reach_member_end()
		self._read_member_header()

	def _reach_member_end(self):
		"""Seeks the _fileobj at the end of the last known member.
		"""
		self._fileobj.seek(self._last_zstream_end)

		# The zlib stream could end with an empty block.
		deobj = zlib.decompressobj(-zlib.MAX_WBITS)
		extra = b""
		while deobj.unused_data == b"" and not extra:
			extra += deobj.decompress(self._fileobj.read(3))

		extra += deobj.flush()
		if extra != b"":
			raise IOError("Found extra compressed data after chunks.")

		self._fileobj.seek(GZIP_CRC32_LEN - len(deobj.unused_data),
				os.SEEK_CUR)
		isize = _read32(self._fileobj)
		self._members[-1].set_input_size(isize)

	def tell(self):
		return self._pos

	def seek(self, offset, whence=os.SEEK_SET):
		if whence == os.SEEK_SET:
			new_pos = offset
		elif whence == os.SEEK_CUR:
			new_pos = self._pos + offset
		elif whence == os.SEEK_END:
			raise ValueError("Seek from the end not supported")
		else:
			raise ValueError("Unknown whence: %r" % whence)

		if new_pos < 0:
			raise ValueError("Invalid pos: %r" % new_pos)
		self._pos = new_pos

	def __repr__(self):
		return "<idzip %s file %r at %s>" % (
			"open" if not self.closed else "closed",
			self.name,
			hex(id(self)))


class _Member(object):
	def __init__(self, chlen, start_pos, start_chunk_index, sure_size):
		self.chlen = chlen
		self.start_pos = start_pos
		self.start_chunk_index = start_chunk_index
		self.sure_size = sure_size
		self.isize = None

	def set_input_size(self, isize):
		assert isize >= self.sure_size
		self.isize = isize


def _read_gzip_header(input):
	"""Returns a parsed gzip header.
	The position of the input is advanced beyond the header.
	EOFError is thrown if there is not enough of data for the header.
	"""
	header = {
			"extra_field": {}
			}

	magic, flags, mtime = struct.unpack("<3sBIxx", _read_exactly(input, 10))
	if magic != compressor.GZIP_DEFLATE_ID:
		raise IOError("Not a gzip-deflate file.")

	if compressor.FRESERVED & flags:
		raise IOError("Unknown reserved flags: %s" % flags)

	if compressor.FEXTRA & flags:
		xlen = _read16(input)
		extra_field = input.read(xlen)
		header["extra_field"] = _split_subfields(extra_field)

	if compressor.FNAME & flags:
		_skip_cstring(input)

	if compressor.FCOMMENT & flags:
		_skip_cstring(input)

	if compressor.FHCRC & flags:
		# Skips header CRC
		input.read(2)

	return header


def _read_exactly(input, size):
	data = input.read(size)
	if len(data) != size:
		raise EOFError("Reached EOF")
	return data


def _read16(input):
	"""Reads next two bytes as an unsigned integer.
	"""
	return struct.unpack("<H", _read_exactly(input, 2))[0]

def _read32(input):
	"""Reads next four bytes as an unsigned integer.
	"""
	return struct.unpack("<I", _read_exactly(input, 4))[0]

def _split_subfields(extra_field):
	"""Returns a dict with {sub_id: subfield_data} entries.
	The extra field contains a variable number of bytes
	for each subfields:
	+---+---+---+---+===============================+
	|SUB_ID |  LEN  | LEN bytes of subfield data ...|
	+---+---+---+---+===============================+
	"""
	input = BytesIO(extra_field)
	sub_fields = {}
	while True:
		sub_id = input.read(2)
		if not sub_id:
			return sub_fields

		data_len = _read16(input)
		sub_id = sub_id.decode("UTF-8")
		sub_fields[sub_id] = input.read(data_len)


def _skip_cstring(input):
	"""Reads and discards a zero-terminated string.
	"""
	while True:
		c = input.read(1)
		if not c or c == b"\0":
			return


def _parse_dictzip_field(subfield):
	"""Returns a dict with:
		chlen ... length of each uncompressed chunk,
		zlengths ... lengths of compressed chunks.

	The dictzip subfield consists of:
	+---+---+---+---+---+---+==============================================+
	| VER=1 | CHLEN | CHCNT | CHCNT 2-byte lengths of compressed chunks ...|
	+---+---+---+---+---+---+==============================================+
	"""
	input = BytesIO(subfield)
	ver, chlen, chunk_count = struct.unpack("<HHH", input.read(6))
	if ver != 1:
		raise IOError("Unsupported dictzip version: %s" % ver)

	zlengths = []
	for i in range(chunk_count):
		zlengths.append(_read16(input))

	return dict(chlen=chlen, zlengths=zlengths)


IdzipFile = IdzipReader

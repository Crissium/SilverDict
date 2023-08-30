"""
This compressor produces a seekable compression format.
It is possible to decompress any part of the output.
The decompression does not need to start from the file beginning.

The format is gzip compatible. Gunzip can uncompress it.
Extra info is stored in the gzip header.

Project description:
http://code.google.com/p/idzip/
"""

import sys
import zlib
import struct
import time

from io import BytesIO, UnsupportedOperation
from os import path, SEEK_END, SEEK_SET

from ._stream import IOStreamWrapperMixin, check_file_like_for_writing

try:
	basestring
except NameError:
	basestring = (bytes, str)


fsencoding = 'UTF-8'
try:
	fsencoding = sys.getfilesystemencoding()
except AttributeError:
	pass

# The chunk length used by dictzip.
CHUNK_LENGTH = 58315

# The max number of chunks is given by the max length of the gzip extra field.
# A new gzip member with a new header is started if hitting that limit.
MAX_NUM_CHUNKS = (0xffff - 10) // 2
MAX_MEMBER_SIZE = MAX_NUM_CHUNKS * CHUNK_LENGTH

WRITE_BLOCK_SIZE = MAX_MEMBER_SIZE // (2 ** 5)

# Slow compression is OK.
COMPRESSION_LEVEL = zlib.Z_BEST_COMPRESSION

# Gzip header flags from RFC 1952.
GZIP_DEFLATE_ID = b"\x1f\x8b\x08"
FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT = 1, 2, 4, 8, 16
FRESERVED = 0xff - (FTEXT | FHCRC | FEXTRA | FNAME | FCOMMENT)
OS_CODE_UNIX = 3


def compress(input, in_size, output, basename=None, mtime=None):
	"""Produces a valid gzip output for the given input.
	A gzip file consists of one or many members.
	Each member would be a valid gzip file.
	"""
	if mtime is None:
		mtime = time.time()
	while True:
		member_size = min(in_size, MAX_MEMBER_SIZE)
		if basename is not None:
			basename = basename.encode(fsencoding)
		_compress_member(input, member_size, output, basename, mtime)
		# Only the first member will carry the basename and mtime.
		basename = None
		mtime = 0

		in_size -= member_size
		if in_size == 0:
			return


def compress_member(input, in_size, output, basename, mtime):
	""" Make the 'private' function public for the writer class
	"""
	return _compress_member(input, in_size, output, basename, mtime)


def _compress_member(input, in_size, output, basename, mtime):
	"""A gzip member contains:
	1) The header.
	2) The compressed data.
	"""
	zlengths_pos = _prepare_header(output, in_size, basename, mtime)
	zlengths = _compress_data(input, in_size, output)

	# Writes the lengths of compressed chunks to the header.
	end_pos = output.tell()
	output.seek(zlengths_pos)
	for zlen in zlengths:
		_write16(output, zlen)

	output.seek(end_pos)


def _compress_data(input, in_size, output):
	"""Compresses the given number of input bytes to the output.
	The output consists of:
	1) The compressed data.
	2) 4 bytes of CRC.
	3) 4 bytes of file size.
	"""
	assert in_size <= 0xffffffff
	zlengths = []
	crcval = zlib.crc32(b"")
	compobj = zlib.compressobj(COMPRESSION_LEVEL, zlib.DEFLATED,
							   -zlib.MAX_WBITS)

	need = in_size
	while need > 0:
		read_size = min(need, CHUNK_LENGTH)
		chunk = input.read(read_size)
		if len(chunk) != read_size:
			raise IOError("Need %s bytes, got %s" % (read_size, len(chunk)))

		need -= len(chunk)
		crcval = zlib.crc32(chunk, crcval)
		zlen = _compress_chunk(compobj, chunk, output)
		zlengths.append(zlen)

	# An empty block with BFINAL=1 flag ends the zlib data stream.
	output.write(compobj.flush(zlib.Z_FINISH))
	_write32(output, crcval)
	_write32(output, in_size)
	return zlengths


def _compress_chunk(compobj, chunk, output):
	data = compobj.compress(chunk)
	zlen = len(data)
	output.write(data)

	data = compobj.flush(zlib.Z_FULL_FLUSH)
	zlen += len(data)
	output.write(data)
	return zlen


def _prepare_header(output, in_size, basename, mtime):
	"""Writes a prepared gzip header to the output.
	The gzip header is defined in RFC 1952.

	The gzip header starts with:
	+---+---+---+---+---+---+---+---+---+---+
	|x1f|x8b|x08|FLG|     MTIME     |XFL|OS |
	+---+---+---+---+---+---+---+---+---+---+
	where:
	FLG ... flags. FEXTRA|FNAME is used by idzip.
	MTIME ... the modification time of the original file or 0.
	XFL ... extra flags about the compression.
	OS ... operating system used for the compression.

	The next header sections are:
	1) Extra field, if the FEXTRA flag is set.
	   Its format is described in _write_extra_field().
	2) The original file name, if the FNAME flag is set.
	   The file name string is zero-terminated.
	"""
	output.write(GZIP_DEFLATE_ID)
	flags = FEXTRA
	if basename:
		flags |= FNAME
	output.write(bytearray([flags]))

	# The mtime will be undefined if it does not fit.
	if mtime > 0xffffffff:
		mtime = 0
	_write32(output, mtime)

	deflate_flags = b"\0"
	if COMPRESSION_LEVEL == zlib.Z_BEST_COMPRESSION:
		deflate_flags = b"\x02"  # slowest compression algorithm
	output.write(deflate_flags)
	output.write(bytearray([OS_CODE_UNIX]))

	zlengths_pos = _write_extra_field(output, in_size)
	if basename:
		output.write(basename + b'\0')  # original basename

	return zlengths_pos


def _write_extra_field(output, in_size):
	"""Writes the dictzip extra field.
	It will be initiated with zeros on the place of
	the lengths of compressed chunks.

	The gzip extra field is present when the FEXTRA flag is set.
	RFC 1952 defines the used bytes:
	+---+---+================================+
	| XLEN  | XLEN bytes of "extra field" ...|
	+---+---+================================+

	Idzip adds only one subfield:
	+---+---+---+---+===============================+
	|'R'|'A'|  LEN  | LEN bytes of subfield data ...|
	+---+---+---+---+===============================+

	The subfield ID "RA" stands for Random Access.
	That subfield ID signalizes the dictzip gzip extension.
	The dictzip stores the length of uncompressed chunks
	and the lengths of compressed chunks to the gzip header:
	+---+---+---+---+---+---+==============================================+
	| VER=1 | CHLEN | CHCNT | CHCNT 2-byte lengths of compressed chunks ...|
	+---+---+---+---+---+---+==============================================+

	Two bytes are used to store a length of a compressed chunk.
	So the length of a compressed chunk has to be max 0xfffff.
	That puts a restriction on the CHLEN -- the length of
	uncompressed chunks. Dictzip uses CHLEN=58315.

	Only a fixed number of chunk lengths will fit to the gzip header.
	That limits the max file size of a dictzip file.
	Idzip does not have that limitation. It starts a new gzip member if needed.
	The new member would be also a valid dictzip file.
	"""
	num_chunks = in_size // CHUNK_LENGTH
	if in_size % CHUNK_LENGTH != 0:
		num_chunks += 1

	field_length = 3 * 2 + 2 * num_chunks
	extra_length = 2 * 2 + field_length
	assert extra_length <= 0xffff
	_write16(output, extra_length)  # XLEN

	# Dictzip extra field (Random Access)
	output.write(b"RA")
	_write16(output, field_length)
	_write16(output, 1)  # version
	_write16(output, CHUNK_LENGTH)
	_write16(output, num_chunks)
	zlengths_pos = output.tell()
	output.write(b"\0\0" * num_chunks)
	return zlengths_pos


def _write16(output, value):
	"""Writes only the lowest 2 bytes from the given number.
	"""
	output.write(struct.pack("<H", value & 0xffff))


def _write32(output, value):
	"""Writes only the lowest 4 bytes from the given number.
	"""
	output.write(struct.pack("<I", value & 0xffffffff))


class IdzipWriter(IOStreamWrapperMixin):
	FILE_EXTENSION = 'dz'
	enforce_extension = True

	def __init__(self, output, sync_size=MAX_MEMBER_SIZE, mtime=None):
		if mtime is None:
			mtime = time.time()
		if isinstance(output, basestring):
			self.output = self._prepare_file_stream(output)
			self._should_close = True
		else:
			# hopefully a file like object
			if not check_file_like_for_writing(output):
				raise TypeError(
					"`output` must be a file-like object supporting "
					"write, tell, flush, and close!")
			self.output = output
			self._should_close = False
		self.input_buffer = BytesIO()
		try:
			name = path.abspath(self.output.name)
			basename = path.basename(name)
			self.name = name
			self.basename = basename.encode(fsencoding)
		except AttributeError:
			self.name = ""
			self.basename = self.name.encode(fsencoding)
		self.uncompressed_position = 0
		self.sync_size = sync_size
		self.mtime = int(mtime)
		self.compressobj = None
		self._reset_compressor()
		self.version = 1

	def _prepare_file_stream(self, path):
		if self.enforce_extension and not path.endswith(self.FILE_EXTENSION):
			path = "%s.%s" % (path, self.FILE_EXTENSION)
		return open(path, 'wb')

	@property
	def stream(self):
		return self.output

	def _make_compressor(self):
		return zlib.compressobj(
			COMPRESSION_LEVEL, zlib.DEFLATED,
			-zlib.MAX_WBITS)

	def _reset_compressor(self):
		self.compressobj = self._make_compressor()

	def seek(self, offset, whence=SEEK_SET):
		raise UnsupportedOperation("Cannot seek on a write-only stream")

	def reset_buffer(self):
		# For truncate() to actually help us circumvent memory problems,
		# we need to seek to the beginning of the buffer, otherwise the
		# next call to write() will just pad the buffer with null bytes
		# up to the current position returned by tell()
		self.input_buffer.seek(0)
		self.input_buffer.truncate(0)

	def _get_buffer_size(self):
		curpos = self.input_buffer.tell()
		self.input_buffer.seek(0, SEEK_END)
		buffer_len = self.input_buffer.tell()
		self.input_buffer.seek(curpos)
		return buffer_len

	def _write_chunked(self, b, chunk_size=WRITE_BLOCK_SIZE):
		offset = 0
		total = len(b)
		i = 0
		while offset < total:
			s = b[offset:offset + chunk_size]
			self.input_buffer.write(s)
			self.uncompressed_position += len(s)
			i += 1
			offset += chunk_size
			if i % 2 == 0:
				self.sync()
				self.reset_buffer()
		return total

	def write(self, b):
		try:
			self.input_buffer.write(b)
		except MemoryError:
			# Attempting to write to the input buffer may cause
			# it to optimistically request a contiguous allocation
			# larger than the memory allocator can currently supply,
			# raising a MemoryError. This can be recovered from by
			# syncing the current buffer to disk, resetting the
			# input buffer, and trying to write again
			self.sync()
			self.reset_buffer()
			try:
				self.input_buffer.write(b)
			except MemoryError:
				# If the data to be written are so large that
				# they cannot be written to the input buffer in
				# one shot, try writing it in chunks. If *this*
				# runs out of memory, we're out of options.
				return self._write_chunked(b)
		self.uncompressed_position += len(b)
		buffer_len = self._get_buffer_size()
		if buffer_len >= self.sync_size:
			if self._check_member_size_valid(buffer_len):
				self.sync()
				self.reset_buffer()
			else:
				self._sync_chunked()
		return len(b)

	def sync(self):
		self.compress_member()
		self.reset_buffer()
		return self.output.tell()

	def _sync_chunked(self, flush=False):
		# accumulate chunks of the input buffer which are at most
		# `MAX_MEMBER_SIZE` bytes long
		valid_members = []
		self.input_buffer.seek(0)
		chunk = self.input_buffer.read(MAX_MEMBER_SIZE - 1)
		while chunk:
			valid_members.append(BytesIO(chunk))
			chunk = self.input_buffer.read(MAX_MEMBER_SIZE - 1)
		# if the input buffer was empty, then no valid members were
		# made so return immediately
		if not valid_members:
			return
		# if there is only one member, chunked syncing should be the same
		# as normal syncing, leaving the input buffer empty
		elif len(valid_members) == 1:
			self.input_buffer = valid_members[0]
			self.compress_member()
			self.reset_buffer()
		else:
			# otherwise, for all but the last valid member, sync those buffers
			# to the output stream, and then set the last valid member as the current
			# input buffer to avoid having a tiny leftover fragment.
			for chunk in valid_members[:-1]:
				self.input_buffer = chunk
				self.compress_member()
				self.reset_buffer()
			self.input_buffer = valid_members[-1]
			self.input_buffer.seek(0, SEEK_END)
			if flush:
				self.compress_member()
				self.reset_buffer()

	def tell(self):
		return self.uncompressed_position

	def flush(self):
		self.sync()
		return self.output.flush()

	def close(self):
		if not self.closed:
			self.sync()
			self.reset_buffer()
			if self._should_close:
				closing = self.output.close()
				return closing
		return None

	def _calculate_number_of_chunks_for_bytes(self, in_size):
		num_chunks = in_size // CHUNK_LENGTH
		if in_size % CHUNK_LENGTH != 0:
			num_chunks += 1
		return num_chunks

	def _calculate_extra_field_length(self, in_size):
		num_chunks = self._calculate_number_of_chunks_for_bytes(in_size)
		field_length = 3 * 2 + 2 * num_chunks
		return field_length

	def _calculate_header_extra_size(self, in_size):
		field_length = self._calculate_extra_field_length(in_size)
		extra_length = 2 * 2 + field_length
		return extra_length

	def _check_member_size_valid(self, in_size):
		extra_length = self._calculate_header_extra_size(in_size)
		return extra_length <= 0xffff

	def compress_member(self):
		"""A gzip member contains:
		1) The header.
		2) The compressed data.
		"""
		self.input_buffer.seek(0, SEEK_END)
		member_size = self.input_buffer.tell()
		self.input_buffer.seek(0)

		zlengths_pos = self._prepare_header(member_size)
		zlengths = self._compress_data(member_size)

		# Writes the lengths of compressed chunks to the header.
		end_pos = self.output.tell()
		self.output.seek(zlengths_pos)
		for zlen in zlengths:
			_write16(self.output, zlen)

		self.output.seek(end_pos)

	def _prepare_header(self, in_size):
		"""Writes a prepared gzip header to the output.
		The gzip header is defined in RFC 1952.

		The gzip header starts with:
		+---+---+---+---+---+---+---+---+---+---+
		|x1f|x8b|x08|FLG|     MTIME     |XFL|OS |
		+---+---+---+---+---+---+---+---+---+---+
		where:
		FLG ... flags. FEXTRA|FNAME is used by idzip.
		MTIME ... the modification time of the original file or 0.
		XFL ... extra flags about the compression.
		OS ... operating system used for the compression.

		The next header sections are:
		1) Extra field, if the FEXTRA flag is set.
		   Its format is described in _write_extra_field().
		2) The original file name, if the FNAME flag is set.
		   The file name string is zero-terminated.
		"""
		self.output.write(GZIP_DEFLATE_ID)
		flags = FEXTRA
		if self.basename:
			flags |= FNAME
		self.output.write(bytearray([flags]))

		# The mtime will be undefined if it does not fit.
		if self.mtime > 0xffffffff:
			mtime = 0
		else:
			mtime = self.mtime
		_write32(self.output, mtime)

		deflate_flags = b"\0"
		if COMPRESSION_LEVEL == zlib.Z_BEST_COMPRESSION:
			deflate_flags = b"\x02"  # slowest compression algorithm
		self.output.write(deflate_flags)
		self.output.write(bytearray([OS_CODE_UNIX]))

		zlengths_pos = self._write_extra_field(in_size)
		if self.basename:
			self.output.write(self.basename + b'\0')  # original basename

		return zlengths_pos

	def _write_extra_field(self, in_size):
		"""Writes the dictzip extra field.
		It will be initiated with zeros on the place of
		the lengths of compressed chunks.

		The gzip extra field is present when the FEXTRA flag is set.
		RFC 1952 defines the used bytes:
		+---+---+================================+
		| XLEN  | XLEN bytes of "extra field" ...|
		+---+---+================================+

		Idzip adds only one subfield:
		+---+---+---+---+===============================+
		|'R'|'A'|  LEN  | LEN bytes of subfield data ...|
		+---+---+---+---+===============================+

		The subfield ID "RA" stands for Random Access.
		That subfield ID signalizes the dictzip gzip extension.
		The dictzip stores the length of uncompressed chunks
		and the lengths of compressed chunks to the gzip header:
		+---+---+---+---+---+---+==============================================+
		| VER=1 | CHLEN | CHCNT | CHCNT 2-byte lengths of compressed chunks ...|
		+---+---+---+---+---+---+==============================================+

		Two bytes are used to store a length of a compressed chunk.
		So the length of a compressed chunk has to be max 0xfffff.
		That puts a restriction on the CHLEN -- the length of
		uncompressed chunks. Dictzip uses CHLEN=58315.

		Only a fixed number of chunk lengths will fit to the gzip header.
		That limits the max file size of a dictzip file.
		Idzip does not have that limitation. It starts a new gzip member if needed.
		The new member would be also a valid dictzip file.
		"""
		# num_chunks = in_size // CHUNK_LENGTH
		# if in_size % CHUNK_LENGTH != 0:
		#     num_chunks += 1
		num_chunks = self._calculate_number_of_chunks_for_bytes(in_size)
		# field_length = 3 * 2 + 2 * num_chunks
		field_length = self._calculate_extra_field_length(in_size)
		# extra_length = 2 * 2 + field_length
		extra_length = self._calculate_header_extra_size(in_size)
		assert extra_length <= 0xffff
		_write16(self.output, extra_length)  # XLEN

		# Dictzip extra field (Random Access)
		self.output.write(b"RA")
		_write16(self.output, field_length)
		_write16(self.output, self.version)  # version
		_write16(self.output, CHUNK_LENGTH)
		_write16(self.output, num_chunks)
		zlengths_pos = self.output.tell()
		self.output.write(b"\0\0" * num_chunks)
		return zlengths_pos

	def _compress_data(self, in_size):
		"""Compresses the given number of input bytes to the output.
		The output consists of:
		1) The compressed data.
		2) 4 bytes of CRC.
		3) 4 bytes of file size.
		"""
		assert in_size <= 0xffffffff
		zlengths = []
		crcval = zlib.crc32(b"")

		need = in_size
		while need > 0:
			read_size = min(need, CHUNK_LENGTH)
			chunk = self.input_buffer.read(read_size)
			if len(chunk) != read_size:
				raise IOError("Need %s bytes, got %s" % (read_size, len(chunk)))

			need -= len(chunk)
			crcval = zlib.crc32(chunk, crcval)
			zlen = self._compress_chunk(chunk)
			zlengths.append(zlen)

		# An empty block with BFINAL=1 flag ends the zlib data stream.
		self.output.write(self.compressobj.flush(zlib.Z_FINISH))
		self._reset_compressor()
		_write32(self.output, crcval)
		_write32(self.output, in_size)
		return zlengths

	def _compress_chunk(self, chunk):
		data = self.compressobj.compress(chunk)
		zlen = len(data)
		self.output.write(data)

		data = self.compressobj.flush(zlib.Z_FULL_FLUSH)
		zlen += len(data)
		self.output.write(data)
		return zlen

#!/usr/bin/env python
"""Usage: %prog [OPTION]... FILE...
Compresses the given files.
"""

import os
import sys
import optparse
import logging

parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, parent_dir)
import idzip
from idzip import compressor

DEFAULT_SUFFIX = ".dz"

def _parse_args():
	parser = optparse.OptionParser(__doc__)
	parser.add_option("-d", "--decompress", action="store_true",
			help="decompress the file")
	parser.add_option("-S", "--suffix",
			help="change the default suffix (default=%s)" % DEFAULT_SUFFIX)
	parser.add_option("-k", "--keep", action="store_true",
			help="don't unlink the processed files")
	parser.add_option("-v", "--verbose", action="count",
			help="increase verbosity")
	parser.set_defaults(verbose=0, suffix=DEFAULT_SUFFIX, keep=False)

	options, args = parser.parse_args()
	if not options.suffix or "/" in options.suffix:
		parser.error("Incorrect suffix: %r" % options.suffix)

	if len(args) == 0:
		parser.error("An input file is required.")

	return options, args


def _compress(filename, options):
	input = open(filename, "rb")
	inputinfo = os.fstat(input.fileno())
	basename = os.path.basename(filename)

	target = filename + options.suffix
	logging.info("compressing %r to %r", filename, target)
	output = open(target, "wb")
	compressor.compress(input, inputinfo.st_size, output,
			basename, int(inputinfo.st_mtime))

	_finish_output(output, options)
	input.close()
	return True


def _decompress(filename, options):
	"""Decompresses the whole file.
	It is useful mainly for testing. Normal gunzip is enough
	when uncompressing a file from the beginning.
	"""
	suffix = options.suffix
	if not filename.endswith(suffix) or len(filename) == len(suffix):
		logging.warn("without %r suffix -- ignored: %r",
				suffix, filename)
		return False

	target = filename[:-len(suffix)]
	input = idzip.open(filename)
	logging.info("uncompressing %r to %r", filename, target)
	output = open(target, "wb")
	while True:
		data = input.read(1024)
		if not data:
			break

		output.write(data)

	_finish_output(output, options)
	input.close()
	return True


def _finish_output(output, options):
	if not options.keep:
		# We want to preserve at least one copy of the data.
		output.flush()
		os.fsync(output.fileno())
	output.close()


def main():
	options, args = _parse_args()
	logging.basicConfig(level=logging.WARNING - 10*options.verbose)

	action = _compress
	if options.decompress:
		action = _decompress

	for filename in args:
		ok = action(filename, options)
		if ok and not options.keep:
			os.unlink(filename)


if __name__ == "__main__":
	main()


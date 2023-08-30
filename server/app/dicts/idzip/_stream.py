

class IOStreamWrapperMixin(object):

	@property
	def closed(self):
		return self.stream.closed

	def seekable(self):
		return self.stream.seekable()

	def readable(self):
		return self.stream.readable()

	def writable(self):
		return self.stream.writable()

	def fileno(self):
		return self.stream.fileno()

	def __del__(self):
		if not self.closed:
			self.close()


def check_file_like_for_writing(f):
	check = (
		hasattr(f, "write") and hasattr(f, "tell") and
		hasattr(f, 'flush') and hasattr(f, 'close'))
	return check

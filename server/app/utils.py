import functools
import logging
import re
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Iterable


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


_ISOLATED_MARKER = '/* Isolated */\n'
_re_css_comments = re.compile(r'\/\*(?:.(?!\*\/))*.?\*\/', re.DOTALL)
_re_css_selectors = re.compile(r'[ \*\>\+\,;:\[\{\]]')
_re_css_separators = re.compile(r'[,;{]')


def isolate_css(full_filename: str, id: str) -> None:
	"""
	Isolate different dictionaries' styles by prepending the article block's ID to each selector.
	"""
	with open(full_filename) as f:
		css = f.read()
	
	if css.startswith(_ISOLATED_MARKER):
		return
	
	css = _re_css_comments.sub('', css)

	current_pos = 0
	buf = []

	while current_pos < len(css):
		ch = css[current_pos]

		if ch == '@':
			n = current_pos
			if css[current_pos:current_pos+7].lower() == '@import' or \
				css[current_pos:current_pos+10].lower() == '@font-face' or \
				css[current_pos:current_pos+10].lower() == '@namespace' or \
				css[current_pos:current_pos+8].lower() == '@charset':
				# Copy rule as is.
				n = css.find(';', current_pos)
				n2 = css.find('{', current_pos)
				if n2 > 0 and n > n2:
					n = n2 - 1
			elif css[current_pos:current_pos+6].lower() == '@media':
				# Copy up to '{' and continue parsing inside.
				n = css.find('{', current_pos)
			elif css[current_pos:current_pos+5].lower() == '@page':
				# Discard
				n = css.find('}', current_pos)
				if n < 0:
					break
				current_pos = n + 1
				continue
			else:
				# Copy rule as is.
				n = css.find('}', current_pos)

			if n < 0:
				break
			
			buf.append(css[current_pos:n+1])
			current_pos = n + 1
		elif ch == '{':
			n = css.find('}', current_pos)
			if n < 0:
				break

			buf.append(css[current_pos:n+1])
			current_pos = n + 1
		elif ch.isalpha() or ch in ('.', '#', '*', '\\', ':'):
			if ch.isalpha() or ch == '*':
				# Check for namespace prefix
				for i in range(current_pos, len(css)):
					ch1 = css[i]
					if not ch1.isalnum() and \
						not ch1 == '_' and \
						not ch1 == '-' and \
						not (ch1 == '*' and i == current_pos):
						if ch1 == '|':
							buf.append(css[current_pos:i+1])
							current_pos = i + 1
					break
				if ch1 == '|':
					continue

			n = _re_css_selectors.search(css, current_pos + 1)
			if not n:
				buf.append(css[current_pos:])
				break
			else:
				n = n.start()
				selector = css[current_pos:n]
				trimmed = selector.strip().lower()
				if trimmed == 'html' or trimmed == 'body':
					buf.append(f'{selector} {id} ')
					current_pos += 4
				else:
					buf.append(f'{id} ')
				
			n = _re_css_separators.search(css, current_pos)
			if not n:
				buf.append(css[current_pos:])
				break
			else:
				buf.append(css[current_pos:n.start()])
				current_pos = n.start()
		else:
			buf.append(ch)
			current_pos += 1

	new_css = f'{_ISOLATED_MARKER}{"".join(buf)}'
	with open(full_filename, 'w') as f:
		f.write(new_css)


def run_in_thread_pool(
	func: Callable[..., Any],
	*iterables: Iterable[Any],
	num_max_workers: int | None = None
) -> list[Any]:
	@functools.wraps(func)
	def wrapper(arg: Any) -> Any:
		try:
			return func(arg)
		except Exception as e:
			logger.error(f'Error in thread pool: {e}\n{traceback.format_exc()}')
			raise
	
	with ThreadPoolExecutor(num_max_workers) as executor:
		return list(executor.map(wrapper, *iterables))

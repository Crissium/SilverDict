import re

re_number = re.compile(r'<b>\s*(\d+)(.*?)</b>')

def transform_michaelis(html: 'str') -> 'str':
	# Add <br> tags before each number, remove whitespace and keep the arbitrary string
	html = re_number.sub(r'<br><b>\1\2</b>', html)
	# Add <br> tags before part of speech information
	html = html.replace('<i> <i><font color="green">', '<br><i><font color="green">')
	return html

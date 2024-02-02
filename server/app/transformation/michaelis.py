import re

line_ending_pattern = re.compile(r'([\.!?])(\s|<)')
transcription_pattern = re.compile(r'\[([^\]]+)\](<i>)?\s')
first_sense_pattern = re.compile(r'</font></i>\s?</i><b>\s?1')


def transform_michaelis(html: str) -> str:
	# Note the order
	html = line_ending_pattern.sub(r'\1<br />\2', html)
	html = html.replace('• ', '')
	html = html.replace('•<i> ', '<i>')
	html = transcription_pattern.sub(r'[\1]<br />\2', html)
	html = first_sense_pattern.sub(r'</font></i><br /></i><b>1', html)

	return html.replace(' a)', '<br />a)')

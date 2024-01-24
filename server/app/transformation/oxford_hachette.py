def transform_oxford_hachette(html: 'str') -> 'str':
	return html.replace('; ', ';<br />').replace('darkslategray', 'grey').replace('color: darkmagenta', 'font-style: italic')

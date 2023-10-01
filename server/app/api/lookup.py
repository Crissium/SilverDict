from flask import current_app, make_response, request, render_template, send_from_directory, Response
import time
from .utils import make_yaml_response
from . import api
from .. import db_manager
from ..dictionaries import simplify

@api.route('/suggestions/<group_name>/<key>')
def suggestions(group_name: 'str', key: 'str') -> 'Response':
	timestamp_suggestions_requested = time.time()
	dicts = current_app.extensions['dictionaries']
	if not dicts.settings.group_exists(group_name):
		response = make_response('<p>Group %s not found</p>' % group_name, 404)
	else:
		suggestions = dicts.suggestions(group_name, key)
		response = make_yaml_response({
			'timestamp': timestamp_suggestions_requested,
			'suggestions': suggestions
		})
	return response

@api.route('/query/<group_name>/<key>')
def query(group_name: 'str', key: 'str') -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if not dicts.settings.group_exists(group_name):
		response = make_response('<p>Group %s not found</p>' % group_name, 404)
	else:
		articles = dicts.query(group_name, key)
		articles_html = render_template('articles.html', articles=articles)
		including_dictionaries = request.args.get('dicts', False)
		if len(articles) > 0:
			if including_dictionaries:
				response = make_yaml_response(
					{
						'found': True,
						'articles': articles_html,
						'dictionaries': [article[0] for article in articles]
					}
				)
			else: # used without the web interface
				response = make_response(articles_html)
		else:
			suggestions = dicts.get_spelling_suggestions(group_name, key)
			suggestions_html = render_template('suggestions.html', key=key, group_name=group_name, suggestions=suggestions)
			if including_dictionaries:
				response = make_yaml_response(
					{
						'found': False,
						'articles': suggestions_html,
						'dictionaries': dicts.settings.dictionaries_of_group(group_name)
					}
				)
			else:
				response = make_response(suggestions_html)
	return response

@api.route('/lookup/<dictionary_name>/<key>')
def lookup(dictionary_name: 'str', key: 'str') -> 'Response':
	"""
	Legacy API, preserved for compatibility.
	"""
	key_simplified = simplify(key)
	dicts = current_app.extensions['dictionaries']
	if not db_manager.dictionary_exists(dictionary_name):
		response = make_response('<p>Dictionary %s not found</p>' % dictionary_name, 404)
	elif not db_manager.entry_exists_in_dictionary(key_simplified, dictionary_name):
		response = make_response('<p>Entry %s not found in dictionary %s</p>' % (key_simplified, dictionary_name), 404)
	else:
		dicts.settings.add_word_to_history(key)
		response = make_response(dicts.lookup(dictionary_name, key_simplified))
	return response

@api.route('/cache/<path:path_name>')
def send_cached_resources(path_name: 'str') -> 'Response':
	response = send_from_directory(current_app.extensions['dictionaries'].settings.CACHE_ROOT, path_name)
	return response

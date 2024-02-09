from flask import current_app, jsonify, make_response, request, render_template, send_from_directory, Response
import time
from . import api
from .. import db_manager
from ..dictionaries import simplify


@api.route('/suggestions/<group_name>/<key>')
def suggestions(group_name: str, key: str) -> Response:
	timestamp_suggestions_requested = float(request.args.get('timestamp', time.time() * 1000))
	dicts = current_app.extensions['dictionaries']
	if not dicts.settings.group_exists(group_name):
		response = make_response('<p>Group %s not found</p>' % group_name, 404)
	else:
		suggestions = dicts.suggestions(group_name, key)
		response = jsonify({
			'timestamp': timestamp_suggestions_requested,
			'suggestions': suggestions
		})
	return response


@api.route('/query/<group_name>/<key>')
def query(group_name: str, key: str) -> Response:
	dicts = current_app.extensions['dictionaries']
	if not dicts.settings.group_exists(group_name):
		response = make_response(f'<p>Group {group_name} not found</p>', 404)
	else:
		articles = dicts.query(group_name, key)
		including_dictionaries = request.args.get('dicts', False)
		if len(articles) > 0:
			if including_dictionaries:
				articles_html = render_template('articles.html', articles=articles)
				response = jsonify(
					{
						'found': True,
						'articles': articles_html,
						'dictionaries': [article[0] for article in articles]
					}
				)
			else:  # used without the web interface
				articles_html = render_template('articles_standalone.html', key=key, articles=articles)
				response = make_response(articles_html)
		else:
			suggestions = dicts.suggestions(group_name, key)
			suggestions_html = render_template('suggestions.html',
									  			key=key,
												group_name=group_name,
												suggestions=suggestions)
			if including_dictionaries:
				response = jsonify(
					{
						'found': False,
						'articles': suggestions_html,
						'dictionaries': dicts.settings.dictionaries_of_group(group_name)
					}
				)
			else:
				response = make_response(suggestions_html)
	return response


@api.route('/anki/<group_name>/<word>')
def anki(group_name: str, word: str) -> Response:
	dicts = current_app.extensions['dictionaries']
	if not dicts.settings.group_exists(group_name):
		response = make_response('<p>Group %s not found.</p>' % group_name, 404)
	else:
		articles = dicts.query_anki(group_name, word)
		including_dictionaries = request.args.get('dicts', False)
		if len(articles) > 0:
			if including_dictionaries:
				articles_html = render_template('anki.html', articles=articles)
				response = jsonify(
					{
						'found': True,
						'articles': articles_html,
						'dictionaries': [article[0] for article in articles]
					}
				)
			else:
				articles_html = render_template('anki_standalone.html', word=word, articles=articles)
				response = make_response(articles_html)
		else:
			if including_dictionaries:
				response = jsonify(
					{
						'found': False,
						'articles': '<p>No results found.</p>',
						'dictionaries': dicts.settings.dictionaries_of_group(group_name)
					}
				)
			else:
				response = make_response('<p>No results found.</p>')

	return response


@api.route('/lookup/<dictionary_name>/<key>')
def lookup(dictionary_name: str, key: str) -> Response:
	"""
	Legacy API, preserved for compatibility.
	"""
	key_simplified = simplify(key)
	dicts = current_app.extensions['dictionaries']
	if not db_manager.dictionary_exists(dictionary_name):
		response = make_response('<p>Dictionary %s not found</p>' % dictionary_name, 404)
	elif not db_manager.entry_exists_in_dictionary(key_simplified, dictionary_name):
		response = make_response('<p>Entry %s not found in dictionary %s</p>' %
								 (key_simplified, dictionary_name), 404)
	else:
		response = make_response(dicts.lookup(dictionary_name, key_simplified))
	return response


@api.route('/fts/<query>')
def full_text_search(query: str) -> Response:
	dicts = current_app.extensions['dictionaries']
	if not dicts.settings.group_exists(dicts.settings.XAPIAN_GROUP_NAME):
		return make_response(f'<p>Group {dicts.settings.XAPIAN_GROUP_NAME} not found.</p>', 404)
	else:
		articles = dicts.full_text_search(query)
		including_dictionaries = request.args.get('dicts', False)
		if len(articles) > 0:
			if including_dictionaries:
				articles_html = render_template(
					'articles.html',
					articles=[
						(f'{a[0]}__{a[1]}',
						a[2],
						a[3]) for a in articles
					]
				)
				response = jsonify(
					{
						'found': True,
						'articles': articles_html,
						'dictionaries': [
							{
								'dict': a[0],
								'word': a[1]
							} for a in articles
						]
					}
				)
			else:  # used without the web interface
				articles_html = render_template('articles_standalone.html', articles=articles)
				response = make_response(articles_html)
		else:
			response_html = '<p>No result found.</p>'
			if including_dictionaries:
				response = jsonify(
					{
						'found': False,
						'articles': response_html,
						'dictionaries': []
					}
				)
			else:
				response = make_response(response_html)
	return response


@api.route('/cache/<path:path_name>')
def send_cached_resources(path_name: str) -> Response:
	response = send_from_directory(current_app.extensions['dictionaries'].settings.CACHE_ROOT, path_name)
	return response

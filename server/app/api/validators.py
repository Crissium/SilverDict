from flask import jsonify, current_app, request, Response
from . import api

@api.route('/validator/dictionary_info', methods=['POST'])
def dictionary_info_valid() -> 'Response':
	dictionary_info = request.json
	response = jsonify({
		'valid': current_app.extensions['dictionaries'].settings.dictionary_info_valid(dictionary_info)
	})
	return response

@api.route('/validator/source', methods=['POST'])
def source_valid() -> 'Response':
	source = request.json['source']
	response = jsonify({
		'valid': current_app.extensions['dictionaries'].settings.source_valid(source)
	})
	return response

@api.route('/validator/test_connection')
def test_connection() -> 'Response':
	response = jsonify({
		'success': True
	})
	return response
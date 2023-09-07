from flask import current_app, request, Response
from .utils import make_yaml_response, parse_yaml
from . import api

@api.route('/validator/dictionary_info', methods=['POST'])
def dictionary_info_valid() -> 'Response':
	dictionary_info = parse_yaml(request.get_data())
	response = make_yaml_response({
		'valid': current_app.extensions['dictionaries'].settings.dictionary_info_valid(dictionary_info)
	})
	return response

@api.route('/validator/source', methods=['POST'])
def source_valid() -> 'Response':
	source = parse_yaml(request.get_data())['source']
	response = make_yaml_response({
		'valid': current_app.extensions['dictionaries'].settings.source_valid(source)
	})
	return response

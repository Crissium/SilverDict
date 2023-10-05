from flask import jsonify, current_app, request, Response
from . import api
from .. import db_manager
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@api.route('/management/formats')
def get_formats() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	response = jsonify(list(dicts.settings.SUPPORTED_DICTIONARY_FORMATS.keys()))
	return response

@api.route('/management/dictionaries', methods=['GET', 'POST', 'DELETE', 'PUT'])
def dictionaries() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = jsonify(dicts.settings.dictionaries_list)
	elif request.method == 'POST':
		dictionary_info = request.json
		group_name = dictionary_info.pop('group_name')
		dicts.add_dictionary(dictionary_info)
		dicts.settings.add_dictionary_to_group(dictionary_info['dictionary_name'], group_name)
		response = jsonify({
			'dictionaries': dicts.settings.dictionaries_list,
			'groupings': dicts.settings.get_dictionary_groupings()
		})
	elif request.method == 'DELETE':
		dictionary_name = request.json['name']
		dictionary_info = dicts.settings.info_of_dictionary(dictionary_name)
		dicts.remove_dictionary(dictionary_info)
		response = jsonify({
			'dictionaries': dicts.settings.dictionaries_list,
			'groupings': dicts.settings.get_dictionary_groupings()
		})
	elif request.method == 'PUT': # Should only be used to reorder dictionaries
		dictionaries_info = request.json
		dicts.settings.reorder_dictionaries(dictionaries_info)
		response = jsonify(dicts.settings.dictionaries_list)
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/dictionary_name', methods=['PUT'])
def change_dictionary_name() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	info = request.json
	dicts.settings.change_dictionary_display_name(info['name'], info['display'])
	response = jsonify({'success': True})
	return response

@api.route('/management/sources', methods=['GET', 'POST', 'DELETE'])
def sources() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = jsonify(dicts.settings.misc_configs['sources'])
	elif request.method == 'POST':
		source = request.json['source']
		dicts.settings.add_source(source)
		response = jsonify(dicts.settings.misc_configs['sources'])
	elif request.method == 'DELETE':
		source = request.json['source']
		dicts.settings.remove_source(source)
		response = jsonify(dicts.settings.misc_configs['sources'])
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/scan')
def scan_sources() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	for dictionary_info in dicts.settings.scan_sources():
		dicts.add_dictionary(dictionary_info)
	response = jsonify({
		'dictionaries': dicts.settings.dictionaries_list,
		'groupings': dicts.settings.get_dictionary_groupings()
	})
	return response

@api.route('/management/groups', methods=['GET', 'POST', 'DELETE', 'PUT'])
def groups() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = jsonify(dicts.settings.get_groups())
	elif request.method == 'POST':
		group = request.json
		dicts.settings.add_group(group)
		response = jsonify({
			'groups': dicts.settings.get_groups(),
			'groupings': dicts.settings.get_dictionary_groupings()
		})
	elif request.method == 'DELETE':
		group_name = request.json['name']
		dicts.settings.remove_group_by_name(group_name)
		response = jsonify({
			'groups': dicts.settings.get_groups(),
			'groupings': dicts.settings.get_dictionary_groupings()
		})
	elif request.method == 'PUT': # Should only be used to reorder groups
		groups = request.json
		dicts.settings.reorder_groups(groups)
		response = jsonify(dicts.settings.get_groups())
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/group_lang', methods=['PUT'])
def change_group_lang() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	group = request.json
	dicts.settings.change_group_lang(group['name'], group['lang'])
	response = jsonify(dicts.settings.get_groups())
	return response

@api.route('/management/group_name', methods=['PUT'])
def change_group_name() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	info = request.json
	dicts.settings.change_group_name(info['old'], info['new'])
	response = jsonify({
		'groups': dicts.settings.get_groups(),
		'groupings': dicts.settings.get_dictionary_groupings()
	})
	return response

@api.route('/management/dictionary_groupings', methods=['GET', 'POST', 'DELETE'])
def dictionary_groupings() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = jsonify(dicts.settings.get_dictionary_groupings())
	elif request.method == 'POST': # Add a dictionary to a group
		info = request.json
		dicts.settings.add_dictionary_to_group(info['dictionary_name'], info['group_name'])
		response = jsonify(dicts.settings.get_dictionary_groupings())
	elif request.method == 'DELETE': # Remove a dictionary from a group
		info = request.json
		dicts.settings.remove_dictionary_from_group(info['dictionary_name'], info['group_name'])
		response = jsonify(dicts.settings.get_dictionary_groupings())
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/history', methods=['GET', 'DELETE', 'PUT'])
def history() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = jsonify(dicts.settings.lookup_history)
	elif request.method == 'DELETE':
		dicts.settings.clear_history()
		response = jsonify(dicts.settings.lookup_history)
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/history_size', methods=['GET', 'PUT'])
def history_size() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = jsonify({'size': dicts.settings.misc_configs['history_size']})
	elif request.method == 'PUT': # Should be used to change history size
		history_size = int(request.json['size'])
		dicts.settings.set_history_size(history_size)
		response = jsonify(dicts.settings.lookup_history)
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/num_suggestions', methods=['GET', 'PUT'])
def num_suggestions() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = jsonify({'size': dicts.settings.misc_configs['num_suggestions']})
	elif request.method == 'PUT':
		num_suggestions = int(request.json['size'])
		dicts.settings.set_suggestions_size(num_suggestions)
		response = jsonify({'size': dicts.settings.misc_configs['num_suggestions']})
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/create_ngram_table')
def create_ngram_table() -> 'Response':
	db_manager.create_ngram_table()
	logger.info('Recreated ngram table')
	response = jsonify({'success': True})
	return response
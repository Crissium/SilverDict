from flask import current_app, request, Response
from .utils import make_yaml_response, parse_yaml
from . import api

@api.route('/management/formats')
def get_formats() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	response = make_yaml_response(list(dicts.settings.SUPPORTED_DICTIONARY_FORMATS.keys()))
	return response

@api.route('/management/dictionaries', methods=['GET', 'POST', 'DELETE', 'PUT'])
def dictionaries() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = make_yaml_response(dicts.settings.dictionaries_list)
	elif request.method == 'POST':
		dictionary_info = parse_yaml(request.get_data())
		group_name = dictionary_info.pop('group_name')
		dicts.add_dictionary(dictionary_info)
		dicts.settings.add_dictionary_to_group(dictionary_info['dictionary_name'], group_name)
		response = make_yaml_response({
			'dictionaries': dicts.settings.dictionaries_list,
			'groupings': dicts.settings.get_dictionary_groupings()
		})
	elif request.method == 'DELETE':
		dictionary_name = parse_yaml(request.get_data())['name']
		dictionary_info = dicts.settings.info_of_dictionary(dictionary_name)
		dicts.remove_dictionary(dictionary_info)
		response = make_yaml_response({
			'dictionaries': dicts.settings.dictionaries_list,
			'groupings': dicts.settings.get_dictionary_groupings()
		})
	elif request.method == 'PUT': # Should only be used to reorder dictionaries
		dictionaries_info = parse_yaml(request.get_data())
		dicts.settings.reorder_dictionaries(dictionaries_info)
		response = make_yaml_response(dicts.settings.dictionaries_list)
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/dictionary_name', methods=['PUT'])
def change_dictionary_name() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	info = parse_yaml(request.get_data())
	dicts.settings.change_dictionary_display_name(info['name'], info['display'])
	response = make_yaml_response({'success': True})
	return response

@api.route('/management/sources', methods=['GET', 'POST', 'DELETE'])
def sources() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = make_yaml_response(dicts.settings.misc_configs['sources'])
	elif request.method == 'POST':
		source = parse_yaml(request.get_data())['source']
		dicts.settings.add_source(source)
		response = make_yaml_response(dicts.settings.misc_configs['sources'])
	elif request.method == 'DELETE':
		source = parse_yaml(request.get_data())['source']
		dicts.settings.remove_source(source)
		response = make_yaml_response(dicts.settings.misc_configs['sources'])
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/scan')
def scan_sources() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	for dictionary_info in dicts.settings.scan_sources():
		dicts.add_dictionary(dictionary_info)
	response = make_yaml_response({
		'dictionaries': dicts.settings.dictionaries_list,
		'groupings': dicts.settings.get_dictionary_groupings()
	})
	return response

@api.route('/management/groups', methods=['GET', 'POST', 'DELETE', 'PUT'])
def groups() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = make_yaml_response(dicts.settings.groups)
	elif request.method == 'POST':
		group = parse_yaml(request.get_data())
		dicts.settings.add_group(group)
		response = make_yaml_response({
			'groups': dicts.settings.groups,
			'groupings': dicts.settings.get_dictionary_groupings()
		})
	elif request.method == 'DELETE':
		group_name = parse_yaml(request.get_data())['name']
		dicts.settings.remove_group_by_name(group_name)
		response = make_yaml_response({
			'groups': dicts.settings.groups,
			'groupings': dicts.settings.get_dictionary_groupings()
		})
	elif request.method == 'PUT': # Should only be used to reorder groups
		groups = parse_yaml(request.get_data())
		dicts.settings.reorder_groups(groups)
		response = make_yaml_response(dicts.settings.groups)
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/group_lang', methods=['PUT'])
def change_group_lang() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	group = parse_yaml(request.get_data())
	dicts.settings.change_group_lang(group['name'], group['lang'])
	response = make_yaml_response(dicts.settings.groups)
	return response

@api.route('/management/group_name', methods=['PUT'])
def change_group_name() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	info = parse_yaml(request.get_data())
	dicts.settings.change_group_name(info['old'], info['new'])
	response = make_yaml_response({
		'groups': dicts.settings.groups,
		'groupings': dicts.settings.get_dictionary_groupings()
	})
	return response

@api.route('/management/dictionary_groupings', methods=['GET', 'POST', 'DELETE'])
def dictionary_groupings() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = make_yaml_response(dicts.settings.get_dictionary_groupings())
	elif request.method == 'POST': # Add a dictionary to a group
		info = parse_yaml(request.get_data())
		dicts.settings.add_dictionary_to_group(info['dictionary_name'], info['group_name'])
		response = make_yaml_response(dicts.settings.get_dictionary_groupings())
	elif request.method == 'DELETE': # Remove a dictionary from a group
		info = parse_yaml(request.get_data())
		dicts.settings.remove_dictionary_from_group(info['dictionary_name'], info['group_name'])
		response = make_yaml_response(dicts.settings.get_dictionary_groupings())
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/history', methods=['GET', 'DELETE', 'PUT'])
def history() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = make_yaml_response(dicts.settings.lookup_history)
	elif request.method == 'DELETE':
		dicts.settings.clear_history()
		response = make_yaml_response(dicts.settings.lookup_history)
	elif request.method == 'PUT': # Should be used to change history size
		history_size = int(parse_yaml(request.get_data())['size'])
		dicts.settings.set_history_size(history_size)
		response = make_yaml_response(dicts.settings.lookup_history)
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response

@api.route('/management/num_suggestions', methods=['GET', 'PUT'])
def num_suggestions() -> 'Response':
	dicts = current_app.extensions['dictionaries']
	if request.method == 'GET':
		response = make_yaml_response({'size': dicts.settings.misc_configs['num_suggestions']})
	elif request.method == 'PUT':
		num_suggestions = int(parse_yaml(request.get_data())['size'])
		dicts.settings.set_suggestions_size(num_suggestions)
		response = make_yaml_response({'size': dicts.settings.misc_configs['num_suggestions']})
	else:
		raise ValueError('Invalid request method %s' % request.method)
	return response
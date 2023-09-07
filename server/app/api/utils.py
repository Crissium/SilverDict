from flask import make_response, Response
import yaml
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
	from yaml import CSafeLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import SafeLoader as Loader, Dumper
	logger.warning('Using pure Python YAML parser. Consider installing libyaml for faster speed.')

YAML_CONTENT_TYPE = 'text/plain; charset=utf-8'

def make_yaml_response(data: 'list | dict') -> 'Response':
	return make_response(yaml.dump(data, Dumper=Dumper), 200, {'Content-Type': YAML_CONTENT_TYPE})

def parse_yaml(data: 'str') -> 'list | dict':
	return yaml.load(data, Loader=Loader)
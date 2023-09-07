from flask import Blueprint

api = Blueprint('api', __name__)

from . import lookup, management, validators

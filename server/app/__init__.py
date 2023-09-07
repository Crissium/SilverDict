from flask import Flask
from flask_cors import CORS
from .dictionaries import Dictionaries

def create_app() -> 'Flask':
	app = Flask(__name__)
	Dictionaries(app)
	CORS(app)
	from .api import api
	app.register_blueprint(api, url_prefix='/api')
	return app
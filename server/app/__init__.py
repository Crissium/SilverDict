from flask import Flask
from flask_cors import CORS
from .dictionaries import Dictionaries


def create_app() -> Flask:
	app = Flask(__name__, static_folder='../build', static_url_path='/silverdict/')
	Dictionaries(app)
	CORS(app)
	from .api import api
	app.register_blueprint(api, url_prefix='/silverdict/api')

	@app.route('/silverdict/')
	def index():
		return app.send_static_file('index.html')

	return app

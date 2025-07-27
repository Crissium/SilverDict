import os
from flask import Flask, render_template_string
from flask_cors import CORS
from .dictionaries import Dictionaries
from pathlib import Path

def create_app(base_url: str) -> Flask:
	app = Flask(__name__, static_folder='../build', static_url_path=f'{base_url}/')
	Dictionaries(app)
	CORS(app)
	from .api import api
	app.register_blueprint(api, url_prefix=f'{base_url}/api')

	index_string = (Path(__file__).parent.parent / 'build/index.html').read_text()

	@app.route(f'{base_url}/')
	def index():
		return render_template_string(index_string, base_url=base_url)

	return app

from app import create_app
from waitress import serve
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
	app = create_app()
	serve(app, listen='%s:%s' % (app.extensions['dictionaries'].settings.preferences['listening_address'], app.extensions['dictionaries'].settings.PORT))

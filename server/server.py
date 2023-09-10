from app import create_app
from waitress import serve

if __name__ == '__main__':
	app = create_app()
	serve(app, listen='0.0.0.0:%s' % app.extensions['dictionaries'].settings.PORT, threads=8)

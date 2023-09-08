from app import create_app
from waitress import serve

if __name__ == '__main__':
	app = create_app()
	serve(app, listen='localhost:%s' % app.extensions['dictionaries'].settings.PORT, threads=8)

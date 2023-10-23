from app import create_app
from waitress import serve
import sys
import threading
import os
import webbrowser
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
	app = create_app()
	if len(sys.argv) > 1: # specify the address to listen on
		address = sys.argv[1]
		if ':' in address:
			host, port = address.split(':')
		else:
			host = address
			port = app.extensions['dictionaries'].settings.PORT
	else:
		host = app.extensions['dictionaries'].settings.preferences['listening_address']
		port = app.extensions['dictionaries'].settings.PORT

	if os.getenv('BROWSER'): # mainly for use on a-Shell
		server_thread = threading.Thread(target=lambda: serve(app, listen='%s:%s' % (host, port)))
		server_thread.start()
		webbrowser.open('http://localhost:%s' % port)
		server_thread.join()
	else:
		serve(app, listen='%s:%s' % (host, port))

from app import create_app
from waitress import serve


silver_dict = create_app()
serve(silver_dict, listen='localhost:%s' % silver_dict.configs.PORT)
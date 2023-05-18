from .silverdict import SilverDict
from flask_cors import CORS


def create_app() -> 'SilverDict':
    app = SilverDict()
    CORS(app)
    return app
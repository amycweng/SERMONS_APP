from flask import Flask
from .config import Config
from .db import DB
from .vectordb import Vector_DB

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    app.db = DB(app)
    app.vectordb = Vector_DB()

    from .index import bp as index_bp
    app.register_blueprint(index_bp)
    
    from .sermon import bp as sermon_bp
    app.register_blueprint(sermon_bp)

    from .author import bp as author_bp
    app.register_blueprint(author_bp)
    return app

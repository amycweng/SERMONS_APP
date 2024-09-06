from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB
from .vectordb import Vector_DB

login = LoginManager()
login.login_view = 'users.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    app.db = DB(app)
    app.vectordb = Vector_DB()
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)
    
    from .sermon import bp as sermon_bp
    app.register_blueprint(sermon_bp)

    from .author import bp as author_bp
    app.register_blueprint(author_bp)

    from .download import bp as download_bp
    app.register_blueprint(download_bp)
    return app

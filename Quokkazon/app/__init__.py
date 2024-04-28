from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = 'static/product_images'
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    app.db = DB(app)
    login.init_app(app)

    from ...app.index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)
    
    from .products import bp as products_bp
    app.register_blueprint(products_bp)

    from .feedback import bp as feedback_bp
    app.register_blueprint(feedback_bp)

    from .allpurchases import bp as allpurchases_bp
    app.register_blueprint(allpurchases_bp)

    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .profile import bp as profile_bp
    app.register_blueprint(profile_bp)
    
    from .categories import bp as categories_bp
    app.register_blueprint(categories_bp)
    
    from .messages import bp as messages_bp
    app.register_blueprint(messages_bp)

    from .userlookup import bp as userlookup_bp
    app.register_blueprint(userlookup_bp)
    
    return app

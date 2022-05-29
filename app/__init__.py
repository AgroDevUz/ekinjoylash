from functools import cache
from flask import Flask
from flask_login import LoginManager
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension

login_manager = LoginManager()
admin = Admin(name='microblog', template_mode='bootstrap4')
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
toolbar = DebugToolbarExtension()
def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('configs/config.py')
    login_manager.init_app(app)
    admin.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    toolbar.init_app(app)
    from app.main.routes import main
    from app.api.routes import api
    app.register_blueprint(main)
    app.register_blueprint(api)
    
    @app.after_request
    def after_request(response):
        header = response.headers
        header.add('Access-Control-Allow-Origin', '*')
        header.add('Access-Control-Allow-Headers', '*')
        header.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
    from app.main.admin import MicroBlogModelView, GeoModelView
    from app.main.models import User, Province, District, Permission, CropName
    admin.add_view(MicroBlogModelView(User, db.session))
    admin.add_view(GeoModelView(Province, db.session))
    admin.add_view(GeoModelView(District, db.session))
    admin.add_view(MicroBlogModelView(Permission, db.session))
    admin.add_view(MicroBlogModelView(CropName, db.session))

    return app
    
    
    
    
    
    
    
    
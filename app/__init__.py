from flask import Flask
from flask_login import LoginManager
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
login_manager = LoginManager()
admin = Admin(name='microblog', template_mode='bootstrap4')
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('configs/config.py')
    login_manager.init_app(app)
    admin.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.main.routes import main
    app.register_blueprint(main)
    
    @app.after_request
    def after_request(response):
        header = response.headers
        header.add('Access-Control-Allow-Origin', '*')
        header.add('Access-Control-Allow-Headers', '*')
        header.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
    from app.main.admin import MicroBlogModelView
    from app.main.models import User, Province, District, Permission, CropName
    admin.add_view(MicroBlogModelView(User, db.session))
    admin.add_view(MicroBlogModelView(Province, db.session))
    admin.add_view(MicroBlogModelView(District, db.session))
    admin.add_view(MicroBlogModelView(Permission, db.session))
    admin.add_view(MicroBlogModelView(CropName, db.session))

    return app
    
    
    
    
    
    
    
    
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager



db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    

    #max connections fix
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "max_overflow": -1,
    "pool_pre_ping": True,
    "pool_recycle": 60 * 60,
    #"pool_size": 30,
    "pool_size": 60,
    }

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/onbudgetdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dddddfdsfsdfsdfsfds'
    db = SQLAlchemy(app)
    db.init_app(app)



    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    #, Category

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    
    
    return app


def create_database(app):
    if not path.exists('website/onbudgetdb'):
        db.create_all(app=app)
        print('Successfully created database')

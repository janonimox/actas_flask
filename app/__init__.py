from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave_secreta_segura'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///actas.db'

    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    from .models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app

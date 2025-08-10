from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Extensiones (una sola instancia global)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# A dónde enviar si no está logueado
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)

    # Config base
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_secreta_segura')  # cámbiala en prod
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///actas.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Archivos subidos (firmas)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'firmas')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4 MB

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Importar modelos y rutas DESPUÉS de init_app, para evitar import circular
    with app.app_context():
        from . import models  # registra modelos
        from .models import Usuario
        from .routes import bp as main_bp
        app.register_blueprint(main_bp)

        @login_manager.user_loader
        def load_user(user_id):
            return Usuario.query.get(int(user_id))

    return app

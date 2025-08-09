from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    cesfam = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(64), default='administrativo')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Acta(db.Model):
    __tablename__ = 'actas'
    id = db.Column(db.Integer, primary_key=True)
    numero_correlativo = db.Column(db.String(64))
    nombres = db.Column(db.String(128))
    apellidos = db.Column(db.String(128))
    rut = db.Column(db.String(20))
    tipo_contrato = db.Column(db.String(64))
    rut_reemplazo = db.Column(db.String(20))
    nombre_reemplazo = db.Column(db.String(128))
    salud = db.Column(db.String(64))
    plan_isapre = db.Column(db.String(128))
    afp = db.Column(db.String(128))
    convenio = db.Column(db.String(128))
    responsable = db.Column(db.String(128))
    fecha_contratacion = db.Column(db.Date)
    periodo_remunerativo = db.Column(db.String(10))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    cesfam = db.Column(db.String(128))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    firma_filename = db.Column(db.String(120))  # <- nuevo campo

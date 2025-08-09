import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///actas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'app/static/firmas'

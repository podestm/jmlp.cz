from flask_sqlalchemy import SQLAlchemy

class Config:
    SECRET_KEY = 'secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/jmlp_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    REGISTRATIONS_FOLDER = 'registrations'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    DB_NAME = "jmlp_test"
    
db = SQLAlchemy()
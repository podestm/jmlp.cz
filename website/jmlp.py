from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from config import  Config, db



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

from views import views
from auth import auth
from admin import admin

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(auth, url_prefix='/')

from models import User
    
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

if __name__ == '__main__':
    app.run(debug=True)

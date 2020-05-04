import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from datetime import timedelta, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
mysql_login = os.environ.get('DB_LOGIN')
mysql_pass = os.environ.get('DB_PASS')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + mysql_login + ':' + mysql_pass + '@localhost/mynotes'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
loginManager = LoginManager(app)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(7)
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

from mynotes.accounts.routes import accounts
from mynotes.articles.routes import rticles
from mynotes.tags.routes import tgs
from mynotes.errors.handlers import errors
from mynotes.keys.routes import kys

app.register_blueprint(accounts)
app.register_blueprint(rticles)
app.register_blueprint(tgs)
app.register_blueprint(errors)
app.register_blueprint(kys)

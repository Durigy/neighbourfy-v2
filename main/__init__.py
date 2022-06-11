from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from datetime import timedelta
import os

SECRET_KEY = ''
DATABASE_URL = ''
DEBUG = False
REMEMBER_COOKIE_DURATION = timedelta(days=1)
SQLALCHEMY_TRACK_MODIFICATIONS = False

if os.path.exists('main/config.py'):
    from .config import secret_key, database_uri, debug_setting, remember_cookie_duration, sqlalchemy_track_modifications
    SECRET_KEY = secret_key
    DATABASE_URL = database_uri
    DEBUG = debug_setting
    REMEMBER_COOKIE_DURATION = remember_cookie_duration
    SQLALCHEMY_TRACK_MODIFICATIONS = sqlalchemy_track_modifications

app = Flask(__name__)

# secret_key_setting
if os.environ.get("SECRET_KEY"): SECRET_KEY = os.environ.get("SECRET_KEY")
app.config['SECRET_KEY'] = SECRET_KEY

# database_setting
if os.environ.get("DATABASE_URL"): DATABASE_URL = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# debug_setting
if os.environ.get("DEBUG"): DEBUG = os.environ.get("DEBUG")
app.config['DEBUG'] = DEBUG

# remember_me_cookie_setting
if os.environ.get("REMEMBER_COOKIE_DURATION"): REMEMBER_COOKIE_DURATION = os.environ.get("REMEMBER_COOKIE_DURATION")
app.config['REMEMBER_COOKIE_DURATION'] = REMEMBER_COOKIE_DURATION

# sqlalchemy_modifications_setting
if os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS"): SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

bcrypt = Bcrypt(app)

from . import routes
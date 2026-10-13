import os
import sys
import subprocess, re
import psutil
import yaml
import time
import json
import socket

from pathlib import Path
from flask import Flask, render_template, url_for, redirect, request
from flask import flash, session

import secrets
import stat

# Authentication Add-On
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap

# from models import User

# Bootstrap the DB (for flask-login)
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# Flask Form Validation
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp ,Optional
from flask_wtf import FlaskForm
import email_validator
from wtforms import ValidationError,validators

from rdm_session import RemoteSessionTunnel

# global config
# global devicename
# global gamehost
# global f1fwd
# global f1store
# global dburl

# Initialise App Backend for flask-login
def create_app():
    app = Flask(__name__) 
    Bootstrap(app)
    SECRET_FILE_PATH = Path(".f1sim_secret")
    try:
        with SECRET_FILE_PATH.open("r") as secret_file:
            app.secret_key = secret_file.read()
    except FileNotFoundError:
        # Let's create a cryptographically secure code in that file
        with SECRET_FILE_PATH.open("w") as secret_file:
            app.secret_key = secrets.token_hex(32)
            secret_file.write(app.secret_key)
            os.chmod(SECRET_FILE_PATH, stat.S_IRUSR)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app,db)
    bcrypt.init_app(app)
    return app


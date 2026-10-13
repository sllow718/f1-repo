import os
import sys
import subprocess, re
import psutil
import yaml
import time
import json
import socket

import stat
import secrets
from pathlib import Path
import argparse

import click
from flask import Flask, render_template, url_for, redirect, request
from flask import flash, session

# Authentication Add-On
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required

# Bootstrap the DB (for flask-login)
# db = SQLAlchemy()
# migrate = Migrate()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.session_protection = "strong"
# login_manager.login_view = "login"
# login_manager.login_message_category = "info"

from app import db
# to allow for dash in python module

# DB Model for flask-login
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)
    client_secret_b32 = db.Column(db.String(300), nullable=True, unique=True)
    client_secret_oauth = db.Column(db.String(300), nullable=True, unique=True)
    client_id = db.Column(db.String(300), nullable=True, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username


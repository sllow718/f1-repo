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
import pyotp
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

from app import db,migrate,bcrypt,login_manager,create_app
from models import User

# Initialise App Backend for flask-login
# Bootstrap this for the "once-off" execution and except out if already exists
def deploy_app():
    try:
        """Run deployment tasks."""
        # from app import create_app,db
        from flask_migrate import upgrade,migrate,init,stamp
        # from models import User
        app = create_app()
        app.app_context().push()
        db.create_all()
        # migrate database to latest revision
        init()
        stamp()
        migrate()
        upgrade()
    except:
        print(sys.exc_info()[0])

deploy_app()
app = create_app()

@app.cli.command("create")
@click.option("--username")
@click.option("--email")
@click.option("--password")
def create_user(username, email, password):
    try:
        newuser = User(
          username=username,
          email=email,
          pwd=bcrypt.generate_password_hash(password),
          client_id="f1simid_{}".format(secrets.token_hex(32)),
          client_secret_oauth="f1simsecret_{}".format(secrets.token_hex(32)),
          client_secret_b32=pyotp.random_base32()
        )
        db.session.add(newuser)
        db.session.commit()
    except InvalidRequestError:
        db.session.rollback()
    except IntegrityError:
        db.session.rollback()
    except DataError:
        db.session.rollback()
    except InterfaceError:
        db.session.rollback()
    except DatabaseError:
        db.session.rollback()

@app.cli.command("alter")
@click.option("--username")
@click.option("--password")
def alter_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user != None:
        user.pwd = bcrypt.generate_password_hash(password)
        db.session.commit()

@app.cli.command("drop")
@click.option("--username")
def drop_user(username):
    user = User.query.filter_by(username=username).first()
    print(user)
    if user != None:
        db.session.delete(user)
        db.session.commit()


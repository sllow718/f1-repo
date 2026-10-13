import os
import sys
import subprocess, re
import psutil
import yaml
import time
import json
import socket

from pathlib import Path
from flask import Flask, render_template, url_for, redirect, request, send_from_directory
from flask import flash, session
from flask import jsonify

import hmac, base64, struct, hashlib, time
import pyotp
import qrcode
import io
import urllib

# Authentication Add-On
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_httpauth import HTTPBasicAuth

# Flask Form Validation
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp ,Optional
from flask_wtf import FlaskForm
import email_validator
from wtforms import ValidationError,validators

from app import create_app,db,login_manager,bcrypt
from models import User
import secrets

from rdm_session import RemoteSessionTunnel

# global config
# global devicename
# global gamehost
# global f1fwd
# global f1store
# global dburl

app = create_app()
auth = HTTPBasicAuth()

def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    #decoding our key
    msg = struct.pack(">Q", intervals_no)
    #conversions between Python values and C structs represente
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = o = h[19] & 15
    #Generate a hash using both of these. Hashing algorithm is HMAC
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    #unpacking
    return h

def get_totp_token(secret):
    #ensuring to give the same otp for 30 seconds
    x =str(get_hotp_token(secret,intervals_no=int(time.time())//30))
    #adding 0 in the beginning till OTP has 6 digits
    while len(x)!=6:
        x+='0'
    return x

# User Admin Form Data Model
class user_admin_form(FlaskForm):
    email = StringField('Email',render_kw={ "readonly": True })
    hidden = HiddenField('Random')
    pwd = StringField('Password',validators=[Length(min=8, max=72)])
    cpwd = StringField('Confirm Password',validators=[Length(min=8, max=72),EqualTo("pwd", message="Passwords must match !")])
    client_id = StringField('Client ID',render_kw={ "readonly": True })
    client_secret_b32 = StringField('Client Base32 Secret',render_kw={ "readonly": True })
    client_secret_oauth = StringField('Client OAuth Secret',render_kw={ "readonly": True })
    submit = SubmitField('Save')
    rotate = SubmitField('Rotate')

# Integrity Check - if email already exists
def validate_email(self, email):
    if User.query.filter_by(email=email.data).first():
        raise ValidationError("Email already registered!")

# Integrity Check - if username already exists
def validate_uname(self, uname):
    if User.query.filter_by(username=username.data).first():
        raise ValidationError("Username already taken!")

# Login Form Data Model
class login_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField()
    otp = PasswordField()
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login route
@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()
    checkusers = User.query.all()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            # print(user)
            # print(user.email)
            # print(user.client_secret_b32)
            # print(user.client_secret_oauth)
            # print(user.pwd)
            if form.pwd.data != None and check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            elif form.otp.data != "" and form.otp.data == get_totp_token(user.client_secret_b32):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")
    return render_template("login.html",form=form,btn_action="Login",nousers=(len(checkusers)==0))

@app.route("/user/cancel", methods=["GET"], strict_slashes=False)
@login_required
def user_admin_cancel():
    return redirect(url_for('index'))

# update user route
@app.route("/user/admin/", methods=("GET", "POST"), strict_slashes=False)
@login_required
def user_admin():
    form = user_admin_form()
    ignore_password = False
    if request.method == 'POST':
        ignore_password = (form.pwd.data == "")
        if ignore_password:
            form.pwd.data = secrets.token_hex(8)
            form.cpwd.data = form.pwd.data
    if form.validate_on_submit() and form.submit.data:
        try:
            if ignore_password == False:
                current_user.pwd = bcrypt.generate_password_hash(form.pwd.data)
            current_user.client_id = form.client_id.data
            current_user.client_secret_oauth = form.client_secret_oauth.data
            current_user.client_secret_b32 = form.client_secret_b32.data
            db.session.commit()
            return redirect(url_for('index'))
        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    elif form.validate_on_submit() and form.rotate.data:
        # db.query to get current user (and populate form)_
        form.email.data = current_user.email
        form.client_id.data = "f1simid_{}".format(secrets.token_hex(32))
        form.client_secret_oauth.data = "f1simsecret_{}".format(secrets.token_hex(32))
        form.client_secret_b32.data = pyotp.random_base32()
        form.pwd.data = ""
        form.cpwd.data = ""
    else:
        # db.query to get current user (and populate form)_
        form.email.data = current_user.email
        form.client_id.data = current_user.client_id
        form.client_secret_oauth.data = current_user.client_secret_oauth
        form.client_secret_b32.data = current_user.client_secret_b32
    return render_template("userdetails.html",form=form,btn_action="Save")

@app.route("/user/otp")
@login_required
def user_otp():
    urlsafe_email = urllib.parse.quote(current_user.email)
    urlsafe_secret = urllib.parse.quote(current_user.client_secret_b32)
    totp_url = f'otpauth://totp/f1sim:{urlsafe_email}?secret={urlsafe_secret}&issuer=f1sim'
    # print(totp_url)
    qrcode_img = qrcode.make(totp_url)
    qrcode_bytes = io.BytesIO()
    qrcode_img.save(qrcode_bytes)
    qrcode_bytes.seek(0)
    qrcode_str = base64.b64encode(qrcode_bytes.read()).decode()
    # print(qrcode_str)
    return render_template("otpdetails.html",qrcode_imgb64=qrcode_str)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

rst = None # RemoteSessionTunnel()

storeyml = os.environ['F1SIM_HOME'] + "/f1store.yaml" 

def load_f1store():
    global config
    global devicename
    global gamehost
    global f1fwd
    global f1store
    global dburl
    global rmqusername
    global rmqpassword
    global storetxt
    global hometrack
    global gameversion
    global leaderboardurl
    global registrationurl
    global runningguideurl
    global trackapi
    global sessionapi
    global serverip
    global rst
    global remote_parameters

    with open(storeyml, 'r') as f:
        storetxt = f.read()
        config = yaml.safe_load(storetxt)
    devicename = config['devicename']
    gamehost = config['gamehost']
    f1fwd = config['forward']
    f1store = config['store']
    dburl = config['oracledb']['properties']['dburl']
    rmqusername = config['rabbitmq']['properties']['rmqusername']
    rmqpassword = config['rabbitmq']['properties']['rmqpassword']
    hometrack = config['hometrack']
    gameversion = config['version']
    trackapi = config['trackapi']
    sessionapi = config['sessionapi']
    leaderboardurl = config['leaderboard']
    registrationurl = config['registration']
    runningguideurl = config['runningguide']
    remote_parameters = {}
    remote_parameters["ssh_host"] = config['remote']['sshhost'] # "services.withoracle.cloud"
    remote_parameters["ssh_user"] = config['remote']['sshuser'] # "pi"
    remote_parameters["ssh_key_file"] = config['remote']['sshkeyfile'] # "/home/pi/.ssh/fort-bastion"
    remote_parameters["autostart"] = config['remote']['autostart']
    # remote_parameters["port_segment"] = config['remote']['portsegment'] # 10000
    restart = False
    if rst != None and rst.is_running():
        rst.stop_session()
        restart = True
    rst = RemoteSessionTunnel(remote_parameters)
    if restart or remote_parameters["autostart"]:
        rst.create_session()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def save_f1store():
    with open(storeyml, 'w') as f:
        f.write(storetxt)

# initial load of f1store.yaml
load_f1store()

serverip = get_local_ip()

# Home route
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template('index.html', ipaddr=serverip, dname=devicename, ghost=gamehost)

@app.route('/about')
def about():
    return render_template('about.html', ipaddr=serverip)

@app.route('/circuit')
def circuit():
    data = {'hometrack': hometrack, 'packetformat': gameversion}
    return render_template('livemap.html', data=data)

@app.route('/circuit/svg')
def svg_circuit():
    data = {'hometrack': hometrack, 'packetformat': gameversion, 'trackapi': trackapi, 'sessionapi': sessionapi}
    return render_template('trackmap_svg.html', data=data)

@app.route('/analyser')
def analyser():
    data = {'gamehost' : gamehost, 'hometrack': hometrack, 'packetformat': gameversion, 'trackapi': trackapi, 'sessionapi': sessionapi}
    return render_template('trackanalyser.html', data=data)

@app.route('/telemetry')
def telemetry():
    data = {'rmqusername': rmqusername, 'rmqpassword': rmqpassword, 'hometrack': hometrack, 'packetformat': gameversion}
    return render_template('f1telemetry.html', data=data)

@app.route('/telemetry/svg')
def svg_telemetry():
    data = {'rmqusername': rmqusername, 'rmqpassword': rmqpassword, 'hometrack': hometrack, 'packetformat': gameversion}
    return render_template('f1telemetry_svg.html', data=data)

@app.route('/leaderboard')
def leaderboard():
    return redirect(leaderboardurl)

@app.route('/registration')
def registration():
    return redirect(registrationurl)

@app.route('/runningguide')
def runningguide():
    return redirect(runningguideurl)

@app.route('/jetDB')
def jet():
    return render_template('f1Jet.html')

@app.route('/chart')
def charting():
    return render_template('chart.html')

@app.route('/rbr/<car>')
def modelviewer(car):

    modelURL = url_for('static', filename='images/RB_18_Max_v05')

    if car == "rb16":
        modelURL = url_for('static', filename='images/F1RB16B_v44')

    return render_template('f1Model.html', model=modelURL)

@app.route('/service')
@login_required
def services():
    # Runtime State of Control Buttons
    f1cons = read_status('f1sim-consumer')
    if (("status" in f1cons) == False) or (("running" in f1cons['status']) == False):
        f1consbtn = 'Start Consumer'
    else:
        f1consbtn = 'Stop Consumer'
    f1prod = read_status('f1sim-producer')
    if (("status" in f1prod) == False) or (("running" in f1prod['status']) == False):
        f1prodbtn = 'Start Producer'
    else:
        f1prodbtn = 'Stop Producer'
    f1webs = read_status('f1sim-webserver')
    f1websbtn = 'Restart Web Server'
    f1rmqs = read_status('rabbitmq-server')
    if (("status" in f1rmqs) == False) or (("running" in f1rmqs['status']) == False):
        f1rmqsbtn = 'Start RabbitMQ'
    else:
        f1rmqsbtn = 'Stop RabbitMQ'

    # Process States (commented out as not displayed)
    # processes = []
    # for proc in psutil.process_iter():
    #     try:
    #         # Get process name & pid from process object.
    #         processName = proc.name()
    #         processID = proc.pid
    #         processes.append((processName , ' ::: ', processID))
    #         # print(processName , ' ::: ', processID)
    #     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
    #         pass
    # proc = {'running': ' '.join(str(e) for e in processes)}
    proc = {}

    # PI Information
    stream = os.popen('python3 web/info.py') 
    output = stream.read()
    info = {'status': 'true', 'output': output}

    # Store and Forward Configuration
    f1param = {'store': f1store, 'forward': f1fwd, 'db': dburl}

    # RabbitMQ Queue Data
    f1rmqlq = list_queues()

    body = {'process': proc, 'info': info, 'f1prod': f1prod, 'f1cons': f1cons, 'f1webs': f1webs, 'f1rmqs': f1rmqs, 'f1store': f1param, 'f1rmqlq': f1rmqlq }

    return render_template('service-status.html', dname=devicename, ghost=gamehost, f1consbtn=f1consbtn, f1prodbtn=f1prodbtn, f1websbtn=f1websbtn, f1rmqsbtn=f1rmqsbtn, body=body)

@app.route('/yaml')
@login_required
def f1config():
    return render_template('f1yaml.html', storetxt = storetxt)

@app.route('/yaml/load')
@login_required
def f1config_load():
    load_f1store()
    return redirect(url_for('f1config'))

@app.route('/yaml/save', methods=['POST'])
@login_required
def f1config_save():
    global storetxt
    storetxt = request.form['storetxt'].replace('\r','')
    # print(storetxt)
    save_f1store()
    return redirect(url_for('f1config'))

@app.route('/test')
@login_required
def testingMQ():
    return render_template('rmq_test.html')

@app.route('/control/producer')
@login_required
def control_producer():
    f1prod = read_status('f1sim-producer')
    if (("status" in f1prod) == False) or (("running" in f1prod['status']) == False):
        control = 'start'
    else:
        control = 'stop'
    p =  subprocess.Popen(['sudo', 'systemctl', control, 'f1sim-producer'], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    # print(output)
    return redirect(url_for('services'))

@app.route('/control/consumer')
@login_required
def control_consumer():
    f1cons = read_status('f1sim-consumer')
    if (("status" in f1cons) == False) or (("running" in f1cons['status']) == False):
        control = 'start'
    else:
        control = 'stop'
    p =  subprocess.Popen(['sudo', 'systemctl', control, 'f1sim-consumer'], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    # print(output)
    return redirect(url_for('services'))

@app.route('/control/webserver')
@login_required
def control_webserver():
    f1webs = read_status('f1sim-webserver')
    control = 'restart'
    p =  subprocess.Popen(['sudo', 'systemctl', control, 'f1sim-webserver'], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    # print(output)
    return redirect(url_for('services'))

@app.route('/control/rabbitmq')
@login_required
def control_rabbitmq():
    f1rmqs = read_status('rabbitmq-server')
    if (("status" in f1rmqs) == False) or (("running" in f1rmqs['status']) == False):
        control = 'start'
    else:
        control = 'stop'
    p =  subprocess.Popen(['sudo', 'systemctl', control, 'rabbitmq-server'], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    # print(output)
    return redirect(url_for('services'))

def list_queues():
    p =  subprocess.Popen(["sudo", "rabbitmqctl", "list_queues"], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    # print(output)
    queues = []
    status_regx= r"^(.*)\t(\d+)"
    for line in output.splitlines():
        queue_status = {}
        queue_search = re.search(status_regx, line)
        if queue_search:
            queue_status['name'] = queue_search.group(1).strip()
            queue_status['count'] = queue_search.group(2).strip()
            print(queue_status)
            queues.append(queue_status)
    return queues

def read_status(service):
    p =  subprocess.Popen(["sudo", "systemctl", "status",  service], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    # print(output)

    service_regx = r"Loaded:.*\/(.*service);"
    status_regx= r"Active:(.*) since (.*);(.*)"
    service_status = {}

    for line in output.splitlines():
        service_search = re.search(service_regx, line)
        status_search = re.search(status_regx, line)

        if service_search:
            service_status['service'] = service_search.group(1)
            #print("service:", service)

        if status_search:
            service_status['status'] = status_search.group(1).strip()
            #print("status:", status.strip())
            service_status['since'] = status_search.group(2).strip()
            #print("since:", since.strip())
            service_status['uptime'] = status_search.group(3).strip()
            #print("uptime:", uptime.strip())

    service_status['output'] = output
    return service_status

@app.route('/rdm/admin')
@login_required
def rdm_admin():
    global rst
    if rst.is_running() == False:
        remotebtn = "Start RDM Session"
    else:
        remotebtn = "Stop RDM Session"
    portsegment = rst.get_portsegment()
    if portsegment != -1:
        remoteportsegment = portsegment
    else:
        remoteportsegment = 0
    return render_template('f1rdm.html',remotebtn=remotebtn,remoteportsegment=remoteportsegment,rdm_checkremotekey=rst.checkremotekey(current_user),rdm_checklocalkey=rdm_checklocalkey())

@app.route('/rdm/control')
@login_required
def rdm_control():
    global rst
    if rst.is_running() == False:
        print("init session");
        rst.create_session()
    else:
        print("existing session");
        rst.stop_session()
    return redirect(url_for('rdm_admin'))

@app.route('/rdm/genlocal')
@login_required
def rdm_genlocalkey():
    global rst
    rst.generatelocalkey(remote_parameters["ssh_key_file"])
    ssh_key_dir = remote_parameters["ssh_key_file"][:remote_parameters["ssh_key_file"].rindex("/")]
    ssh_key_file = remote_parameters["ssh_key_file"][remote_parameters["ssh_key_file"].rindex("/")+1:]
    return send_from_directory(ssh_key_dir,ssh_key_file+".pub", as_attachment=True)

@app.route('/rdm/getlocal')
@login_required
def rdm_getlocalkey():
    ssh_key_dir = remote_parameters["ssh_key_file"][:remote_parameters["ssh_key_file"].rindex("/")]
    ssh_key_file = remote_parameters["ssh_key_file"][remote_parameters["ssh_key_file"].rindex("/")+1:]
    return send_from_directory(ssh_key_dir,ssh_key_file+".pub", as_attachment=True)

def rdm_checklocalkey():
    global rst
    ssh_key_file = remote_parameters["ssh_key_file"]
    return os.path.isfile(ssh_key_file+".pub")

@app.route('/rdm/addremote', methods=['POST'])
@login_required
def rdm_addremotekey():
    global rst
    storetxt = request.form['storetxt'].replace('\r','')
    rst.addremotekey(current_user.email,storetxt)
    return redirect(url_for('rdm_admin'))

@app.route('/rdm/removeremote', methods=['GET'])
@login_required
def rdm_removeremotekey():
    global rst
    rst.removeremotekey(current_user.email)
    return redirect(url_for('rdm_admin'))

@app.route('/api/info')
@auth.login_required
def get_info():
    info = { "gamehost" : gamehost, "devicename" : devicename }
    return jsonify(info)

@auth.verify_password
def verify_password(email, password):
    try:
        user = User.query.filter_by(email=email).first()
        if password == get_totp_token(user.client_secret_b32):
             return email 
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0") 

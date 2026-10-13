import sys
import subprocess
import shlex
import os
import yaml
import logging
import logging.config
import math
import time
import datetime
import json
import stat
from pathlib import Path
from datetime import datetime

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

from models import User

class RemoteSessionTunnel():

    def __init__(self,parameters={}):
        self.process = None
        self.ssh_host = parameters["ssh_host"]
        self.ssh_user = parameters["ssh_user"]

        self.ssh_key_file = parameters["ssh_key_file"]
        # self.port_segment = parameters["port_segment"]
        self.port_segment = None
        self.max_ttl = 0
        self.session_time_created = None
        print("Init Remote Session")

    def generatelocalkey(self,ssh_key_file):
        print("executed ssh-keygen")
        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048
        )
        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption()
        )
        public_key = key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH
        )
        ssh_key_dir = ssh_key_file[:ssh_key_file.rindex("/")]
        if os.path.exists(ssh_key_dir) == False:
            os.makedirs(ssh_key_dir)
        with open(ssh_key_file,"wb") as file:
            file.write(private_key)
        os.chmod(ssh_key_file, stat.S_IRUSR|stat.S_IWUSR)
        with open(ssh_key_file+".pub","wb") as file:
            file.write(public_key)

    def addremotekey(self,name,ssh_key_content):
        print("executed ssh-keygen")
        content = None
        try: 
            templines = [];
            if os.path.isfile(Path.home() / '.ssh' / 'authorized_keys'):
                with open(Path.home() / '.ssh' / 'authorized_keys','r') as file:
                    content = file.read()
                lines = content.split('\n')
                idx = 0;
                while idx < len(lines)-1:
                    line = lines[idx];
                    if line.lstrip().startswith('#') and name in line:
                        idx = idx + 1; 
                        print('removing next line')
                    else:
                        templines.append(line);
                    idx = idx + 1; 
            else:
                with open(Path.home() / '.ssh' / 'authorized_keys','w') as file:
                    file.write("# Created by f1sim-webserver\n")
                os.chmod(Path.home() / '.ssh' / 'authorized_keys', stat.S_IRUSR|stat.S_IWUSR)
            # print(templines);
            with open(Path.home() / '.ssh' / 'authorized_keys','w') as file:
                for line in templines:
                    file.write(line+'\n')
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                file.write('# {} SSH Public Key - {}\n'.format(name,dt_string))
                file.write('{}\n'.format(ssh_key_content))
        except Exception as ex:
            print(ex) 

    def removeremotekey(self,name):
        print("executed ssh-keygen")
        content = None
        try: 
            with open(Path.home() / '.ssh' / 'authorized_keys','r') as file:
                content = file.read()
            lines = content.split('\n')
            idx = 0;
            templines = [];
            while idx < len(lines)-1:
                line = lines[idx];
                if line.lstrip().startswith('#') and name in line:
                    idx = idx + 1; 
                    print('removing next line')
                else:
                    templines.append(line);
                idx = idx + 1; 
            # print(templines);
            with open(Path.home() / '.ssh' / 'authorized_keys','w') as file:
                for line in templines:
                    file.write(line+'\n')
        except Exception as ex:
            print(ex) 

    def listremotekeys(self):
        print("executed ssh-keygen")
        content = None
        ssh_keys_found = [];
        users = User.query.all();
        try: 
            with open(Path.home() / '.ssh' / 'authorized_keys','r') as file:
                content = file.read()
            lines = content.split('\n')
            idx = 0;
            while idx < len(lines)-1:
                line = lines[idx];
                if line.lstrip().startswith('#'):
                    for user in users:
                        if user.email in line:
                            ssh_keys_found.append(user.email)
                idx = idx + 1; 
        except Exception as ex:
            print(ex) 
        return ssh_keys_found

    def checkremotekey(self,current_user):
        print("executed ssh-keygen")
        content = None
        try: 
            with open(Path.home() / '.ssh' / 'authorized_keys','r') as file:
                content = file.read()
            lines = content.split('\n')
            idx = 0;
            while idx < len(lines)-1:
                line = lines[idx];
                if line.lstrip().startswith('#'):
                    if current_user.email in line:
                        return True
                idx = idx + 1; 
        except Exception as ex:
            print(ex) 
        return False

    def is_running(self):
        self.get_portmapping()
        if self.process == None:
            print("Remote Session is Empty")
            return False
        if self.process.poll() != None:
            print("Exiting Remote Session")
            self.process = None
            return False
        print("Remote Session is Running")
        return True

    def stop_session(self):
        if self.process != None:
            print("Terminating Remote Session")
            self.process.terminate()
            self.process = None

    def get_portsegment(self):
        if self.process != None:
            return self.port_segment
        else:
            return -1

    def get_portmapping(self):
        try:
            process = None
            ssh_key_file = self.ssh_key_file
            ssh_user = self.ssh_user
            ssh_host = self.ssh_host
            env = os.environ.copy()
            cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i "+ssh_key_file+" "+ssh_user+"@"+ssh_host+" netstat -an | grep -E '^tcp.*0.*0.*127.0.0.1:[[:digit:]]{3}\[22\|80\|72\|75\].*LISTEN.*$'"
            args = shlex.split(cmd)
            process = subprocess.Popen(args,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (output, err) = process.communicate()
            output = output.decode('utf-8')
            print(output)
            segments = []
            for line in output.split('\n'):
                if line != '':
                    parts = line.split()
                    segment = parts[3].split(':')[1][:3]
                    if not(segment in segments):
                        segments.append(parts[3].split(':')[1][:3])
            print("Port Segments Found")
            print(segments)
            return segments
        except Exception as ex:
            print(ex)
            if process != None:
                process.terminate()
            return []

    def create_session(self):
        try:
            existing_segments = self.get_portmapping()
            base_segment = 100;
            ceil_segment = 200;
            while base_segment < ceil_segment:
                if str(base_segment) in existing_segments:
                    base_segment = base_segment + 1
                else:
                    break
            # port_segment = self.port_segment
            self.port_segment = base_segment*100
            port_segment = self.port_segment
            print("Using Port Segment: {}".format(self.port_segment))
            ssh_key_file = self.ssh_key_file
            ssh_user = self.ssh_user
            ssh_host = self.ssh_host
            env = os.environ.copy()
            env['AUTOSSH_MAXSTART'] = "2"
            port_ssh = int(port_segment)+22
            port_web = int(port_segment)+80
            port_rmq = int(port_segment)+72
            port_mqtt = int(port_segment)+75
            port_mapping = "-R 0.0.0.0:{}:localhost:22 -R 0.0.0.0:{}:localhost:8080 -R 0.0.0.0:{}:localhost:15672 -R 0.0.0.0:{}:localhost:15675".format(port_ssh,port_web,port_rmq,port_mqtt)
            cmd = "/usr/bin/autossh -M 0 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -o ConnectTimeout=30 -N "+port_mapping+" -i "+ssh_key_file+" "+ssh_user+"@"+ssh_host
            print(cmd)
            args = shlex.split(cmd)
            self.process = subprocess.Popen(args,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            print("Created Remote Session: {}".format(self.process.pid))
            return 0
        except Exception as ex:
            print(ex)
            if self.process != None:
                self.process.terminate()
            return -1

def main():
    rst = RemoteSessionTunnel();
    if rst.create_session() == 0:
        print("ok");
        time.sleep(60);
        print("ok");
        rst.stop_session()

if __name__ == '__main__':
    main()

#!/bin/sh

F1SIM_HOME=$(dirname $0 | xargs -I {} realpath {} | rev | cut -d '/' -f 2- | rev)

print_usage()
{
    echo ""
    echo " setup_security.sh [-d SSH_DIR] [-u ADMIN_USER] [-p ADMIN_PASS] [-h]"
    echo ""
    echo " -d: where the ssh-keys are stored"
    echo " -u: admin username"
    echo " -p: admin password"
    echo " -h: this help"
    echo ""
}

while getopts 'd:u:p:fh' flag; do
  case "${flag}" in
    d) SSH_DIR="${OPTARG}" ;;
    u) ADMIN_USER="${OPTARG}" ;;
    p) ADMIN_PASS="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

if [ "${ADMIN_USER}" = "" ]
then
    read -p "Web Admin User (use email address - eg. admin@withoracle.cloud): " ADMIN_USER
fi

if [ "${ADMIN_PASS}" = "" ]
then
    stty -echo
    printf "Web Admin Password: "
    read ADMIN_PASS
    stty echo
    printf "\n"
fi
if [ -z "$SSH_DIR" ] 
then
    read -p "SSH Key Director: " SSH_DIR
fi

SSH_DIR=$(realpath $SSH_DIR)
mkdir -p $SSH_DIR

ssh-keygen -C "f1sim-pi-key" -N ""  -f $SSH_DIR/f1sim-pi-key

cd $F1SIM_HOME
. dev/bin/activate
. $F1SIM_HOME/f1env.sh

export FLASK_APP="$F1SIM_HOME/web/user_admin.py"
flask create --username "${ADMIN_USER}" --email "${ADMIN_USER}" --password "${ADMIN_PASS}"

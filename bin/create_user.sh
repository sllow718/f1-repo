#!/bin/sh

F1SIM_HOME=$(dirname $0 | xargs -I {} realpath {} | rev | cut -d '/' -f 2- | rev)

print_usage()
{
    echo ""
    echo " create_user.sh [-u USER] [-p PASS] [-h]"
    echo ""
    echo " -u: username"
    echo " -p: password"
    echo " -h: this help"
    echo ""
}

while getopts 'u:p:fh' flag; do
  case "${flag}" in
    u) WEB_USER="${OPTARG}" ;;
    p) WEB_PASS="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

if [ "${WEB_USER}" = "" ]
then
    read -p "Web User (Email eg. admin@withoracle.cloud): " WEB_USER
fi

if [ "${WEB_PASS}" = "" ]
then
    stty -echo
    printf "Web Password: "
    read WEB_PASS
    stty echo
    printf "\n"
fi

cd $F1SIM_HOME
. dev/bin/activate
. $F1SIM_HOME/f1env.sh

export FLASK_APP="$F1SIM_HOME/web/user_admin.py"
flask create --username "${WEB_USER}" --email "${WEB_USER}" --password "${WEB_PASS}"

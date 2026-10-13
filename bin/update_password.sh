#!/bin/sh

F1SIM_HOME=$(dirname $0 | xargs -I {} realpath {} | rev | cut -d '/' -f 2- | rev)

print_usage()
{
    echo ""
    echo " update_password.sh [-u ADMIN_USER] [-p ADMIN_PASS] [-h]"
    echo ""
    echo " -u: admin username"
    echo " -p: admin password"
    echo " -h: this help"
    echo ""
}

while getopts 'u:p:fh' flag; do
  case "${flag}" in
    u) ADMIN_USER="${OPTARG}" ;;
    p) ADMIN_PASS="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

if [ "${ADMIN_USER}" = "" ]
then
    read -p "Web Admin User: " ADMIN_USER
fi

if [ "${ADMIN_PASS}" = "" ]
then
    stty -echo
    printf "Web Admin Password: "
    read ADMIN_PASS
    stty echo
    printf "\n"
fi

cd $F1SIM_HOME
. dev/bin/activate
. $F1SIM_HOME/f1env.sh

export FLASK_APP="$F1SIM_HOME/web/user_admin.py"
flask alter --username "${ADMIN_USER}" --password "${ADMIN_PASS}"

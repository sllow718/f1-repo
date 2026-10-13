#!/bin/sh

F1SIM_HOME=$(dirname $0 | xargs -I {} realpath {} | rev | cut -d '/' -f 2- | rev)

print_usage()
{
    echo ""
    echo " delete_user.sh [-u ADMIN_USER] [-h]"
    echo ""
    echo " -u: admin username"
    echo " -h: this help"
    echo ""
}

while getopts 'd:u:p:fh' flag; do
  case "${flag}" in
    u) ADMIN_USER="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

if [ "${ADMIN_USER}" = "" ]
then
    read -p "Web Admin User: " ADMIN_USER
fi

cd $F1SIM_HOME
. dev/bin/activate
. $F1SIM_HOME/f1env.sh

export FLASK_APP="$F1SIM_HOME/web/user_admin.py"
flask drop --username "${ADMIN_USER}"

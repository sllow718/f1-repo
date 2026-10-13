#!/bin/sh

KERNEL=`uname -s`
MACHINE=`uname -m`
APT_ENABLED=`apt --version`
YUM_ENABLED=`yum --version`

echo "Installing for $KERNEL $MACHINE"
RMQ_INSTALLED=0
if [ "$KERNEL" = "Linux" ]
then
    if [ "$MACHINE" = "aarch64" ]
    then
        if [ "${APT_ENABLED}" != "" ]
        then 
            echo "Installing rabbitmq-server with apt-get repo"
            sudo apt-get install rabbitmq-server
            sudo systemctl enable rabbitmq-server
            sudo systemctl start rabbitmq-server
            RMQ_INSTALLED=1
        fi
    elif [ "$MACHINE" = "x86_64" ]
    then
        if [ "${APT_ENABLED}" != "" ]
        then 
            echo "Installing rabbitmq-server with PackageCloud repo"
            sudo apt-get install curl gnupg apt-transport-https -y

            ## Team RabbitMQ's main signing key
            curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null
            ## Launchpad PPA that provides modern Erlang releases
            curl -1sLf "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xf77f1eda57ebb1cc" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg > /dev/null
            ## PackageCloud RabbitMQ repository
            curl -1sLf "https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.packagecloud.rabbitmq.gpg > /dev/null

            ## Add apt repositories maintained by Team RabbitMQ
            sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF
## Provides modern Erlang/OTP releases
##
## "bionic" as distribution name should work for any reasonably recent Ubuntu or Debian release.
## See the release to distribution mapping table in RabbitMQ doc guides to learn more.
deb [signed-by=/usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg] http://ppa.launchpad.net/rabbitmq/rabbitmq-erlang/ubuntu bionic main
deb-src [signed-by=/usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg] http://ppa.launchpad.net/rabbitmq/rabbitmq-erlang/ubuntu bionic main

## Provides RabbitMQ
##
## "bionic" as distribution name should work for any reasonably recent Ubuntu or Debian release.
## See the release to distribution mapping table in RabbitMQ doc guides to learn more.
deb [signed-by=/usr/share/keyrings/io.packagecloud.rabbitmq.gpg] https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ bionic main
deb-src [signed-by=/usr/share/keyrings/io.packagecloud.rabbitmq.gpg] https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ bionic main
EOF

            ## Update package indices
            sudo apt-get update -y

            ## Install Erlang packages
            sudo apt-get install -y erlang-base \
              erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
              erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
              erlang-runtime-tools erlang-snmp erlang-ssl \
              erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

            ## Install rabbitmq-server and its dependencies
            sudo apt-get install rabbitmq-server -y --fix-missing
            RMQ_INSTALLED=1
        # Assumes OL8
        elif [ "${YUM_ENABLED}" != "" ]
        then 
            echo "Installing rabbitmq-server with manual RPM install"
            mkdir $HOME/Downloads
            wget -P $HOME/Downloads https://github.com/rabbitmq/erlang-rpm/releases/download/v25.1.2/erlang-25.1.2-1.el8.x86_64.rpm
            wget -P $HOME/Downloads https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.11.3/rabbitmq-server-3.11.3-1.el8.noarch.rpm
            sudo yum install -y socat logrotate
            sudo yum install -y $HOME/Downloads/erlang-25.1.2-1.el8.x86_64.rpm
            sudo yum install -y $HOME/Downloads/rabbitmq-server-3.11.3-1.el8.noarch.rpm
            sudo chkconfig rabbitmq-server on
            sudo systemctl daemon-reload
            sudo systemctl start rabbitmq-server.service
            RMQ_INSTALLED=1
        fi
    fi
fi
if [ $RMQ_INSTALLED = 0 ]
then
    echo "Install rabbitmq manually if supported by platform"
    exit 1
fi

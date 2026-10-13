# Get Started

⚠️ This README is a more detailed version in case you would like to tinker around.
## What you'll need

- Autonomous Database provisioned and associated wallet file
- Oracle Instant Client installation
- Python 3+ (Tested with Python 3.8)
- Raspberry Pi 3/4/400 with Raspbian 64bits flashed on a 32Gb micro-sd card

**Important:** If you decide to use an other OS for your RaspberryPi, ensure it has APT as package manager!

## Python Dependencies

- pika
- PyYAML
- f1-telemetry-2021
- cx_Oracle

## Installation steps

### Preparations

1. Download Oracle Instant Client (and unzip) - includes basic and sqlplus (eg _/opt/oracle_)  
  - [https://www.oracle.com/database/technologies/instant-client/downloads.html](https://www.oracle.com/database/technologies/instant-client/downloads.html)
    - For Linux x64-bit
    - _unzip instantclient-basic-linux.x64-21.6.0.0.0dbru.zip -d /opt/oracle_
    - _unzip instantclient-sqlplus-linux.x64-21.6.0.0.0dbru.zip -d /opt/oracle_
    - For Linux Arm x64-bit
    - _unzip instantclient-basic-linux.arm64-19.10.0.0.0dbru.zip -d /opt/oracle_
    - _unzip instantclient-sqlplus-linux.arm64-19.10.0.0.0dbru.zip -d /opt/oracle_
2. Download wallet (and unzip) (eg _Wallet_ATP.zip_)
  - (Preferred) Unzip the files into the Oracle Instant Client directory in the $ORACLE_HOME/network/admin directory
    - _unzip Wallet_ATP.zip -d /opt/oracle/instantclient_21_6/network/admin_
  - (Alternatively) Unzip the files in its own directory and symlink (cwallet.so, sqlnet.ora and tnsnames.ora) into the $ORACLE_HOME/network/admin directory
    - _unzip Wallet_ATP.zip -d /home/oracle/wallet_
    - _cd /opt/oracle/instantclient_21_6/network/admin_
    - _ln -s /home/oracle/wallet/cwallet.sso_
    - _ln -s /home/oracle/wallet/sqlnet.ora_
    - _ln -s /home/oracle/wallet/tnsnames.ora_
  - (Second Alternative) OR specify the TNS_ADMIN environment variable with the wallet directory (and update the sqlnet.ora accordingly as well)
    - _unzip Wallet_ATP.zip -d /home/oracle/wallet_
    - _export TNS_ADMIN=/home/oracle/wallet_
    - _sed  -i 's/\?\/network\/admin/\/home\/oracle\/wallet/' /home/oracle/wallet/sqlnet.ora_
3. Copy f1env.sh.template as f1env.sh
4. Update f1env.sh (with Oracle Instant Client installation details)
  - Define a unique game_host (this is the name of your instance or event - eg. F1SIM_WELCOME)
  - Set $ORACLE_HOME as the Oracle Instant Client directory (eg _/opt/oracle/instantclient_21_6_)
5. Copy f1store.yaml.template as f1store.yaml
6. Update f1store.yaml (with Autonomous Database details)
  - Configure _store_ parameter to how you want to process / save the data
    - Set _store: none_ to log the capture
    - Set _store: oracledb_ to save the packet in an Autonomous Database
    - IF _store: oracledb_, set _dbusername_ as your username
    - IF _store: oracledb_, set _dbpassword_ as your password
    - IF _store: oracledb_, set _dburl_ as your TNS_PROFILE name from your wallet)
    - IF _store: oracledb_, set _dbpoolsize_ depending on your resource requirements (higher framerate may require more connections)
    - Set _store: pickle_ to save the packet in a local directory as individual pickle files
    - IF _store: pickle_, set _filedir_ as your directory where the files are save (needs to be created)
7. Set a virtual environment (eg _dev_)
  - _python3 -m venv dev_
  - _source dev/bin/activate_
8. Install Dependencies
  - _pip3 install -r requirements.txt_

### Listener setup

To Run (Listener / RabbitMQ Producer) - this will start a UDP listener and store the data in RabbitMQ
1. _python3 -m venv dev_
1. _source f1env.sh_
2. _python3 src/main.py produce_

To Run (RabbitMQ Consumer / PacketWriter) - this will start a RabbitMQ consumer and save data
1. _python3 -m venv dev_
1. _source f1env.sh_
2. _python3 src/main.py consume_

### Dispatcher setup
To Run (Test "Replay") - this will start a UDP dispatcher using the test data saved using _store: pickle_ (eg _/home/oracle/test/data_)
1. _python3 -m venv dev_
1. _source f1env.sh_
2. _python3 test/main.py /home/oracle/test/data_

## Additional Notes
- Logging is directed to stdout. Modify the f1log.yaml to change the log handlers and log levels.
- Different configurations for packet writers is available
  - store (either none, pickle, oracledb) enables the data to be stored in different locations
  - filter (either true or false) enables the data to be filtered (if _store: oracledb_)
  - save (either true or false) enables the data to be saved or not
  - properties (for each of the stores) sets the required parameters accordingly
- If you are using the _store: oracledb_ option, then it will configure a session pool, you can specify the poolsize. Be aware of the performance (ie a higher frame rate may require a higher poolsize).

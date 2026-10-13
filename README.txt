Get Started
===========

## What you'll need

- Autonomous Database provisioned and associated wallet zip file
- Python 3+ (Tested with Python 3.8)
- Raspberry Pi 3/4/400 with Raspbian 64bits flashed on a 32Gb micro-sd card

## Installation steps
Steps
1. Create a directory f1-simulator (referred to F1SIM_HOME) and unzip f1-simulator.zip
2. Download wallet (eg _Wallet_ATP.zip_) and copy wallet zip file into $F1SIM_HOME
3. Run $F1SIM_HOME/bin/install_pi.sh
4. Copy $F1SIM_HOME/f1store.yaml.template as $F1SIM_HOME/f1store.yaml
5. Update f1store.yaml (with Autonomous Database details)
  - Configure _gamehost_ parameter to your event or permanent host (used as part of the APEX Event Manager and Leaderboard)
  - Configure _device_ parameter to your device name (used as part of the APEX Event Manager and Leaderboard)
  - Configure _store_ parameter to how you want to process / save the data
    - Set _store: none_ to log the capture
    - Set _store: oracledb_ to save the packet in an Autonomous Database
    - For _oracledb_, set _dbusername_ as your username
    - For _oracledb_, set _dbpassword_ as your password
    - For _oracledb_, set _dburl_ as your TNS_PROFILE name from your wallet)
    - For _oracledb_, set _poolsize_ depending on your resource requirements (higher framerate may require more connections)
    - Set _store: pickle_ to save the packet in a local directory as individual pickle files
    - For _pickle_, set _filedir_ as your directory where the files are save (needs to be created)
    - Set _store: rabbitmq_ to save the packet in rabbitmq (default to localhost)
    - For _rabbitmq, set _host_ as host where rabbitmq is running
    - For _rabbitmq, set _rmqusername_ as your username
    - For _rabbitmq, set _rmqpassword_ as your password
  - If Store And Forward is preferred
    - Set _store: rabbitmq_ to store the packets
    - Set _forward: [oracledb | pickle | none]_ to forward the packets (to Autonomous Database, Pickle file or none)

### Preparations
To Run (Listener / PacketWriter) - this will start a UDP listener and save data
1. _sudo systemctl start f1sim-producer_

To Run (RabbitMQ Consumer / PacketWriter) - this will start a Rabbit MQ consumer and save data
1. _sudo systemctl start f1sim-consumer_

To Run (Web Server) - this will start a flask-based web application to support the running of the F1 Simulator
1. _sudo systemctl start f1sim-webserver_

To Monitor / Manage RabbitMQ (eg _assuming on the pi_)
1. _sudo rabbitmqctl list_queues_ to see how many messages on the _PacketData_ queue
2. _sudo rabbitmqctl purge_queue PacketData_ to delete messages on the _PacketData_ queue
OR
1. Connect to http://localhost:15672 (or remotely via the Pi's IP address)
2. Use your RMQ username / password to log into the management console

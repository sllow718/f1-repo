# Get Started

If you are looking to run the f1-simulator, please refer to README.txt. These instructions are more for developers and contributors to the project.

## What you'll need

- Autonomous Database provisioned and associated wallet file
- Python 3+ (Tested with Python 3.8)
- Raspberry Pi 3/4/400 with Raspbian 64bits flashed on a 32Gb micro-sd card
- RabbitMQ (if Store And Forward is preferred)
- Linux-based (as the scripts have been run with Ubuntu / Oracle Linux)
- Tested on arm64 and x86-64 (with Ubuntu and apt) and x86-64 (with Oracle Linux 8 and yum)

## Python Dependencies

- pika (if rabbitmq is used)
- PyYAML
- oracledb
- flask

## Installation steps
Steps
1. Download wallet (and unzip) (eg _Wallet_ATP.zip_)
  - Specify the wallet directory from the f1store.yaml
    - _unzip Wallet_ATP.zip -d /home/oracle/wallet_
3. Copy f1env.sh.template as f1env.sh
4. Update f1env.sh
  - Set $F1SIM_HOME of the f1-simulator directory
1. Install and configure RabbitMQ (if Store And Forward is preferred)
  - Install RabbitMQ (if on Ubuntu)
    - _sudo apt-get install rabbitmq-server_
    - _sudo systemctl enable rabbitmq-server_
    - _sudo systemctl start rabbitmq-server_
  - Install RabbitMQ (if on Oracle Linux)
    - @TODO - Find the erlang EL8 rpm and rabbitmq noarch rpm and install
  - Configure RabbitMQ
    - @TODO - Install MQTT, Management Console
    - @TODO - Configure PacketData queue
    - @TODO - Configure admin user (for remote access and MQTT)
5. Copy f1store.yaml.template as f1store.yaml
. Update f1store.yaml (with Autonomous Database details)
  - Configure _store_ parameter to how you want to process / save the data
    - Set _store: none_ to log the capture
    - Set _store: oracledb_ to save the packet in an Autonomous Database
    - For _oracledb_, set _dbusername_ as your username
    - For _oracledb_, set _dbpassword_ as your password
    - For _oracledb_, set _dbwalletdir_ as for your wallet directory
    - For _oracledb_, set _dbwalletpassword_ as for your wallet password
    - For _oracledb_, set _dburl_ as your TNS_PROFILE name from your wallet)
    - For _oracledb_, set _poolsize_ depending on your resource requirements (higher framerate may require more connections)
    - Set _store: pickle_ to save the packet in a local directory as individual pickle files
    - For _pickle_, set _filedir_ as your directory where the files are save (needs to be created)
    - Set _store: rabbitmq_ to save the packet in rabbitmq (default to localhost)
    - For _rabbitmq, set _host_ as host where rabbitmq is running
  - If Store And Forward is preferred
    - Set _store: rabbitmq_ to store the packets
    - Set _forward: [oracledb | pickle | none]_ to forward the packets (to Autonomous Database, Pickle file or none)
7. Set a virtual environment (eg _dev_)
  - _python3 -m venv dev_
  - _source dev/bin/activate_
8. Install Dependencies
  - _pip3 install -r requirements.txt_

### Preparations
To Run (Listener / PacketWriter) - this will start a UDP listener and save data
1. _source f1env.sh_
2. _python3 src/main.py produce_

To Run (RabbitMQ Consumer / PacketWriter) - this will start a Rabbit MQ consumer and save data
1. _source f1env.sh_
2. _python3 src/main.py consume_ 

To Monitor / Manage RabbitMQ (eg _assuming on the pi_)
1. _sudo rabbitmqctl list_queues_ to see how many messages on the _PacketData_ queue
2. _sudo rabbitmqctl purge_queue PacketData_ to delete messages on the _PacketData_ queue

Start by cloning the git repository with your prefered method, HTTPS or SSH. Then checkout the rabbitmq branch

```
git clone <f1-simulator.git>
```

```
cd f1-simulator
```

Download your ATP Wallet .zip file on your Raspberry Pi. Use your preferred method, wget or sftp.

```
bin/download_rabbitmq.sh
```

Before moving futher, we need to setup our environment. Run the setup script with the following command. Ensure to update `pi` with your username.

```
bin/setup_env.sh
```

We're going to connect your environment with the ATP. Run the following script, it will ask for **Wallet (ZIP) File**, which is the .zip file location, ie `/home/pi/Wallet_fortatp.zip`. **Wallet Install Directory**, is the location where the wallet directory "Wallet_XXX" should be created, we recommend to use "`.`" here.

```
bin/setup_wallet.sh
```

Last script to run, is the service configuration. By running the following command, it will ask you **F1Sim Root Directory**, which is the f1-simulator directory itself, ie `/home/pi/f1-simulator`. Ensure to update `pi` with your username.

```
bin/setup_service.sh
```

After the service has been setup. Copy `f1store.yaml.template` as `f1store.yaml`. Then update the copied version with your Autonomous Database details.

```
cp f1store.yaml.template f1store.yaml
```

- Add a game `GAMEHOST` information and `DEVICE` name

- Configure `store` parameter to how you want to process / save the data
  - Set `store: none` to log the capture
  - Set `store: oracledb` to save the packet in an Autonomous Database
    - **If** `store: oracledb`, set `dbusername` as your *username*
    - **If** `store: oracledb`, set `dbpassword` as your *password*
    - **If** `store: oracledb`, set `dbwalletdir` as your *wallet directory*
    - **If** `store: oracledb`, set `dbwalletpassword` as your *wallet password*
    - **If** `store: oracledb`, set `dburl` as your `TNS_PROFILE` name from your wallet (use low profile)
    - **If** `store: oracledb`, set `dbpoolsize` depending on your resource requirements (higher framerate may require more connections)
  - Set `store: pickle` to save the packet in a local directory as individual pickle files
    - **If** `store: pickle`, set _filedir_ as your directory where the files are save (needs to be created)

Last step here will be to run the service setup script. It will ask for the **F1Sim Root Directory**, which is the f1-simulator directory, ie `/home/pi/f1-simulator`. 

### Start the engine 🏎️

Now it's time to start the engine, to do so, you just need to run the following script.

```
bin/start.sh
```

If you want to stop, then run the stop script.

```
bin/stop.sh
```

### Managing the services

The producer and consumer is independently manageable through `systemctl`. Run the following commands to do so.

```
sudo systemctl start|status|restart|stop f1sim-consumer
sudo systemctl start|status|restart|stop f1sim-producer
```

### Managing RabbitMQ (assuming you're using a Raspberry Pi)

The RabbitMQ server is independently manageable through `systemctl`. Run the following commands to do so.

```
sudo systemctl start|status|restart|stop rabbitmq-server
```

To see how many messages are currently in the RabbitMQ *PacketData* queue.

```
sudo rabbitmqctl list_queues
```

To delete messages in the RabbitMQ *PacketData* queue.

```
sudo rabbitmqctl purge_queue PacketData
```

## Additional Notes
- Logging is directed to stdout. Modify the f1log.yaml to change the log handlers and log levels.
- Different configurations for packet writers is available
  - store (either none, pickle, oracledb, rabbitmq) enables the data to be stored in different locations
  - forward (either none, pickle, oracledb) enables the data to be stored in rabbitmq and forwarded in different locations
  - filter (either true or false) enables the data to be filtered (if _store: oracledb_)
  - save (either true or false) enables the data to be saved or not
  - properties (for each of the stores) sets the required parameters accordingly
- If you are using the _store: oracledb_ option, then it will configure a session pool, you can specify the poolsize. Be aware of the performance (ie a higher frame rate may require a higher poolsize).

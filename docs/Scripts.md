# Installation & Management Scripts (WiP)

Intallation and management scripts are accessible through : `/f1-simulator/bin/`.

**Important**: When running the scripts, make sure you're executing them from the `f1-simulator` folder.

## download_instantclient.sh

This script takes care of downloading the correct version of Oracle Instant Client and SQL*Plus. It will first ask a **Download Location** and then the **Instant Client Location**. We recommend to input "`.`" for both, so the installation takes place in the `f1-simulator` folder. The script will automatically detect if your runnning a 64bits or ARM system and will download the compatible version.

The packages are downloaded from the official Oracle download page, accessible through [here](https://www.oracle.com/database/technologies/instant-client/downloads.html)

**Script arguments**

```
download_instantclient.sh [-d DOWNLOAD_DIR] [-i IC_DIR] [-f] [-h]

-d: where the Instant Client ZIP files are downloaded
-i: where the Instant Client is unzipped (the instantclient_??_?? directory will be created in this directory
-f: force
-h: show this current help page
```

## download_rabbitmq.sh

**Important**:

This script is responsible to download `rabbitmq-server` package through the APT package manager. If you're running an machine that's not ARM, you will need install rabbitmq manually, if your platform is supported. 

Refer to the download & installation [page](https://www.rabbitmq.com/download.html) of RabbitMQ itself, and find your appropriate method.

## run_consummer.sh

lorem ipsum

## run_producer.sh

lorem ipsum

## setup_env.sh


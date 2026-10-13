import oracledb
import time
import sys
import os
import yaml
import logging
import logging.config
from pathlib import Path
from f1sim import PacketWriter

home = str(Path.home())

class OracleDatabaseConnection(PacketWriter):

    def is_local_threaded(self):
        return false

    def connect(self):
        if self.dbmode == "thin":
            self.pool = oracledb.create_pool(user=self.dbusername, password=self.dbpassword, dsn=self.dburl, min=1, max=self.poolsize, increment=1, threaded=True, config_dir=self.dbwalletdir, wallet_location=self.dbwalletdir, wallet_password=self.dbwalletpassword, expire_time=2)
        else:
            self.pool = oracledb.create_pool(user=self.dbusername, password=self.dbpassword, dsn=self.dburl, min=1, max=self.poolsize, increment=1, threaded=True, expire_time=2)
        self.pool.ping_interval=60
        self.pool.timeout=300
        logging.info('Connection successful.')

    def __init__(self, parameters):
        self.dbmode = parameters['dbmode']
        self.dbusername = parameters['dbusername']
        self.dbpassword = parameters['dbpassword']
        self.poolsize = parameters['poolsize']
        self.dburl = parameters['dburl']
        self.level = parameters['level']
        self.logging = logging;
        logging.debug(self.dburl)
        logging.debug(self.dbusername)
        logging.debug(self.dbpassword)
        logging.debug(self.poolsize)
        if self.dbmode == "thin":
            self.dbwalletdir = parameters['dbwalletdir']
            self.dbwalletpassword = parameters['dbwalletpassword']
            logging.debug(self.dbwalletdir)
            logging.debug(self.dbwalletpassword)
        else:
            oracledb.init_oracle_client()
        self.connect();

    def close_pool(self):
        self.pool.close()
        logging.info('Connection pool closed.')

    def test(self):
        connection = None
        retry = 6
        while retry > 0:
            try:
                connection = self.pool.acquire()
                connection.autocommit = True
                cursor = oracledb.Cursor(connection)
                # cursor.execute(location,parameters);
                for row in cursor.execute("select * from \"F1SIM_DEVICE\" order by M_TIMESTAMP"):
                    print(row)
                return 1
            except Exception as ex:
                self.logging.error(ex)
                retry = retry - 1
                if retry % 3 == 0:
                    self.connect();  
            finally:
                if connection != None:
                    self.pool.release(connection)
        self.logging.error("retries failed")

    def insert(self, location, parameters):
        if (self.level == 'laptime') and not(('LAPTIME' in location) or ('SESSION' in location)):
            self.logging.debug("Record Filtered")
            return -1
        connection = None
        retry = 6
        while retry > 0:
            try:
                connection = self.pool.acquire()
                connection.autocommit = True
                cursor = oracledb.Cursor(connection)
                cursor.execute(location,parameters);
                if ('DEVICE' in location):
                    self.logging.info("Consumer Heartbeat Record Inserted")
                    self.logging.info("Conn.Pool.Params:{}:{}:{}".format(self.pool.min,self.pool.max,self.pool.opened))
                self.logging.debug("Consumer Record Inserted")
                return 1
            except Exception as ex:
                self.logging.error(ex)
                retry = retry - 1
                if retry % 3 == 0:
                    self.connect();  
            finally:
                if connection != None:
                    self.pool.release(connection)
        self.logging.error("Consumer Retries Failed")
        return 0

def test_class():
    with open('f1log.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    parameters = { "dbusername" : "username", "dbpassword" : "password", "dburl" : "adb_low", "dbwalletdir" : "/home/pi/f1-simulator/wallet", "dbwalletpassword" : "wallet", "poolsize" : 10, "level" : "all" };
    object = OracleDatabaseConnection(parameters)
    logging.info(object.pool)
    while True:
        object.test();
        time.sleep(1);
    object.close_pool()

if __name__ == '__main__':
    test_class()

import json,os,sys

import pymongo
from application import mongo_conn_string
from application.common.loggerfile import my_logger
from application.config.config_file import kafka_bootstrap_server
from kafka import KafkaConsumer


def filebrowsestatus():
    try:
        consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server)
        consumer.subscribe(pattern='filestatus*')
        for message in consumer:
            hdfspath = message.value

            data = hdfspath.replace("'", '"')

            message = json.loads(data)

            result = message["result"]
            filesinpath = result.decode('base64', 'strict')
            filename = message["filename"]
            clusterid = message['clusterid']
            customerid = message['customerid']
            timestamp = message['timestamp']

            filestatus = {}
            filestatus['clusterid'] = clusterid
            filestatus['customerid'] = customerid
            filestatus['filename'] = filename
            filestatus['filesinpath'] = filesinpath
            filestatus['timestamp'] = timestamp
            mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
            database_conn = mongo_db_conn['haas']
            db_collection = database_conn['filebrowsingstatus']
            result = db_collection.insert_one(filestatus)
            print 'done with mongo'
    except pymongo.errors.ConnectionFailure, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
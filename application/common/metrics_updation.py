import os

import pymongo
import sys
from application import mongo_conn_string
from application.common.loggerfile import  my_logger

def metricSubscriber(data):
    try:
        customerid = data['customer_id']
        # my_logger.info(customerid,data)
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['local']
        db_collection = database_conn[customerid]
        my_logger.info(database_conn)
        result = db_collection.insert_one(data)
        my_logger.info(customerid)
        my_logger.info("data inserted")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
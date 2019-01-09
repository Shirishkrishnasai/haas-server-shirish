import pymongo
from application import mongo_conn_string
from application.common.loggerfile import  my_logger

def metricSubscriber(data):
    try:
        customerid = data['customer_id']
        my_logger.info(customerid)
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['local']
        db_collection = database_conn[customerid]

        result = db_collection.insert_one(data)

    except pymongo.errors.ConnectionFailure, e:
        my_logger.debug(e)
        #return jsonify(message='unable to connect mongo')

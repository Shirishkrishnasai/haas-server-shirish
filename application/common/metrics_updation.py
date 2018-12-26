import pymongo
from application import mongo_conn_string
def metricSubscriber(data):
    try:
        customerid = data['customer_id']
        print customerid
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['local']
        db_collection = database_conn[customerid]

        result = db_collection.insert_one(data)
        #print result
        # query_statement= database_conn.find(dat
        # object_id=query_statement[0]["_id"]
        # print object_id

    except pymongo.errors.ConnectionFailure, e:
        my_logger.debug(e)
        return jsonify(message='unable to connect mongo')

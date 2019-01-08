from application.common.loggerfile import my_logger

"""

"""


def hiveDatabaseResult():
    my_logger.info("Nothing to Do here")

    #
    # while True:
    #
    #     try:
    #         print "in hive database result consumer"
    #         consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server)
    #         consumer.subscribe(pattern='hivedatabaseresult*')
    #         print "subscribed to topic"
    #         for message in consumer:
    #             print "in for loop-------------database result consumer"
    #             hivedatabaseresult = message.value
    #             print type(hivedatabaseresult)
    #             data = hivedatabaseresult.replace("'", '"')
    #             print data,'dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    #             message = json.loads(data)
    #             print message ,type(message) ,'message',message.keys()
    #
    #             filesinpath=result.decode('base64','strict')
    #             mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
    #             database_conn = mongo_db_conn['haas']
    #             db_collection = database_conn['hive_database']
    #             db_collection.save()
    #             print 'done with mongo'
    #     except pymongo.errors.ConnectionFailure, e:
    #
    #         my_logger.debug(e)
    #
    #
    #

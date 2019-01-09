from application.common.loggerfile import my_logger

"""

"""


def hiveDatabaseResult():
    my_logger.info("Nothing to Do here")

    #
    # while True:
    #
    #     try:
    #         my_logger.info("in hive database result consumer")
    #         consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server)
    #         consumer.subscribe(pattern='hivedatabaseresult*')
    #         my_logger.info("subscribed to topic")
    #         for message in consumer:
    #             my_logger.info("in for loop-------------database result consumer")
    #             hivedatabaseresult = message.value
    #             my_logger.info(type(hivedatabaseresult))
    #             data = hivedatabaseresult.replace("'", '"')
    #             my_logger.info(data)
    #             message = json.loads(data)
    #             my_logger.info(message )
    #             my_logger.info(type(message))
    #
    #             filesinpath=result.decode('base64','strict')
    #             mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
    #             database_conn = mongo_db_conn['haas']
    #             db_collection = database_conn['hive_database']
    #             db_collection.save()
    #             my_logger.info('done with mongo')
    #     except pymongo.errors.ConnectionFailure, e:
    #
    #         my_logger.debug(e)
    #
    #
    #

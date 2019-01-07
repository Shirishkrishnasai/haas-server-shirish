from application.common.loggerfile import my_logger


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
    #
    #             message = json.loads(data)
    #             print message ,type(message) ,'message',message.keys()
    #
    #
    #
    #     except Exception as e:
    #
    #         my_logger.debug(e)
    #
    #
    #

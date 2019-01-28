import os
import sys
import time

from application.common.loggerfile import my_logger
from application.modules.core.api.task_status_updation import taskstatusupdation
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from flask import json
from kafka import KafkaConsumer


def _kafkataskconsumer():
    # Connection to kafka
    consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server, api_version=kafka_api_version)
    consumer.subscribe(pattern='taskstatus*')
    while True:
        # consumer.poll(1000)
        try:
            message = consumer.poll(timeout_ms=1000, max_records=1)
            # print json.dumps(message)
            if message != {}:
                # for message in consumer:
                topicMesages = message.values()
                for messageValues in topicMesages[0]:
                    try:
                        customer_data = messageValues.value
                        data = customer_data.replace("'", '"')
                        json_loads_customer_data = json.loads(data)
                        if json_loads_customer_data['event_type'] == "task_status":
                            taskstatusupdation(task_status_information=json_loads_customer_data)
                        my_logger.info("Updated Status")
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        my_logger.error(exc_type)
                        my_logger.error(fname)
                        my_logger.error(exc_tb.tb_lineno)
                        my_logger.info("Something wrong in kafka")
                my_logger.info("Message processed..")
            else:
                my_logger.info("Didn't get any Message from topic taskstatus*")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
            my_logger.error("Unable to porcess Mesage")
        print "Task Stats consumer ended..."
        time.sleep(2)

def kafkataskconsumer():
    try:
        _kafkataskconsumer()
    except Exception as e:
        my_logger.info("CAlling itself..,kafkataskconsumer")
        kafkataskconsumer()

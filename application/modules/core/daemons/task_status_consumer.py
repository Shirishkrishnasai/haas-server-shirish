import time

from application.common.loggerfile import my_logger
from application.common.task_status_updation import taskstatusconsumer
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from flask import json
from kafka import KafkaConsumer


def kafkataskconsumer():
    # Connection to kafka
    while True:
        consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server, api_version=kafka_api_version)
        consumer.subscribe(pattern='taskstatus*')
        consumer.poll(1000)
        for message in consumer:
            try:
                customer_data = message.value
                data = customer_data.replace("'", '"')
                json_loads_customer_data = json.loads(data)
                if json_loads_customer_data['event_type'] == "task_status":
                    taskstatusconsumer(task_status_information=json_loads_customer_data)

            except Exception as e:
                my_logger.erro(str(e))
                print "Something wrong in kafka"

            time.sleep(0.1)

        print "Task Stats consumer ended..."
    time.sleep(10)

import time

from application.common.metrics_updation import metricSubscriber
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from flask import json
from kafka import KafkaConsumer


def kafkaconsumer():
    # Connection to kafka
    try:
        consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server, api_version=kafka_api_version)
        consumer.subscribe(pattern='metrics*')
        # Reading data from consumer and passing to the function

        for message in consumer:
            # print message
            customer_data = message.value
            # print customer_data
            data = customer_data.replace("'", '"')
            json_loads_customer_data = json.loads(data)
            # print json_loads_customer_data
            if json_loads_customer_data['event_type'] == "metrics":
                metricSubscriber(data=json_loads_customer_data)
            time.sleep(0.1)

        time.sleep(1)
        print "Cling loop"
    except Exception as e:
        return e.message

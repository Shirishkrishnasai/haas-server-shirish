import time
from kafka import KafkaConsumer
from flask import json
# import json
from application.common.task_status_updation import taskstatusconsumer
from application.config.config_file import kafka_bootstrap_server, kafka_api_version


def kafkataskconsumer():
    # Connection to kafka
    print "in task_status"

    # Reading data from consumer and passing to the function

    print "Polling consumer"
    while True:

        consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server, api_version=kafka_api_version)
        consumer.subscribe(pattern='taskstatus*')
        print consumer, "task_status"
        consumer.poll(1000)
        for message in consumer:
            try:
                customer_data = message.value
                print customer_data, "task_status_consumer"
                data = customer_data.replace("'", '"')
                print type(data)
                print data
                json_loads_customer_data = json.loads(data)
                print json_loads_customer_data

                if json_loads_customer_data['event_type'] == "task_status":
                    taskstatusconsumer(task_status_information=json_loads_customer_data)
                    print 'arvindddddddddddddddddddddd', customer_data

                else:
                    print("key error..")
            except:
                print "Something wrong in kafka"
                consumer.poll(1000)
                #break
            time.sleep(3)

        print "Task Stats consumer ended..."
    time.sleep(10)

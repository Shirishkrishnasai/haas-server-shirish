from kafka import KafkaConsumer
from flask import Blueprint
from flask import json
from application.common.task_status_updation import taskstatusconsumer 
kafkaconsume=Blueprint('kafkaconsume',__name__)
@kafkaconsume.route("/kafkaconsume",methods=["GET"])
def kafkaconsumer():

# Connection to kafka
    try:
        consumer = KafkaConsumer(bootstrap_servers = ['192.168.100.146:9092'])
        consumer.subscribe(pattern='taskstatus*')
    
#Reading data from consumer and passing to the function
    
    
        for message in consumer:
            task_status_data=message.value
            task_status_replace=task_status_data.replace("'",'"')
            json_loads_taskstatus_data=json.loads(task_status_replace)
            taskstatusconsumer(task_status_information=json_loads_taskstatus_data)

    except Exception as e:
        return e.message

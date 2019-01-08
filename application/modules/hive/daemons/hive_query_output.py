from apscheduler.schedulers.background import BackgroundScheduler
import yaml
import io
from datetime import datetime
from application.models.models import TblHiveRequest
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.loggerfile import my_logger
from sqlalchemy import and_
import uuid
from datetime import datetime, timedelta
import json
from kafka import KafkaConsumer
from application.config.config_file import kafka_bootstrap_server
import time



def hiveQueryOutput():
    while True:
        #try:
            my_logger.info("in hive query output consumer")
            consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server, group_id='server')
            consumer.poll(timeout_ms = 30000,max_records=None)
            consumer.subscribe(pattern='hivequeryresult*')
            my_logger.info("subscribed to topic" + 'hivequeryresult*')
            consumer.poll(1000)
            for message in consumer:
                hive_query_result = message.value

                data = hive_query_result.replace("'", '"')
                my_logger.info(data)
                message = json.loads(data)
                my_logger.info(message)
                if message.has_key('output'):
                    my_logger.info(message['output'])
                    decoded_output = json.loads(message['output'].decode('base64', 'strict'))

                    my_logger.info(decoded_output)
                    my_logger.info(type(decoded_output))
                    decoded_output = yaml.load(decoded_output)

                    message['output'] = decoded_output

                    my_logger.info(message)
                    my_logger.info(type(message['output']))

                    my_logger.info(message)
                    my_logger.info(type(message))
                    my_logger.info(message.keys())


                    consumer.commit()

                    isexecuted = False
                    my_logger.info("Exiting from Consumer..")
                db_session = scoped_session(session_factory)
                query_output = db_session.query(TblHiveRequest.hive_query_output).filter(TblHiveRequest.uid_hive_request_id == message['hive_request_id'])
                query_output.update({"hive_query_output":str(message)})
                db_session.commit()
                db_session.close()


                isexecuted = False
                my_logger.info("Exiting fom loop")

    time.sleep(10)

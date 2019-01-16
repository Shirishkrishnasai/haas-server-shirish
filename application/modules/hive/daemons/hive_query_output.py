import yaml
from application.models.models import TblHiveRequest
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.loggerfile import my_logger
import json,sys,os
from kafka import KafkaConsumer
from application.config.config_file import kafka_bootstrap_server
import time



def hiveQueryOutput():
    while True:
        try:
            my_logger.info("in hive query output consumer")
            consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server, group_id='server')
            consumer.subscribe(pattern='hivequeryresult*')
            while True:
                message = consumer.poll(timeout_ms=1000, max_records=1)
                if message != {}:
                    topicMesages = message.values()

                    for messageValues in topicMesages[0]:
                        try:


                            hive_query_result = messageValues.value

                            data = hive_query_result.replace("'", '"')
                            my_logger.info(data)
                            message = json.loads(data)
                            my_logger.info(message)
                            if message.has_key('output'):
                                print message['output']
                                decoded_output = json.loads(message['output'].decode('base64', 'strict'))

                                print decoded_output, type(
                                    decoded_output)
                                decoded_output = yaml.load(decoded_output)

                                message['output'] = decoded_output

                                print message, type(message['output'])

                                print message, type(
                                    message), 'message', message.keys()


                                consumer.commit()

                            db_session = scoped_session(session_factory)
                            query_output = db_session.query(TblHiveRequest.hive_query_output).filter(TblHiveRequest.uid_hive_request_id == message['hive_request_id'])
                            query_output.update({"hive_query_output":str(message)})
                            db_session.commit()
                            db_session.close()


                            isexecuted = False
                            my_logger.info("Exiting fom loop")

                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                            my_logger.error(exc_type)
                            my_logger.error(fname)
                            my_logger.error(exc_tb.tb_lineno)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)

    time.sleep(10)

import time
from kafka import KafkaConsumer
from flask import json
from sqlalchemy.orm import scoped_session
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from application.models.models import TblHiveMetaStatus,TblHiveRequest
from application import session_factory
from application.common.loggerfile import my_logger





def kafkaHiveStatusConsumer():
    # Connection to kafka
    my_logger.info("in hive_task_status_consumer")

    # Reading data from consumer
    my_logger.info("Polling consumer")
    while True:
        my_logger.info("its a 'hello' from while loop")

        consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server, api_version=kafka_api_version)
        consumer.subscribe(pattern='hivequerystatus*')
        my_logger.debug(consumer)
        print "its hive query status subsciber ...subscribed"
        consumer.poll(1000)
        print 'polling over'
        for message in consumer:
            try:
                print "in hive query consumer try block"
                query_status_data = message.value
                my_logger.debug(query_status_data)
                data = query_status_data.replace("'", '"')

                my_logger.debug(data)
                json_loads_query_status_data = json.loads(data)
                my_logger.info("showing json data")
                my_logger.debug(json_loads_query_status_data)

                if json_loads_query_status_data['event_type'] == "query_status":

                    my_logger.info("all conditions checked, connecting to database")
                    db_session = scoped_session(session_factory)
                    hive_meta_status_values = db_session.query(TblHiveMetaStatus.var_status,
                                                               TblHiveMetaStatus.srl_id).all()
                    hive_meta_status_values_dict = dict(hive_meta_status_values)
                    hive_query_status_insert_values = TblHiveRequest(uid_hive_request_id=json_loads_query_status_data['hive_request_id'],
                                                                     uid_agent_id=json_loads_query_status_data['agent_id'],
                                                                     uid_cluster_id=json_loads_query_status_data['cluster_id'],
                                                                     int_query_status=hive_meta_status_values_dict[json_loads_query_status_data['hive_query_status']],
                                                                     ts_status_time=json_loads_query_status_data['status_time'])
                    db_session.add(hive_query_status_insert_values)
                    db_session.commit()
                    db_session.close()
                    my_logger.info("committing done to database and session closed")

                else:
                    my_logger.info("key error..")

            except Exception as e:
                my_logger.error(e)
                my_logger.info("Something wrong in kafka")
                consumer.poll(1000)
                #break
            time.sleep(3)

        my_logger.info("hive status consumer ended...")
    time.sleep(10)

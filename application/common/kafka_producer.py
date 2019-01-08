import os
import sys

from application import session_factory
from application.common.loggerfile import my_logger
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from application.models.models import TblKafkaPublisher, TblKafkaTopic
from flask import json
from kafka import KafkaProducer
from sqlalchemy.orm import scoped_session



def kafkaproducer(message):
    try:
        producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_server, api_version=kafka_api_version)

        for cluster_customer_details in message:
            customerid = cluster_customer_details["customer_id"]
            clusterid = cluster_customer_details["cluster_id"]
            cluster_info_string = json.dumps(cluster_customer_details)
            producer.send(getGeneratedTopicForTasks(clusterid, customerid), cluster_info_string)
        producer.close()
        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.info(" ".join([exc_type, fname, exc_tb.tb_lineno]))
        return False

    finally:
        my_logger.info("Returning From Producer")

    return True


def getGeneratedTopicForTasks(clusterid, customerid):
    return "tasks_" + customerid + "_" + clusterid


def kafkaproducer_old(message):
    # Connection to kafka
    try:
        producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_server, api_version=kafka_api_version)
        db_session = scoped_session(session_factory)
        print message
        for cluster_customer_details in message:

            customerid = cluster_customer_details["customer_id"]
            clusterid = cluster_customer_details["cluster_id"]

            kafka_publisher_query_statement = db_session.query(TblKafkaPublisher).filter(
                TblKafkaPublisher.uid_customer_id == customerid, TblKafkaPublisher.uid_cluster_id == clusterid).all()

            # for i in kafka_publisher_query_statement:
            #      print i.as_dict()
            #      #kafka_topic_id_info = i.to_dict()

            kafka_topic_id_info = [i.as_dict() for i in kafka_publisher_query_statement]
            #           print kafka_topic_id_info,"kafka topic idddddddddddddssssssssssssssss"
            my_logger.info(kafka_topic_id_info)
            my_logger.info("Runnnnn........................")
            for kafka_topic_string in kafka_topic_id_info:
                my_logger.debug("In for loop")
                print(kafka_topic_string)
                # kafka_topic = json.loads(kafka_topic_string)
                kafka_topic = kafka_topic_string
                my_logger.debug("", kafka_topic)
                kafka_topic_query_statement = db_session.query(TblKafkaTopic).filter(
                    TblKafkaTopic.uid_topic_id == kafka_topic["uid_topic_id"]).all()
                kafka_topic_name_string = [i.as_dict() for i in kafka_topic_query_statement]
                # print kafka_topic_name_string

                kafka_topic_name_info = kafka_topic_name_string[0]
                my_logger.info(kafka_topic_name_info)
                my_logger.info("  Id of Kafka topic")
                if kafka_topic_name_info["var_topic_type"] == "tasks":
                    my_logger.info("in tasks")
                    # topicid=json.loads(kafka_topic_id_info[0])

                    # Retrieving topic name

                    kafka_topic_name = kafka_topic_name_info["var_topic_name"]
                    kafkatopic = kafka_topic_name.decode('utf-8')
                    my_logger.debug(kafkatopic)
                    my_logger.debug(cluster_customer_details)
                    cluster_info_string = json.dumps(cluster_customer_details)
                    producer.send(kafkatopic, cluster_info_string)
                    my_logger.info("sending message to kafka topic")
                    producer.flush()
        producer.close()
        db_session.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

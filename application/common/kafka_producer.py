from kafka import KafkaProducer
from application.models.models import TblKafkaPublisher, TblKafkaTopic
from application import app, db
from flask import json
from sqlalchemy.orm import scoped_session
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from application.common.loggerfile import my_logger
from application import session_factory

def kafkaproducer(message):
    # Connection to kafka
    try:
        producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_server, api_version=kafka_api_version)
        db_session = scoped_session(session_factory)
        for cluster_customer_details in message:

            customerid = cluster_customer_details["customer_id"]
            clusterid = cluster_customer_details["cluster_id"]
            kafka_publisher_query_statement = db_session.query(TblKafkaPublisher).filter(
                TblKafkaPublisher.uid_customer_id == customerid, TblKafkaPublisher.uid_cluster_id == clusterid).all()
            kafka_topic_id_info = [i.to_json() for i in kafka_publisher_query_statement]

            for kafka_topic_string in kafka_topic_id_info:
                my_logger.debug("In for loop")
                kafka_topic = json.loads(kafka_topic_string)
                kafka_topic_query_statement = db_session.query(TblKafkaTopic).filter(
                    TblKafkaTopic.uid_topic_id == kafka_topic["uid_topic_id"]).all()
                kafka_topic_name_string = [i.to_json() for i in kafka_topic_query_statement]
                # print kafka_topic_name_string

                kafka_topic_name_info = json.loads(kafka_topic_name_string[0])
                my_logger.debug(kafka_topic_name_info)
                my_logger.debug("  Id of Kafka topic")
                if kafka_topic_name_info["var_topic_type"] == "tasks":
                    my_logger.debug("in tasks")
                    # topicid=json.loads(kafka_topic_id_info[0])

                    # Retrieving topic name

                    kafka_topic_name = kafka_topic_name_info["var_topic_name"]
                    kafkatopic = kafka_topic_name.decode('utf-8')
                    my_logger.debug(kafkatopic)
                    my_logger.debug(cluster_customer_details)
                    cluster_info_string = json.dumps(cluster_customer_details)
                    producer.send(kafkatopic, cluster_info_string)
                    my_logger.debug("sending message to kafka topic")
                    producer.flush()
        producer.close()
        db_session.close()
    except Exception as e:
        my_logger.debug(e)
        my_logger.debug("Something went wrong in kafka consumer..")
        return e.message

import time,sys,os
import pymongo

from flask import Blueprint,jsonify
from application import mongo_conn_string

from application.common.metrics_updation import metricSubscriber
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from flask import json,request
from kafka import KafkaConsumer
from application.common.loggerfile import my_logger
from sqlalchemy.orm import scoped_session
from application import session_factory

hdfsmongometrics = Blueprint('hdfsmongometrics',__name__)
@hdfsmongometrics.route("/api/hdfs_mongo",methods=['POST'])
def hdfs_metrics_consumer():
    # Connection to kafka
    # try:
        # db_session = scoped_session(session_factory)
        data = request.json
        print data,type(data)

        if data['event_type'] == "metrics":
            customerid = data['customer_id']
            cluster_id = data['cluster_id']
            print customerid
            mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
            database_conn = mongo_db_conn['local']
            db_collection = database_conn[cluster_id]

            result = db_collection.insert_one(data)

import time,sys,os
import pymongo

from flask import Blueprint,jsonify
from application import mongo_conn_string

from application.common.metrics_updation import metricSubscriber
from flask import json,request
from application.common.loggerfile import my_logger
from sqlalchemy.orm import scoped_session
from application import session_factory

hdfsmetricsapi = Blueprint('hdfsmetricsapi',__name__)
@hdfsmetricsapi.route("/api/hdfs_metrics",methods=['POST'])
def hdfs_metrics_consumer():
# Connection to kafka
    try:
        # db_session = scoped_session(session_factory)
        data = request.json
        print data,type(data)

        if data['event_type'] == "metrics":
            cluster_id = data['cluster_id']
            mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
            database_conn = mongo_db_conn['highgear']
            db_collection = database_conn[cluster_id]
            db_collection.insert_one(data)
            return ('posted')
    except pymongo.errors.ConnectionFailure, e:
        my_logger.debug(e)


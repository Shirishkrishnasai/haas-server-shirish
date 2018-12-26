from flask import jsonify,request
import pymongo
import psycopg2
import uuid
from application import conn_string,mongo_conn_string
from flask import Blueprint
from application.models.models import TblCustomerRequest
from application import app,db


highgearclient=Blueprint('highgearclient', __name__)
@highgearclient.route("/addcluster",methods=['POST'])

def hg_client():

    try:
        customer_request=request.json

    # Getting data to build cluster


        customer_data = customer_request['payload']

        # Connectiong to mongodb to insert customer data
        if customer_data['cloud_type'] == "azure":

            mongo_connection = pymongo.MongoClient(mongo_conn_string)
            database_connection = mongo_connection["haas"]
            collection_connection = database_connection["highgear"]
            insertstatement=collection_connection.insert_one(customer_data)
            cluster_info_querystatment=collection_connection.find_one(customer_data)
            cluster_info_payloadid=str(cluster_info_querystatment["_id"])

        # Connection to postgresql


            connection_to_haas = psycopg2.connect(conn_string)
            cur = connection_to_haas.cursor()

        # Creating requestid


            request_id=str(uuid.uuid1())
            cur.execute("set search_path to highgear;")
            insert_customer=TblCustomerRequest(txt_payload_id=cluster_info_payloadid,uid_request_id=request_id,uid_customer_id=customer_request['customer_id'],char_feature_id=customer_request['feature_id'])
            db.session.add(insert_customer)
            db.session.commit()
            return jsonify(message='success')
    except Exception as e:
        return e.message

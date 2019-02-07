from kafka import KafkaConsumer
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest
import json,os,sys
from application.common.loggerfile import my_logger
from flask import Blueprint,jsonify, request
import requests

jobdiagnostics = Blueprint('jobdiagnostics', __name__)
@jobdiagnostics.route("/api/jobdiagnostics", methods=['POST'])

def diagnosticsconsumer():
    try:
        db_session = scoped_session(session_factory)
        print "in job diagnostics consumerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
        data = request.json
        print data,'dataa postedddddd'

        #for message in data.items():
        #    print message
        #    json_loads_job_data = json.loads(message)
        #    print json_loads_job_data,'jsonnnnnnnnnnnn'
        print data['customer_id'],data['request_id']
        update_customer_job_request=db_session.query(TblCustomerJobRequest).\
            filter(TblCustomerJobRequest.uid_customer_id==data['customer_id'],TblCustomerJobRequest.uid_request_id==data['request_id'])
        print "after queryyyy"
        update_customer_job_request.update({"var_request_status":json_loads_job_data})
        db_session.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


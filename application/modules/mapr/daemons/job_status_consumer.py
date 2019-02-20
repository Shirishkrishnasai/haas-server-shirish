from kafka import KafkaConsumer
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest,TblMetaMrRequestStatus
from flask import Blueprint,render_template,abort, Flask,jsonify,request
from application.common.loggerfile import my_logger
import sys,os,json


jobstatusapi = Blueprint('jobstatusapi', __name__)
@jobstatusapi.route("/job_status",methods=['POST'])

def statusconsumer():
    try:
        session = scoped_session(session_factory)

        job_status_data = request.json
	for application_status in job_status_data:
        	meta_request_status_query = session.query(TblMetaMrRequestStatus.srl_id).filter(TblMetaMrRequestStatus.var_mr_request_status == application_status['status'])

	        update_customer_job_request=session.query(TblCustomerJobRequest).filter(TblCustomerJobRequest.uid_customer_id==application_status['customer_id'],TblCustomerJobRequest.var_application_id==application_status['application_id'])
        	update_customer_job_request.update({"int_request_status":meta_request_status_query[0][0]})
	        session.commit()


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        session.close()
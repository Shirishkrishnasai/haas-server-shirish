from application.common.loggerfile import my_logger
from flask import Blueprint,jsonify
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest
import json,os,sys

jobdetails=Blueprint('jobdetails',__name__)

@jobdetails.route("/job/<request_id>",methods=['GET'])

def requestresponse(request_id):
    try:
        db_session = scoped_session(session_factory)
        customer_job_request_query=db_session.query(TblCustomerJobRequest.var_diagnostics,TblCustomerJobRequest.var_request_status,TblCustomerJobRequest.var_application_id).filter(TblCustomerJobRequest.uid_request_id==request_id)
        job_output_dict=json.loads(customer_job_request_query[0][0])
        job_output_dict['job']['request_status']=customer_job_request_query[0][1]
        return jsonify(job_output_dict['job'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)

    finally:
        db_session.close()

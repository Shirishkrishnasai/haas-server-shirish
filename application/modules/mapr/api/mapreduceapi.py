import os,sys
from application.common.loggerfile import my_logger
from flask import Blueprint,jsonify
from application.models.models import TblCustomerJobRequest
from sqlalchemy.orm import scoped_session
from application import session_factory

mapreduce=Blueprint('mapreduce',__name__)
@mapreduce.route("/mapreduce/<request_id>",methods=['GET'])
def map_r(request_id):
    try:
        job_details_dict={}
        db_session = scoped_session(session_factory)
        customer_job_request_query=db_session.query(TblCustomerJobRequest.var_job_name,TblCustomerJobRequest.var_job_description).filter(TblCustomerJobRequest.uid_request_id==request_id)
        job_details_dict['job_name']=customer_job_request_query[0][0]
        job_details_dict['description']=customer_job_request_query[0][1]
        return jsonify(job_details_dict)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)

    finally:
        db_session.close()


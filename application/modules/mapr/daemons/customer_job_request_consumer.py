from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest
import os,sys
from application.common.loggerfile import my_logger
from flask import Blueprint,request

mrjobupdate=Blueprint('mrjobupdate',__name__)
@mrjobupdate.route('/api/jobupdation',methods=['POST'])

def jobinsertion():
    try:
        session = scoped_session(session_factory)
        jobdetails=request.json
        job_information_dict = jobdetails
        update_customer_job_request=session.query(TblCustomerJobRequest).filter(TblCustomerJobRequest.uid_request_id == job_information_dict['request_id'])
        update_customer_job_request.update({"var_application_id":job_information_dict['application_id']})
        session.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        session.close()

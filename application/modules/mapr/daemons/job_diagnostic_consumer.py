from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest,TblMetaMrRequestStatus
import json,os,sys
from application.common.loggerfile import my_logger
from flask import Blueprint, request

jobdiagnostics = Blueprint('jobdiagnostics', __name__)
@jobdiagnostics.route("/api/jobdiagnostics", methods=['POST'])

def diagnosticsconsumer():
    try:
        db_session = scoped_session(session_factory)
        data = request.json
        state = str(data['app']['state'])
        request_status_value = db_session.query(TblMetaMrRequestStatus.srl_id).\
            filter(TblMetaMrRequestStatus.var_mr_request_status == state).all()
        update_customer_job_request=db_session.query(TblCustomerJobRequest).\
            filter(TblCustomerJobRequest.uid_customer_id==data['customer_id'],TblCustomerJobRequest.uid_request_id==data['request_id'])
        update_customer_job_request.update({"var_job_diagnostics":json.dumps(data['app']),"int_request_status":int(request_status_value[0][0])})
        db_session.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

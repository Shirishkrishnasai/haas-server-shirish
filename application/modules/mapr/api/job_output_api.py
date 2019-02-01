from flask import Blueprint,jsonify
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest
import json

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
		return e.message
    finally:
        db_session.close()

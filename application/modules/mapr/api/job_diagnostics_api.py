from flask import Blueprint,jsonify
from application.models.models import TblCustomerJobRequest
from sqlalchemy.orm import scoped_session
from application import session_factory
import json

jobdiagnostics=Blueprint('jobdiagnostics',__name__)
@jobdiagnostics.route("/jobdiagnostics/<request_id>",methods=['GET'])
def map_r(request_id):
    session = scoped_session(session_factory)
    customer_job_request_query=session.query(TblCustomerJobRequest.var_job_diagnostics).filter(TblCustomerJobRequest.uid_request_id==request_id)
    job_diagnostics_dict=json.loads(customer_job_request_query[0][0])
    return jsonify(job_diagnostics_dict)
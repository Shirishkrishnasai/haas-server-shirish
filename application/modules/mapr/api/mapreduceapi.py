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
    finally:
        db_session.close()

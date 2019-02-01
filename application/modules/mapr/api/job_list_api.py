from flask import Blueprint,jsonify
from application.models.models import TblCustomerJobRequest,TblMetaMrRequestStatus
from sqlalchemy.orm import scoped_session
from application import session_factory
import json
joblist=Blueprint('joblist',__name__)
@joblist.route("/joblist/<customer_id>/<cluster_id>",methods=['GET'])

def job_list(customer_id,cluster_id):
    try:
        db_session = scoped_session(session_factory)
        customer_job_request_query=db_session.query(TblCustomerJobRequest.var_application_id,TblCustomerJobRequest.int_request_status,TblCustomerJobRequest.var_job_diagnostics,TblCustomerJobRequest.uid_request_id).filter(TblCustomerJobRequest.uid_customer_id==customer_id,TblCustomerJobRequest.uid_cluster_id==cluster_id).all()
        #print customer_job_request_query
        job_list=[]
        print customer_job_request_query,"custttttttttttoooooo"
        for each_job in customer_job_request_query:
            #print each_job,'eksksksks'
            #print each_job[2]
            #if any(x is None for x in each_job[2]) is False:
            if each_job[2] is not None:
                print "insideeeeeeee"
                individual_job_diagnostics={}
                meta_mr_status_query=session.query(TblMetaMrRequestStatus.var_mr_request_status).filter(TblMetaMrRequestStatus.srl_id==customer_job_request_query[0][1]).all()
                job_diagnostic=json.loads(each_job[2])
                print job_diagnostic,'diooooooooooooo'
                #print each_job[3],len(each_job),"eavcccchhh"
                print job_diagnostic['jobs']['job']
                individual_job_diagnostics['application_id']=each_job[0]
                individual_job_diagnostics['job_status']=meta_mr_status_query[0][0]
                individual_job_diagnostics['job_start_time']=job_diagnostic['jobs']['job'][0]['startTime']
                individual_job_diagnostics['job_end_time']=job_diagnostic['jobs']['job'][0]['finishTime']
                individual_job_diagnostics['mr_job_id'] = each_job[3]
                #print individual_job_diagnostics['mr_job_id'],"lollll"
                #print type(individual_job_diagnostics['job_start_time']),"oneeeeeeeeeee"
                #print type(individual_job_diagnostics['job_end_time']),"twooooooooooo"
                job_list.append(individual_job_diagnostics)
                print job_list,"jollllllllllllll"
        return jsonify(jobs=job_list)
    finally:
        db_session.close()

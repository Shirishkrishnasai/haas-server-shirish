from flask import Blueprint,jsonify
from application.models.models import TblCustomerJobRequest,TblMetaMrRequestStatus
from sqlalchemy.orm import scoped_session
from application import session_factory
import json
import sys,os
from application.common.loggerfile import my_logger

joblist=Blueprint('joblist',__name__)
@joblist.route("/joblist/<customer_id>/<cluster_id>",methods=['GET'])

def job_list(customer_id,cluster_id):
    try:
        db_session = scoped_session(session_factory)
        customer_job_request_query=db_session.query(TblCustomerJobRequest.var_application_id,TblCustomerJobRequest.int_request_status,TblCustomerJobRequest.var_job_diagnostics,TblCustomerJobRequest.uid_request_id,TblCustomerJobRequest.txt_job_description,TblCustomerJobRequest.var_job_name).filter(TblCustomerJobRequest.uid_customer_id==customer_id,TblCustomerJobRequest.uid_cluster_id==cluster_id).all()
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
                meta_mr_status_query=db_session.query(TblMetaMrRequestStatus.var_mr_request_status).filter(TblMetaMrRequestStatus.srl_id==each_job[1]).all()
                job_diagnostic=json.loads(each_job[2])
                print job_diagnostic,'diooooooooooooo'
                #print each_job[3],len(each_job),"eavcccchhh"
              #  print job_diagnostic['jobs']['job']
                individual_job_diagnostics['application_id']=each_job[0]
                individual_job_diagnostics['job_status']=meta_mr_status_query[0][0]
                individual_job_diagnostics['startedTime']=job_diagnostic['startedTime']
                individual_job_diagnostics['endTime']=job_diagnostic['elapsedTime']
                individual_job_diagnostics['mr_job_id'] = each_job[3]
                individual_job_diagnostics['description'] = each_job[4]
                individual_job_diagnostics['job_name'] = each_job[5]
                #print individual_job_diagnostics['mr_job_id'],"lollll"
                #print type(individual_job_diagnostics['job_start_time']),"oneeeeeeeeeee"
                #print type(individual_job_diagnostics['job_end_time']),"twooooooooooo"
                job_list.append(individual_job_diagnostics)
                print job_list,"jollllllllllllll"
        return jsonify(jobs=job_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)

    finally:
        db_session.close()

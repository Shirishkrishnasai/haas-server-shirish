from kafka import KafkaConsumer
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest,TblMetaMrRequestStatus
import json,os,sys
from application.common.loggerfile import my_logger
from flask import Blueprint,jsonify, request
import requests

jobdiagnostics = Blueprint('jobdiagnostics', __name__)
@jobdiagnostics.route("/api/jobdiagnostics", methods=['POST'])

def diagnosticsconsumer():
    #try:
        db_session = scoped_session(session_factory)
        print "in job diagnostics consumerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
        data = request.json
        print data,type(data),'dataa postedddddd'
        state = str(data['app']['state'])
        print state,type(state),'sattttttttttttt'
        request_status_value = db_session.query(TblMetaMrRequestStatus.srl_id).\
            filter(TblMetaMrRequestStatus.var_mr_request_status == state).all()
        print request_status_value[0][0],'valueeeeeeeeeeeeeeeeeeeeeeee'
        print data['app'],'apppppppp'
        #for message in data.items():
        #    print message
        #    json_loads_job_data = json.loads(message)
        #    print json_loads_job_data,'jsonnnnnnnnnnnn'
        print data['customer_id'],data['request_id']
        update_customer_job_request=db_session.query(TblCustomerJobRequest).\
            filter(TblCustomerJobRequest.uid_customer_id==data['customer_id'],TblCustomerJobRequest.uid_request_id==data['request_id'])
        print "after queryyyy"
        update_customer_job_request.update({"var_job_diagnostics":json.dumps(data['app']),"int_request_status":int(request_status_value[0][0])})
        db_session.commit()
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #
    #     my_logger.error(exc_type)
    #     my_logger.error(fname)
    #     my_logger.error(exc_tb.tb_lineno)
    # finally:
    #     db_session.close()


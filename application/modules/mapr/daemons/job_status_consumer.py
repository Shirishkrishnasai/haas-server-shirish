import sendgrid
from sqlalchemy.orm import scoped_session
from application import session_factory, sendgrid_key
from application.models.models import TblCustomerJobRequest,TblMetaMrRequestStatus
from flask import Blueprint,jsonify,request
from application.common.loggerfile import my_logger
from sendgrid.helpers.mail import *
import sys,os


jobstatusapi = Blueprint('jobstatusapi', __name__)
@jobstatusapi.route("/job_status",methods=['POST'])

def statusconsumer():
    try:
        session = scoped_session(session_factory)

        job_status_data = request.json
        for application_status in job_status_data:
            meta_request_status_query = session.query(TblMetaMrRequestStatus.srl_id).filter(TblMetaMrRequestStatus.var_mr_request_status == application_status['status'])

            update_customer_job_request=session.query(TblCustomerJobRequest).filter(TblCustomerJobRequest.uid_customer_id==application_status['customer_id'],TblCustomerJobRequest.var_application_id==application_status['application_id'])
            update_customer_job_request.update({"int_request_status":meta_request_status_query[0][0]})
            session.commit()
            # mail integration
            meta_task_status_dict = dict(
                session.query(TblMetaMrRequestStatus.var_mr_request_status, TblMetaMrRequestStatus.srl_id).all())
            job_name = session.query(TblCustomerJobRequest.var_job_name, TblCustomerJobRequest.var_user_name).filter(
                TblCustomerJobRequest.var_application_id == application_status['application_id']).first()
            if meta_task_status_dict["FINISHED"] == meta_request_status_query[0]:
                message = "Mapreduce job with job name '" + job_name[0] + "' success"
            elif meta_task_status_dict["FAILED"] == meta_request_status_query[0]:
                message = "Mapreduce job with job name '" + job_name[0] + "' failed"
            else:
                pass
            subject = "Mapreduce job information"
            sendgrid_obj = sendgrid.SendGridAPIClient(apikey=sendgrid_key)
            from_email = Email('jasti700@gmail.com')
            to_email = Email(job_name[1])
            content_to_send = Content("text/plain", message)
            mail_sent = Mail(from_email, subject, to_email, content_to_send)
            response = sendgrid_obj.client.mail.send.post(request_body=mail_sent.get())
            return jsonify(response.status_code)
            # mail integration
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        session.close()
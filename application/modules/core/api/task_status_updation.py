import sys,os
import sendgrid
from sendgrid.helpers.mail import *
from application.config.config_file import sendgrid_key
from flask import jsonify, request, Blueprint
from application import session_factory
from application.common.loggerfile import my_logger
from application.models.models import TblTask, TblMetaTaskStatus,TblCustomerRequest, TblCluster, TblUsers
from sqlalchemy.orm import scoped_session
from datetime import datetime
taskstatus=Blueprint('taskstatus', __name__)
@taskstatus.route("/taskstatus", methods=['POST'])
def task_status_update():
   try:
        db_session = scoped_session(session_factory)
        task_status_information = request.json
        taskid = task_status_information["payload"]["task_id"]
        taskstatus = task_status_information["payload"]["status"]
        customerid = task_status_information["customer_id"]
        clusterid = task_status_information["cluster_id"]
        meta_task_status_dict = dict(db_session.query(TblMetaTaskStatus.var_task_status,
                                                 TblMetaTaskStatus.srl_id).all())
        taskstatusupdate = db_session.query(TblTask).filter(TblTask.uid_task_id == taskid)
        taskstatusupdate.update({"int_task_status": meta_task_status_dict[taskstatus]})
        db_session.commit()
        updated_task_status_query=db_session.query(TblTask.int_task_status).filter(TblTask.uid_task_id== taskid).first()
        if updated_task_status_query[0] == meta_task_status_dict[taskstatus]:
            request1 = db_session.query(TblTask.uid_request_id).filter(TblTask.uid_task_id == taskid).first()
            requests_id = request1[0]
            taskid_statuses = db_session.query(TblTask.int_task_status).filter(TblTask.uid_request_id==requests_id).all()
            if all(x[0] == meta_task_status_dict['COMPLETED'] for x in taskid_statuses):
                #mail_sending
                feature_id=db_session.query(TblCustomerRequest.char_feature_id).filter(TblCustomerRequest.uid_request_id==requests_id).first()
                if feature_id[0]=='10':
                    message="Cluster provision and configuration completed and ready to use"
                elif feature_id[0]=='12' :
                    message="Hive node provison and configuration completed and ready to use"
                elif feature_id[0]=='14':
                    message="Spark node provison and configuration is completed and ready to use"
                else :
                    pass
                sendgrid_obj = sendgrid.SendGridAPIClient(apikey=sendgrid_key)
                from_email = Email('jasti700@gmail.com')
                to_adress = db_session.query(TblUsers.var_user_name).filter(TblUsers.uid_customer_id == customerid).first()
                to_email = Email(to_adress[0])
                subject = "azure cluster information"
                content_to_send = Content("text/plain", message)
                mail_sent = Mail(from_email, subject, to_email, content_to_send)
                sendgrid_obj.client.mail.send.post(request_body=mail_sent.get())
                #mail_sending
                valid_cluster_status = db_session.query(TblCluster.valid_cluster,TblCluster.cluster_created_datetime).filter(
                    TblCluster.uid_cluster_id == clusterid)
                date_time = datetime.now()
                valid_cluster_status.update({"valid_cluster": True,"cluster_created_datetime":date_time})
                db_session.commit()
                requests = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == requests_id)
                requests.update({"int_request_status": meta_task_status_dict['COMPLETED']})
                db_session.commit()
            else:
                requests = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == requests_id)
                requests.update({"int_request_status": meta_task_status_dict['RUNNING']})
                db_session.commit()
            return jsonify(message="success", taskid=taskid)
        else :
            return jsonify(message="failed",taskid=taskid)
   except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
        return jsonify(message="failed")
   finally:
      db_session.close()

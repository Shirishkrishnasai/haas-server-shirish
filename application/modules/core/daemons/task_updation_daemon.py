import datetime,os,sys
from application.common.loggerfile import my_logger
from sqlalchemy import and_
from application import  session_factory
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import scoped_session
from application.config.config_file import sendgrid_key
from sendgrid import sendgrid
from sendgrid.helpers.mail import *
from application.models.models import TblTask, TblMetaTaskStatus, TblCustomerRequest, TblCluster, TblUsers
def updated_Task():
    try:
        db_session = scoped_session(session_factory)
        meta_task_status_dict = dict(db_session.query(TblMetaTaskStatus.var_task_status,
                                                      TblMetaTaskStatus.srl_id).all())
        req_ids=db_session.query(TblCustomerRequest.uid_request_id,TblCustomerRequest.uid_customer_id,TblCustomerRequest.uid_cluster_id).filter(and_(TblCustomerRequest.char_feature_id!='9',TblCustomerRequest.char_feature_id!='11',
                                                                                     TblCustomerRequest.char_feature_id!='13',TblCustomerRequest.int_request_status!='4')).all()
        for ids in req_ids :
            request_id=ids[0]
            customer_id=ids[1]
            cluster_id=ids[2]
            total_tasks=db_session.query(TblTask.int_task_status).filter(TblTask.uid_request_id==request_id).all()
            if total_tasks!=[]:
                if all(x[0] == meta_task_status_dict['COMPLETED'] for x in total_tasks):
                    # mail_sending
                    feature_id=db_session.query(TblCustomerRequest.char_feature_id).filter(TblCustomerRequest.uid_request_id==request_id).first()
                    requests = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == request_id)
                    requests.update({"int_request_status": meta_task_status_dict['COMPLETED']})
                    db_session.commit()
                    if feature_id[0]=='10':
                         message="Cluster provision and configuration completed and ready to use"
                         date_time = datetime.datetime.now()
                         valid_cluster_status = db_session.query(TblCluster.valid_cluster,TblCluster.cluster_created_datetime).filter(TblCluster.uid_cluster_id == cluster_id)
                         valid_cluster_status.update({"valid_cluster": True, "cluster_created_datetime": date_time})
                         db_session.commit()
                    elif feature_id[0]=='12' :
                          message="Hive node provison and configuration completed and ready to use"
                    elif feature_id[0]=='14':
                         message="Spark node provison and configuration is completed and ready to use"
                    else :
                         pass
                    sendgrid_obj = sendgrid.SendGridAPIClient(apikey=sendgrid_key)
                    from_email = Email('jasti700@gmail.com')
                    to_adress = db_session.query(TblUsers.var_user_name).filter(TblUsers.uid_customer_id == customer_id).first()
                    to_email = Email(to_adress[0])
                    subject = "azure cluster information"
                    content_to_send = Content("text/plain", message)
                    mail_sent = Mail(from_email, subject, to_email, content_to_send)
                    sendgrid_obj.client.mail.send.post(request_body=mail_sent.get())
                else :
                       pass
            else :
                 pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

def taskupdationscheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(updated_Task, 'cron', second='*/15')
    scheduler.start()
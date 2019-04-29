import datetime,os,sys
from application.common.loggerfile import my_logger
from sqlalchemy import and_,or_
from application import  session_factory
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import scoped_session
from application.config.config_file import sendgrid_key
from sendgrid import sendgrid, SendGridAPIClient
from sendgrid.helpers.mail import *
from application.models.models import TblTask, TblMetaTaskStatus, TblCustomerRequest, TblCluster, TblUsers, TblCustomer


def updated_Task():
    try:
        db_session = scoped_session(session_factory)
        meta_task_status_dict = dict(db_session.query(TblMetaTaskStatus.var_task_status,
                                                      TblMetaTaskStatus.srl_id).all())
        req_ids=db_session.query(TblCustomerRequest.uid_request_id,TblCustomerRequest.uid_customer_id,TblCustomerRequest.uid_cluster_id).filter(TblCustomerRequest.char_feature_id!='9').filter(TblCustomerRequest.char_feature_id!='11').filter(TblCustomerRequest.char_feature_id!='13').filter(or_(TblCustomerRequest.int_request_status!='4',TblCustomerRequest.int_request_status==None)).all()
        for ids in req_ids :
            request_id=ids[0]
            customer_id=ids[1]
            cluster_id=ids[2]
            cluster_name=db_session.query(TblCluster.var_cluster_name).filter(TblCluster.uid_cluster_id==cluster_id).first()
            total_tasks=db_session.query(TblTask.int_task_status).filter(TblTask.uid_request_id==request_id).all()
            if total_tasks!=[]:
                if all(x[0] == meta_task_status_dict['COMPLETED'] for x in total_tasks):
                    # mail_sending
                    user_dn = db_session.query(TblCustomer.txt_customer_dn).filter(TblCustomer.uid_customer_id == customer_id).first()
                    details_user = user_dn[0].split(',')
                    username = str(details_user[0]).split('=')
                    feature_id=db_session.query(TblCustomerRequest.char_feature_id).filter(TblCustomerRequest.uid_request_id==request_id).first()
                    requests = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == request_id)
                    requests.update({"int_request_status": meta_task_status_dict['COMPLETED']})
                    db_session.commit()
                    if feature_id[0]=='10':
                         message_to_send="Dear "+ username[1]+" your cluster request is completed now you can use the " +cluster_name+" cluster"
                         date_time = datetime.datetime.now()
                         valid_cluster_status = db_session.query(TblCluster.valid_cluster,TblCluster.cluster_created_datetime).filter(TblCluster.uid_cluster_id == cluster_id)
                         valid_cluster_status.update({"valid_cluster": True, "cluster_created_datetime": date_time})
                         db_session.commit()
                    elif feature_id[0]=='12' :
                          message_to_send="Dear "+ username[1]+" your Hive node request is completed now you can use the hive on" +cluster_name+" cluster"
                    elif feature_id[0]=='14':
                         message_to_send="Dear "+ username[1]+" your spark node request is completed now you can use the spark on " +cluster_name+" cluster"
                    else :
                         pass
                    to_adress = db_session.query(TblUsers.var_user_name).filter(
                        TblUsers.uid_customer_id == customer_id).first()
                    to_email = Email(to_adress[0])
                    message = Mail(from_email='jasti700@gmail.com',to_emails=to_email,subject='cluster datils',html_content=message_to_send)
                    sendgrid_client = SendGridAPIClient(sendgrid_key)
                    sendgrid_client.send(message)

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

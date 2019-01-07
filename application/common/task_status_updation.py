from application import session_factory
from application.common.loggerfile import my_logger
from application.models.models import TblTask, TblMetaTaskStatus
from sqlalchemy.orm import scoped_session


def taskstatusconsumer(task_status_information):
    # Updatind task status in database
    db_session = scoped_session(session_factory)
    try:

        taskid = task_status_information["payload"]["task_id"]
        taskstatus = task_status_information["payload"]["status"]
        customerid = task_status_information["customer_id"]
        taskstatuslower = str(taskstatus.upper())
        metataskstatus = db_session.query(TblMetaTaskStatus.srl_id).filter(
            TblMetaTaskStatus.var_task_status == taskstatuslower).all()
        # query = db_session.query(TblTask).filter(TblTask.uid_task_id == taskid, TblTask.uid_customer_id == customerid)
        taskstatusupdate = db_session.query(TblTask).filter(TblTask.uid_task_id == taskid).filter(
            TblTask.uid_customer_id == customerid)
        taskstatusupdate.update({"int_task_status": metataskstatus[0][0]})
        db_session.commit()
    except Exception as e:
        my_logger.error(str(e));
    finally:
        db_session.close();

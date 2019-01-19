from application import session_factory
from application.common.loggerfile import my_logger
from application.models.models import TblTask, TblMetaTaskStatus,TblMetaRequestStatus,TblCustomerRequest
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
        request = db_session.query(TblTask.uid_request_id).filter(TblTask.uid_task_id == taskid).all()
        requests_id = request[0][0]
        task_id = db_session.query(TblTask.uid_task_id).filter(TblTask.uid_request_id == requests_id).all()
        completedstatus = db_session.query(TblMetaRequestStatus.srl_id).filter(
            TblMetaRequestStatus.var_request_status == "COMPLETED").all()
        completed = completedstatus[0][0]
        runningstatus = db_session.query(TblMetaRequestStatus.srl_id).filter(
            TblMetaRequestStatus.var_request_status == "RUNNING").all()
        running = runningstatus[0][0]
        tuple = []
        for task in task_id:
            status = db_session.query(TblTask.int_task_status).filter(TblTask.uid_task_id == task[0]).all()
            tuple.append(status)
        if all(x == completedstatus for x in tuple):
            request = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == requests_id)
            request.update({"int_request_status": completed})
            db_session.commit()
        else:
            request = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == requests_id)
            request.update({"int_request_status": running})
            db_session.commit()
    except Exception as e:
        my_logger.error(str(e));
    finally:
        db_session.close();

from flask import Flask, jsonify, request, Request, Blueprint
from application import session_factory
from application.common.loggerfile import my_logger
from application.models.models import TblTask, TblMetaTaskStatus, TblMetaRequestStatus, TblCustomerRequest
from sqlalchemy.orm import scoped_session
taskstatus=Blueprint('taskstatus', __name__)
@taskstatus.route("/taskstatus", methods=['POST'])
def task_status_update():
    try:
        db_session = scoped_session(session_factory)
        # db_session.query(TblTask).filter(TblTask.char_feature_id==9).all()
        task_status_information = request.json
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
        request1 = db_session.query(TblTask.uid_request_id).filter(TblTask.uid_task_id == taskid).all()
        requests_id = request1[0][0]
        task_id = db_session.query(TblTask.uid_task_id).filter(TblTask.uid_request_id == requests_id).all()
        completedstatus = db_session.query(TblMetaRequestStatus.srl_id).filter(
            TblMetaRequestStatus.var_request_status == "COMPLETED").all()
        completed = completedstatus[0][0]
        runningstatus = db_session.query(TblMetaRequestStatus.srl_id).filter(
            TblMetaRequestStatus.var_request_status == "RUNNING").all()
        running = runningstatus[0][0]
        tuple = []
        for task in task_id:
            print "hi im in for"
            status = db_session.query(TblTask.int_task_status).filter(TblTask.uid_task_id == task[0]).all()
            tuple.append(status)
        print tuple
        if all(x == completedstatus for x in tuple):
            print "im in if"
            requests = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == requests_id)
            requests.update({"int_request_status": completed})
            db_session.commit()
            return jsonify(message=completed)
        else:
            print "im in else"
            requests = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == requests_id)
            requests.update({"int_request_status": running})
            db_session.commit()
            return jsonify(message=running)
        return jsonify(message="completed")
    except Exception as e:
        return e.message
    finally:
        db_session.close()
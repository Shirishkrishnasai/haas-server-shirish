from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblTask,TblMetaTaskStatus

def taskstatusconsumer(task_status_information):
    # Updatind task status in database

    try:

        print "connection okkkkkkkkkkkkkkkkaaaaaaaaaaaaaaaayyyyyyyyyyyyyyyyyyyyyyyyyy"
        db_session = scoped_session(session_factory)
        taskid = task_status_information["payload"]["task_id"]
        print taskid
        taskstatus = task_status_information["payload"]["status"]
        customerid = task_status_information["customer_id"]
        print customerid
        taskstatuslower=str(taskstatus.upper())
        print len(taskstatuslower)
        print taskstatuslower
        metataskstatus=db_session.query(TblMetaTaskStatus.srl_id).filter(TblMetaTaskStatus.var_task_status == taskstatuslower).all()


        print metataskstatus, 'heeeeeeeeeeeeeeeeeeeeeeee'
        print type(metataskstatus[0][0])
        #query = db_session.query(TblTask).filter(TblTask.uid_task_id == taskid, TblTask.uid_customer_id == customerid)
        taskstatusupdate = db_session.query(TblTask).filter(TblTask.uid_task_id == taskid).filter(TblTask.uid_customer_id == customerid)
        print "result",taskstatusupdate
        taskstatusupdate.update({"int_task_status": metataskstatus[0][0]})
        db_session.commit()
        db_session.close()
        print 'hurrrrrrrrrrrrrrrrrrrrraaaaaaaaaaaaaaaaayyyyyyyyyyyyyyyyyy'
    except Exception as e:
        print e.message
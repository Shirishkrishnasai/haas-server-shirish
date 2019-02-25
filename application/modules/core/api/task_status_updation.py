from flask import jsonify, request, Blueprint
from application import session_factory
from application.models.models import TblTask, TblMetaTaskStatus, TblMetaRequestStatus, TblCustomerRequest, TblCluster, \
    TblUsers
from sqlalchemy.orm import scoped_session
from datetime import datetime

taskstatus = Blueprint('taskstatus', __name__)


@taskstatus.route("/taskstatus", methods=['POST'])
def task_status_update():
    try:
        db_session = scoped_session(session_factory)
        task_status_information = request.json
        taskid = task_status_information["payload"]["task_id"]
        taskstatus = task_status_information["payload"]["status"]
        print taskstatus, 'staaaaaaaaaaaatttttttttttttuuuuuuuuuuuuussssssssssssssssssssssssss'
        customerid = task_status_information["customer_id"]
        clusterid = task_status_information["cluster_id"]
        meta_task_status_dict = dict(db_session.query(TblMetaTaskStatus.var_task_status,
                                                      TblMetaTaskStatus.srl_id).all())

        taskstatusupdate = db_session.query(TblTask).filter(TblTask.uid_task_id == taskid)
        print meta_task_status_dict[taskstatus], 'iiiiiiiiiiiiiiiiinnnnnnnnnnnnnnnnntttttttttttttttttttttttttttttt'
        taskstatusupdate.update({"int_task_status": meta_task_status_dict[taskstatus]})

        db_session.commit()
        request1 = db_session.query(TblTask.uid_request_id).filter(TblTask.uid_task_id == taskid).first()
        requests_id = request1[0]
        taskid_statuses = db_session.query(TblTask.int_task_status).filter(TblTask.uid_request_id == requests_id).all()

        if all(x[0] == meta_task_status_dict['COMPLETED'] for x in taskid_statuses):
            valid_cluster_status = db_session.query(TblCluster.valid_cluster,
                                                    TblCluster.cluster_created_datetime).filter(
                TblCluster.uid_cluster_id == clusterid)
            date_time = datetime.now()
            valid_cluster_status.update({"valid_cluster": True, "cluster_created_datetime": date_time})
            db_session.commit()
            requests = db_session.query(TblCustomerRequest.int_request_status).filter(
                TblCustomerRequest.uid_request_id == requests_id).first()
            requests.update({"int_request_status": meta_task_status_dict['COMPLETED']})
            db_session.commit()
        else:
            requests = db_session.query(TblCustomerRequest.int_request_status).filter(
                TblCustomerRequest.uid_request_id == requests_id)
            requests.update({"int_request_status": meta_task_status_dict['RUNNING']})
            db_session.commit()
        return jsonify("sucess")
    except Exception as e:
        print e.message
        return jsonify("failed")
    finally:
        db_session.close()


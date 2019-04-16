import sys,os
from flask import jsonify, request, Blueprint
from application import session_factory
from application.common.loggerfile import my_logger
from application.models.models import TblTask, TblMetaTaskStatus
from sqlalchemy.orm import scoped_session
servertaskstatus=Blueprint('servertaskstatus', __name__)
@servertaskstatus.route('/servertaskstatus/<task_id>', methods=['POST'])
def server_task_status_update(task_id):
    try:
        db_session = scoped_session(session_factory)
        server_task_status_information = request.json
        status = server_task_status_information['status']
        cluster_id = server_task_status_information['cluster_id']
        meta_task_status_dict = dict(db_session.query(TblMetaTaskStatus.var_task_status,
                                                      TblMetaTaskStatus.srl_id).all())
        my_logger.info(meta_task_status_dict)
        task_status_update = db_session.query(TblTask).filter(TblTask.uid_task_id == task_id)

        task_status_update.update({"int_task_status": meta_task_status_dict[str(status)]})
        db_session.commit()
        my_logger.info("task status updation commiting doneeeeee")
        return jsonify(message="success", taskid=task_id, return_status=status)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
        return jsonify(message="failed")
    finally:
        db_session.close()

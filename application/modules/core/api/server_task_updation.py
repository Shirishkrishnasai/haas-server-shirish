import sys,os
import sendgrid
from sendgrid.helpers.mail import *
# from application.config.config_file import sendgrid_key
from flask import jsonify, request, Blueprint
from application import session_factory
from application.common.loggerfile import my_logger
from application.models.models import TblTask, TblMetaTaskStatus,TblCustomerRequest, TblCluster, TblUsers,TblMetaRequestStatus
from sqlalchemy.orm import scoped_session
from datetime import datetime
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
        print meta_task_status_dict
        task_status_update = db_session.query(TblTask).filter(TblTask.uid_task_id == task_id)

        task_status_update.update({"int_task_status": meta_task_status_dict[str(status)]})
        db_session.commit()

        request_id_task_query = db_session.query(TblTask.uid_request_id).filter(TblTask.uid_task_id == task_id).all()
        request_id = request_id_task_query[0][0]
        print request_id,'reqstidddddddddddddd'
        task_status_query = db_session.query(TblTask.int_task_status).filter(TblTask.uid_request_id == request_id).all()
        print task_status_query


        # completed_value = meta_task_status_dict[str('COMPLETED')]

        if all(tasks[0] == meta_task_status_dict['COMPLETED'] for tasks in task_status_query):
            print 'heyeeeeeeeeeee'
            customer_request_status = db_session.query(TblMetaRequestStatus.srl_id)\
                .filter(TblMetaRequestStatus.var_request_status == 'COMPLETED' ).all()
            print customer_request_status[0][0]
            customer_request_status_update = db_session.query(TblCustomerRequest).filter(
                TblCustomerRequest.uid_request_id == request_id)
            customer_request_status_update.update({"int_request_status": customer_request_status[0][0]})
            db_session.commit()

            update_valid_cluster = db_session.query(TblCluster).filter(TblCluster.uid_cluster_id == cluster_id)
            update_valid_cluster.update({"valid_cluster": 1})
            db_session.commit()
            return jsonify(message="success", taskid=task_id)
        else:
            customer_request_status = db_session.query(TblMetaRequestStatus.srl_id) \
                .filter(TblMetaRequestStatus.var_request_status == 'RUNNING').all()
            customer_request_status_update = db_session.query(TblCustomerRequest).filter(
                TblCustomerRequest.uid_request_id == request_id)
            customer_request_status_update.update({"int_request_status": customer_request_status[0][0]})
            db_session.commit()
            return jsonify(message="success", taskid=task_id)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
        return jsonify(message="failed")
    finally:
        db_session.close()

# server_task_status_update('ca59a5c2-38dc-11e9-a59a-000d3af26ae2')
# cluster_id('85a6ff60-38dc-11e9-a59a-000d3af26ae2')
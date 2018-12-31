from application import session_factory
from application import mongo_conn_string
from application.models.models import TblAgent, TblCustomerRequest, TblFeature,TblFeatureType,TblTaskType,TblTask
import uuid
import datetime
from sqlalchemy.orm import scoped_session
from application import session_factory

def fileuploadworker(request_id):
    task_id=str(uuid.uuid1())
    db_session = scoped_session(session_factory)
    db_session = scoped_session(session_factory)
    customer_request_query=db_session.query(TblCustomerRequest.uid_customer_id,TblCustomerRequest.uid_cluster_id,TblCustomerRequest.char_feature_id,TblCustomerRequest.txt_payload_id).filter(TblCustomerRequest.uid_request_id==request_id).all()
    featuretpe_query=db_session.query(TblFeatureType.char_task_type_id).filter(TblFeatureType.char_feature_id==customer_request_query[0][2]).all()
    task_type_query=db_session.query(TblTaskType.txt_agent_worker_version_path,TblTaskType.txt_agent_worker_version).filter(TblTaskType.char_task_type_id==featuretpe_query[0][0]).all()
    tasks_insertion=TblTask(uid_task_id=task_id,char_task_type_id=featuretpe_query[0][0],uid_request_id=request_id,char_feature_id=customer_request_query[0][2],uid_customer_id=customer_request_query[0][0],txt_payload_id=customer_request_query[0][3],txt_agent_worker_version=task_type_query[0][1],txt_agent_worker_version_path=task_type_query[0][0],var_created_by='system',var_modified_by='sysytem',ts_created_datetime=datetime.datetime.now(),ts_modified_datetime=datetime.datetime.now())
    db_session.add(tasks_insertion)
    db_session.commit()
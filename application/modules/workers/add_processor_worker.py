import uuid
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import Tbltasks
import datetime
def addprocessor(request_id):
        session = scoped_session(session_factory)

        # querying data from customer request table

        customer_data = session.query(TblCustomerRequest.txt_payload_id, TblCustomerRequest.uid_customer_id,TblCustomerRequest.char_feature_id,TblCustomerRequest.uid_cluster_id).filter(TblCustomerRequest.uid_request_id == request_id).all()
        payloadid = customer_data[0][0]
        customer_id = customer_data[0][1]
        feature_id = customer_data[0][2]
        cluster_id = customer_data[0][3]

        print "in"


        task_types_id_list = session.query(TblFeatureType.char_task_type_id).filter(TblFeatureType.char_feature_id == feature_id).all()
        task_type_list=[]
        for task_type_ids in task_types_id_list:
            task_type_list.append(task_type_ids[0])

        metatablestatus = session.query(TblMetaTaskStatus.var_task_status, TblMetaTaskStatus.srl_id).all()
        table_status_values = dict(metatablestatus)
        task_status_value = table_status_values['CREATED']
        queryvmcreation=session.query(TblVmCreation.uid_agent_id,TblVmCreation.var_role).filter(TblVmCreation.uid_customer_id==customer_id,TblVmCreation.uid_cluster_id==cluster_id).all()
        agent_id=''
        for agents in queryvmcreation:
                if agents[1] == "nifi_node":
                        agent_id+=agents[0]
        task_type_role_info = session.query(TblTaskType.char_task_type_id,TblTaskType.int_vm_roles,TblTaskType.txt_agent_worker_version_path).filter(TblTaskType.char_task_type_id.in_(task_type_list)).all()
        for task_types in task_type_role_info:
            task_id=uuid.uuid1()
            time_now=datetime.datetime.now()
            tasksinsertion=Tbltasks(uid_task_id=task_id,char_task_type_id=task_types[0],txt_agent_worker_version_path=task_types[2],int_task_status=task_status_value,uid_agent_id=agent_id,var_created_by='system',var_modified_by='system',ts_created_datetime=time_now,ts_modified_datetime=time_now)
            session.add(tasksinsertion)
            session.commit()
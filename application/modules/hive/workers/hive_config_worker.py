from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.util import generate_tasks, find_dep_tasks

import pymongo
from bson.objectid import ObjectId

import uuid
import sys,os
from datetime import datetime
from application import conn_string, mongo_conn_string, db, app
from application.models.models import TblMetaTaskStatus, TblTask, TblAgent, TblCustomerRequest, TblCluster,TblFeatureType, TblTaskType, TblKafkaPublisher, TblKafkaTopic, TblMetaNodeRoles, TblClusterType,TblVmCreation,TblNodeInformation,TblAgent
from application.common.loggerfile import my_logger
from sqlalchemy import and_

def configure_hive(request_id):

    try:
        #request_id = sys.argv[1]
        session = scoped_session(session_factory)

        customer_feature_ids = session.query(TblCustomerRequest.uid_customer_id,TblCustomerRequest.char_feature_id,TblCustomerRequest.txt_dependency_request_id).filter(TblCustomerRequest.uid_request_id==request_id).first()
        customer_id = customer_feature_ids[0]
        feature_id = customer_feature_ids[1]

        dependent_request_id = customer_feature_ids[2]
        payloadid = session.query(TblCustomerRequest.txt_payload_id).filter(TblCustomerRequest.uid_request_id == dependent_request_id).first()
        payload_id = str(payloadid[0])
        mongo_connection = pymongo.MongoClient(mongo_conn_string)
        database_connection = mongo_connection['haas']
        collection_connection = database_connection['highgear']




        hive_node_information = collection_connection.find_one({"_id": ObjectId(payload_id)})
        cluster_id = hive_node_information['cluster_id']
        print cluster_id ,'clsssssssssssssssssssssssussssssssssssssssssssssss'
        #cluster_id = "9a1ada8b-c888-11e8-bace-000c29b9b7fd"

        task_types_list = session.query(TblFeatureType.char_task_type_id).filter(TblFeatureType.char_feature_id==feature_id).all()


        dependenttasks_workerpaths = session.query(TblTaskType.char_task_type_id,TblTaskType.txt_dependency_task_id,TblTaskType.txt_agent_worker_version_path).filter(TblTaskType.char_task_type_id.in_(task_types_list)).all()
        task_dependencytask_workerpaths_dict = {taskid:[dependenttaskid,workerpath] for taskid,dependenttaskid,workerpath in dependenttasks_workerpaths}
        my_logger.debug(task_dependencytask_workerpaths_dict)

        agentid_ip_vmid=session.query(TblVmCreation.uid_agent_id,
                                      TblVmCreation.var_ip,
                                      TblVmCreation.uid_vm_id).filter(TblVmCreation.uid_customer_id == customer_id,
                                                                      TblVmCreation.uid_cluster_id == cluster_id,
                                                                      TblVmCreation.var_role == 'hive').first()
        agent_id = agentid_ip_vmid[0]
        node_ip = agentid_ip_vmid[1]
        vm_id = agentid_ip_vmid[2]
        node_id = str(uuid.uuid1()) #generating uuid for nodeid
        node_information_tbl_insert = TblNodeInformation(uid_node_id = node_id,
                                                         uid_vm_id = vm_id,
                                                         uid_cluster_id = cluster_id,
                                                         uid_customer_id = customer_id,
                                                         char_role = 'hive',
                                                         var_created_by = 'hive-config-worker',
                                                         var_modified_by = 'hive-config-worker',
                                                         ts_created_datetime = datetime.now(),
                                                         ts_modified_datetime = datetime.now())

        session.add(node_information_tbl_insert)
        session.commit()

        agent_tbl_insert =  TblAgent(uid_agent_id = agent_id,
                                     txt_agent_desc = "hive agent",
                                     uid_node_id = node_id,
                                     uid_customer_id = customer_id,
                                     uid_cluster_id = cluster_id,
                                     private_ips = node_ip,
                                     str_agent_version = '1.0',
                                     var_created_by = "hive-config-worker",
                                     var_modified_by = "hive-config-worker",
                                     ts_created_datetime = datetime.now(),
                                     ts_modified_datetime = datetime.now()
                                     )
        session.add(agent_tbl_insert)
        session.commit()

        host_file = ''
        namenode_datanode_hive = session.query(TblVmCreation.var_ip,TblVmCreation.var_name).filter(TblVmCreation.uid_cluster_id==cluster_id).all()
        for each_node in namenode_datanode_hive:
            host_file = host_file+each_node[0]+' '+each_node[1]+'\n'
        #name_node_ip_value = str(name_node_ip[0])
        database_connection.hiveconfig.insert_one({"namenode_ip":host_file})
        #querying the same for object id to insert into tasks table(payloadid)
        namenodeip_query = database_connection.hiveconfig.find_one({"namenode_ip":host_file})
        print namenodeip_query, 'checccccccccccckkkkkkkkkkkkkkkkkkkkk'
        #getting the same objectid to insert into tasks table
        namenodeip_query_objectid = str(namenodeip_query["_id"])


        metatabletaskstatus = session.query(TblMetaTaskStatus.var_task_status, TblMetaTaskStatus.srl_id).all()
        table_status_values = dict(metatabletaskstatus)
        task_status_value = table_status_values['CREATED']


        for tasktypeid, dependent_tasktypeid in task_dependencytask_workerpaths_dict.items():
            task_id = str(uuid.uuid1())
            task_dependencytask_workerpaths_dict[tasktypeid].append(task_id)

        for tasktypeid,dependent_tasktypeid in task_dependencytask_workerpaths_dict.items():
            if dependent_tasktypeid[0] == None:
                my_logger.debug(tasktypeid)
                my_logger.debug(dependent_tasktypeid)
                tasks_tbl_inserts = TblTask(uid_task_id = dependent_tasktypeid[2],
                                            char_task_type_id = tasktypeid,
                                            uid_request_id = request_id,
                                            char_feature_id = feature_id,
                                            uid_customer_id = customer_id,
                                            uid_agent_id = agent_id,
                                            txt_payload_id = namenodeip_query_objectid,
                                            int_task_status = task_status_value,
                                            txt_agent_worker_version_path = dependent_tasktypeid[1],
                                            var_created_by = "hive-config-worker",
                                            var_modified_by = "hive-config-worker",
                                            ts_created_datetime = datetime.now(),
                                            ts_modified_datetime = datetime.now()
                                            )
                session.add(tasks_tbl_inserts)
                session.commit()

            else:
                depe_task_id = task_dependencytask_workerpaths_dict[dependent_tasktypeid[0]][2]
                tasks_tbl_inserts = TblTask(uid_task_id=dependent_tasktypeid[2],
                                            char_task_type_id=tasktypeid,
                                            uid_request_id=request_id,
                                            char_feature_id=feature_id,
                                            uid_customer_id=customer_id,
                                            uid_agent_id=agent_id,
                                            txt_dependent_task_id = depe_task_id,
                                            int_task_status=task_status_value,
                                            txt_agent_worker_version_path=dependent_tasktypeid[1],
                                            var_created_by="hive-config-worker",
                                            var_modified_by="hive-config-worker",
                                            ts_created_datetime=datetime.now(),
                                            ts_modified_datetime=datetime.now()
                                            )
                session.add(tasks_tbl_inserts)
                session.commit()

        my_logger.info("done for hive config worker to generate tasks..............now check tasks table........................................")

    except Exception as e :
	exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(str(e))
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)


if __name__ == '__main__':
    try:
        if len(sys.argv)>=1:
            request_id = sys.argv[1]
            configure_hive(request_id)
        else:
            print "args not passed"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(str(e))
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)


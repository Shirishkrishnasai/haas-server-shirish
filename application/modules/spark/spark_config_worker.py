import io
from ConfigParser import ConfigParser

from azure.storage.file import FileService
from sqlalchemy.orm import scoped_session
from application import session_factory
import pymongo
import uuid
import sys, os
from datetime import datetime
from application import mongo_conn_string
from application.models.models import TblMetaTaskStatus, TblTask,  TblCustomerRequest,  \
    TblFeatureType, TblTaskType, TblMetaNodeRoles, TblVmCreation, \
    TblNodeInformation, TblAgent
from application.common.loggerfile import my_logger


def configure_spark(request_id):
    try:
	print "in configure spark worker ***********************************$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"

        session = scoped_session(session_factory)

        customer_feature_ids = session.query(TblCustomerRequest.uid_customer_id,
                                             TblCustomerRequest.char_feature_id,
                                             TblCustomerRequest.uid_cluster_id).filter(TblCustomerRequest.uid_request_id == request_id).first()
        customer_id, feature_id, cluster_id = customer_feature_ids[0], customer_feature_ids[1], customer_feature_ids[2]


        task_types_list = session.query(TblFeatureType.char_task_type_id).filter(TblFeatureType.char_feature_id == feature_id).all()

        dependenttasks_workerpaths_0 = session.query(TblTaskType.char_task_type_id,
                                                     TblTaskType.txt_dependency_task_id,
                                                     TblTaskType.txt_agent_worker_version_path,
                                                     TblTaskType.int_vm_roles).filter(TblTaskType.char_task_type_id.in_(task_types_list)).all()
        node_roles_query_dict = dict(session.query(TblMetaNodeRoles.srl_id,
                                         TblMetaNodeRoles.vm_roles).all())

###################################################### tasks generation #######################################################################

        dependenttasks_workerpaths = []
        #this for loop generates a list(dependenttasks_workerpaths) that contains role in character and eliminate role integer
        for each_tuplee in dependenttasks_workerpaths_0:
            each_tuplee = list(each_tuplee)
            each_tuplee[3] = node_roles_query_dict[each_tuplee[3]]
            dependenttasks_workerpaths.append(each_tuplee)
        print dependenttasks_workerpaths,'111111111111111111111111111111111111111111'

        nodes_count_dicty = dict(session.query(TblVmCreation.uid_agent_id,
                                               TblVmCreation.var_role).filter(TblVmCreation.uid_cluster_id == cluster_id).all())

        dependenttasks_workerpaths_dicty = {}
        dependenttasks_workerpaths_dicty.update({task_typeid:[dep_task_typeid,worker_path,role] for task_typeid,dep_task_typeid,worker_path,role in dependenttasks_workerpaths})
        tasks_list = []
        #this for loop attaches agentid to the dependenttasks_workerpaths list
        for agid,agrole in nodes_count_dicty.items():
            for ttid,dttid in dependenttasks_workerpaths_dicty.items():
                if(agrole == dttid[2]):
                    taskid = str(uuid.uuid1())
                    tasks_list.append([ttid,dttid[0],agrole,agid,dttid[1],taskid])
        print tasks_list,'222222222222222222222222222222222222222222222222222'
        task_dependencytask_workerpaths_dict_list = []
        for each_listy in tasks_list:
            task_dependencytask_workerpaths_dict_list.append({each_listy[0]:[each_listy[1],each_listy[2],each_listy[3],each_listy[4],each_listy[5]]})
        print task_dependencytask_workerpaths_dict_list,'333333333333333333333333333333333333333333'
        #my_logger.info(task_dependencytask_workerpaths_dict_list)
        task_depttask_dict ={}
        for depttask in task_dependencytask_workerpaths_dict_list:
            for keys,values in depttask.items():
                if values[0] == None:
                    pass
                else:
                    task_depttask_dict.update({keys:[values[0]]})
        print task_depttask_dict,'444444444444444444444444444444444444'
#
        for bigdicty in task_dependencytask_workerpaths_dict_list:
            for keykey,listy in bigdicty.items():
                for tk,dv in task_depttask_dict.items():
                    if dv[0]==keykey:
                        dv.append(listy[4])

        for bigdicty in task_dependencytask_workerpaths_dict_list:
            for keykey,listy in bigdicty.items():
                for tk,dv in task_depttask_dict.items():
                    if tk==keykey:
                        listy.append(dv[1])
        print task_dependencytask_workerpaths_dict_list,'555555555555555555555555555555'




# ##############################################################end of tasks generation #########################################################
#
        agentid_ip_vmid = session.query(TblVmCreation.uid_agent_id,
                                         TblVmCreation.var_ip,
                                         TblVmCreation.uid_vm_id).filter(TblVmCreation.uid_customer_id == customer_id,
                                                                         TblVmCreation.uid_cluster_id == cluster_id,
                                                                         TblVmCreation.var_role == 'spark').first()
        agent_id = agentid_ip_vmid[0]
        node_ip = agentid_ip_vmid[1]
        vm_id = agentid_ip_vmid[2]
        node_id = str(uuid.uuid1())  # generating uuid for nodeid
        node_information_tbl_insert = TblNodeInformation(uid_node_id=node_id,
                                                         uid_vm_id=vm_id,
                                                         uid_cluster_id=cluster_id,
                                                         uid_customer_id=customer_id,
                                                         char_role='spark',
                                                         var_created_by='spark-config-worker',
                                                         var_modified_by='spark-config-worker',
                                                         ts_created_datetime=datetime.now(),
                                                         ts_modified_datetime=datetime.now())

        session.add(node_information_tbl_insert)
        session.commit()

        agent_tbl_insert = TblAgent(uid_agent_id=agent_id,
                                    txt_agent_desc="spark agent",
                                    uid_node_id=node_id,
                                    uid_customer_id=customer_id,
                                    uid_cluster_id=cluster_id,
                                    private_ips=node_ip,
                                    str_agent_version='1.0',
                                    var_created_by="spark-config-worker",
                                    var_modified_by="spark-config-worker",
                                    ts_created_datetime=datetime.now(),
                                    ts_modified_datetime=datetime.now()
                                    )
        session.add(agent_tbl_insert)
        session.commit()

################################################## for spark host file ############################################################

        host_file = ''

        namenode_datanode_spark = session.query(TblVmCreation.var_ip,
                                               TblVmCreation.var_name,
                                               TblVmCreation.var_role,
                                               TblVmCreation.uid_agent_id).filter(TblVmCreation.uid_cluster_id == cluster_id).all()
        for each_node in namenode_datanode_spark:
            host_file = host_file + each_node[0] + ' ' + each_node[1] + '\n'
        cfg = ConfigParser()
        cfg.read('application/config/azure_config.ini')
        account_name = cfg.get('file_storage', 'account_name')
        account_key = cfg.get('file_storage', 'key')
        byte_stream = io.BytesIO(host_file)
        no_of_bytes = len(host_file)
        file_service = FileService(account_name=account_name, account_key=account_key)
        file_service.create_file_from_stream(share_name=str(cluster_id),
                                             directory_name="hostfile",
                                             file_name="host",
                                             stream=byte_stream,
                                             count=no_of_bytes)
        # Appending hosts payload to list
        print "\n\n\n\n\n", "successssss", "\n\n\n\n\n\n\n"
###################################################### for name node ip ##############################################

        namenode_ip = [nnode[0] + ' ' + nnode[1] + '\n' for nnode in namenode_datanode_spark if nnode[2] == 'namenode'][0]


        mongo_connection = pymongo.MongoClient(mongo_conn_string)
        database_connection = mongo_connection['haas']

        database_connection.sparkconfig.insert_one({"namenode_ip": namenode_ip})

        namenodeip_query = database_connection.sparkconfig.find_one({"namenode_ip": namenode_ip})
        namenodeip_query_objectid = str(namenodeip_query["_id"])
############################################# spark host payload generation over ###############################################

        metatabletaskstatus = session.query(TblMetaTaskStatus.var_task_status, TblMetaTaskStatus.srl_id).all()
        table_status_values = dict(metatabletaskstatus)
        task_status_value = table_status_values['CREATED']
        for each_dicty in task_dependencytask_workerpaths_dict_list:
            for tasktype,deptasktypelist in each_dicty.items():
                if deptasktypelist[1] == 'spark':
                    if deptasktypelist[0] == None:
                        tasks_tbl_inserts = TblTask(uid_task_id=deptasktypelist[4],
                                                    char_task_type_id=tasktype,
                                                    uid_request_id=request_id,
                                                    char_feature_id=feature_id,
                                                    uid_customer_id=customer_id,
                                                    uid_agent_id=agent_id,
                                                    txt_payload_id=namenodeip_query_objectid,
                                                    int_task_status=task_status_value,
                                                    txt_agent_worker_version_path=deptasktypelist[3],
                                                    var_created_by="spark-config-worker",
                                                    var_modified_by="spark-config-worker",
                                                    ts_created_datetime=datetime.now(),
                                                    ts_modified_datetime=datetime.now()
                                                    )
                        session.add(tasks_tbl_inserts)
                        session.commit()

                    elif tasktype == 'F14_T4':
                        tasks_tbl_inserts = TblTask(uid_task_id=deptasktypelist[4],
                                                    char_task_type_id=tasktype,
                                                    uid_request_id=request_id,
                                                    char_feature_id=feature_id,
                                                    uid_customer_id=customer_id,
                                                    uid_agent_id=agent_id,
                                                    txt_dependent_task_id=deptasktypelist[5],
                                                    txt_payload_id=namenodeip_query_objectid,
                                                    int_task_status=task_status_value,
                                                    txt_agent_worker_version_path=deptasktypelist[3],
                                                    var_created_by="spark-config-worker",
                                                    var_modified_by="spark-config-worker",
                                                    ts_created_datetime=datetime.now(),
                                                    ts_modified_datetime=datetime.now()
                                                    )
                        session.add(tasks_tbl_inserts)
                        session.commit()


                    else:
                        tasks_tbl_inserts = TblTask(uid_task_id=deptasktypelist[4],
                                                    char_task_type_id=tasktype,
                                                    uid_request_id=request_id,
                                                    char_feature_id=feature_id,
                                                    uid_customer_id=customer_id,
                                                    uid_agent_id=agent_id,
                                                    txt_dependent_task_id=deptasktypelist[5],
                                                    int_task_status=task_status_value,
                                                    txt_agent_worker_version_path=deptasktypelist[3],
                                                    var_created_by="spark-config-worker",
                                                    var_modified_by="spark-config-worker",
                                                    ts_created_datetime=datetime.now(),
                                                    ts_modified_datetime=datetime.now()
                                                    )
                        session.add(tasks_tbl_inserts)
                        session.commit()
                else:
                    tasks_tbl_inserts = TblTask(uid_task_id=deptasktypelist[4],
                                                char_task_type_id=tasktype,
                                                uid_request_id=request_id,
                                                char_feature_id=feature_id,
                                                uid_customer_id=customer_id,
                                                uid_agent_id=deptasktypelist[2],
                                                int_task_status=task_status_value,
                                                txt_agent_worker_version_path=deptasktypelist[3],
                                                var_created_by="spark-config-worker",
                                                var_modified_by="spark-config-worker",
                                                ts_created_datetime=datetime.now(),
                                                ts_modified_datetime=datetime.now()
                                                )
                    session.add(tasks_tbl_inserts)
                    session.commit()

        my_logger.info("done for spark config worker to generate tasks..............now check tasks table........................................")
#
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(str(e))
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        session.close()
        mongo_connection.close()


if __name__ == '__main__':
    # try:
    if len(sys.argv) >= 1:
        request_id = sys.argv[1]
        configure_spark(request_id)
    else:
        my_logger.info("args not passed")
    #except Exception as e:
     #   exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     my_logger.error(str(e))
#     my_logger.error(exc_type)
#     my_logger.error(fname)
#     my_logger.error(exc_tb.tb_lineno)





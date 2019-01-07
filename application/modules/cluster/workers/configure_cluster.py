from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.util import generate_tasks, find_dep_tasks
import pymongo
import uuid
import sys
import datetime
from application import conn_string, mongo_conn_string, db, app
from application.models.models import TblMetaTaskStatus, TblTask, TblAgent, TblCustomerRequest, TblCluster, \
    TblFeatureType, TblTaskType, TblKafkaPublisher, TblKafkaTopic, TblMetaNodeRoles, TblClusterType, TblVmCreation, \
    TblNodeInformation, TblAgent
from application.common.loggerfile import my_logger



def configure_cluster():
    # try:
    my_logger.info("in cluster configure worker")
    request_id = sys.argv[1]
    session = scoped_session(session_factory)

    # querying data from customer request table

    customer_data = session.query(TblCustomerRequest.txt_payload_id, TblCustomerRequest.uid_customer_id,
                                  TblCustomerRequest.char_feature_id, TblCustomerRequest.uid_cluster_id).filter(
        TblCustomerRequest.uid_request_id == request_id).all()
    payloadid = customer_data[0][0]
    customer_id = customer_data[0][1]
    feature_id = customer_data[0][2]
    # cluster_id = customer_data[0][3]
    cluster_id = 'ae945516-09bc-11e9-b4fe-000c29da5704'


    task_types_id_list = session.query(TblFeatureType.char_task_type_id).filter(
        TblFeatureType.char_feature_id == feature_id).all()
    print "222222222222222222222222222", task_types_id_list
    task_type_list = []
    for task_type_ids in task_types_id_list:
        task_type_list.append(task_type_ids[0])

    task_type_role_info = session.query(TblTaskType.char_task_type_id, TblTaskType.int_vm_roles).filter(
        TblTaskType.char_task_type_id.in_(task_type_list)).all()
    print "3333333333333333333333333333333", task_type_role_info

    task_types_info_dict = {}
    for task_types in task_type_role_info:
        task_types_info_list = session.query(TblMetaNodeRoles.vm_roles).filter(
            TblMetaNodeRoles.srl_id == task_types[1]).all()
        task_types_info_dict[task_types[0]] = task_types_info_list[0][0]
    print "444444444444444444444444444444444444", task_types_info_dict

    print "data querying from vm creation table"

    vm_roles_query = session.query(TblVmCreation.uid_cluster_id, TblVmCreation.uid_agent_id, TblVmCreation.var_role,
                                   TblVmCreation.var_ip, TblVmCreation.uid_vm_id).filter(
        TblVmCreation.uid_customer_id == customer_id, TblVmCreation.uid_cluster_id == cluster_id,
        TblVmCreation.bool_edge == 'f').all()
    print "5555555555555555555555555555555555555555555555555", vm_roles_query

    print "generating cluster_information_dictionary for task generation method"

    cluster_information_dict = {}
    for cluster_nodes_information in vm_roles_query:
        cluster_information_dict[cluster_nodes_information[1]] = cluster_nodes_information[2]
        print "passing parameters to task generation"
    print "task type", task_types_info_dict, cluster_information_dict
    task_generator = generate_tasks(dict_nodes=cluster_information_dict, dict_tasktypes=task_types_info_dict)
    print "Got Task_genrator", task_generator

    print "inserting into node_information table"

    time_now = datetime.datetime.now()
    for vm_information in vm_roles_query:
        node_id = str(uuid.uuid1())
        #            fqdn_string=str(vm_information[5]) + ".kwartile"
        print node_id, "Got Not Id"
        node_information_insertion = TblNodeInformation(uid_node_id=node_id, uid_vm_id=vm_information[4],
                                                        uid_cluster_id=cluster_id, uid_customer_id=customer_id,
                                                        char_role=vm_information[2], var_created_by='system',
                                                        var_modified_by='system', ts_created_datetime=time_now,
                                                        ts_modified_datetime=time_now)
        session.add(node_information_insertion)
        session.commit()

    print "inserting into agent table"

    node_information_query = session.query(TblNodeInformation.uid_node_id, TblNodeInformation.uid_vm_id).filter(
        TblNodeInformation.uid_customer_id == customer_id, TblNodeInformation.uid_cluster_id == cluster_id).all()
    print node_information_query, "node information has nodeid,vmid filtered by customerid and clusterid.........it gets all the records"

    for vm_creation_information in vm_roles_query:
        print "111111111111111111111111111111111"
        #	    print vm_creation_information
        for node_information_individual in node_information_query:
            #		print vm_creation_information[4] ,node_information_individual[1],vm_creation_information
            if vm_creation_information[4] == node_information_individual[1]:
                print vm_creation_information[1], "theeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeee"
                agent_insertion = TblAgent(uid_agent_id=vm_creation_information[1],
                                           uid_node_id=node_information_individual[0], uid_cluster_id=cluster_id,
                                           uid_customer_id=customer_id, private_ips=vm_creation_information[3],
                                           var_created_by='system', var_modified_by='system',
                                           ts_created_datetime=time_now, ts_modified_datetime=time_now)
                session.add(agent_insertion)
    session.commit()
    print "heeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

    # inserting into kafka tables

    topiclist = ['tasks', 'taskstatus', 'metrics']
    for individualtopic in topiclist:
        topicid = str(uuid.uuid1())
        topicname = individualtopic + "_" + str(customer_id) + "_" + str(cluster_id)
        kafka_topic_name_insertion = TblKafkaTopic(uid_topic_id=topicid, var_topic_name=topicname,
                                                   var_topic_type=individualtopic, var_created_by='system',
                                                   var_modified_by='system', ts_created_datetime=time_now,
                                                   ts_modified_datetime=time_now)
        session.add(kafka_topic_name_insertion)
        session.commit()
        kafka_topic_id_insertion = TblKafkaPublisher(uid_topic_id=topicid, uid_cluster_id=cluster_id,
                                                     uid_customer_id=customer_id, var_created_by='system',
                                                     var_modified_by='system', ts_created_datetime=time_now,
                                                     ts_modified_datetime=time_now)
        session.add(kafka_topic_id_insertion)
        session.commit()

    print "declairing  strings for slaves,host,configuration to append ips"

    host_dns_string = ''
    slaves_string = ''
    namenode_payload = ''
    for cluster_nodes_information in vm_roles_query:

        # generate host string

        host_dns_string += cluster_nodes_information[3]

        # generate slaves string

        if cluster_nodes_information[2] != 'namenode':
            slaves_string += cluster_nodes_information[3]

        # generate a string for namenode ip

        if cluster_nodes_information[2] == 'namenode':
            namenode_payload += cluster_nodes_information[3]
    # calling task generation method

    # inserting slaves string to mongo db

    mongo_connection = pymongo.MongoClient(mongo_conn_string)
    database_connection = mongo_connection['haas']
    slaves_content = {"file_name": "slaves.txt", "content": slaves_string}
    database_connection.slaves.insert_one(slaves_content)
    slaves_content_query = database_connection.slaves.find_one(slaves_content)
    slaves_content_objectid = str(slaves_content_query["_id"])

    print "Appending slaves string object id into list"

    for task_information in task_generator:
        if task_information[2] == 'F1_T3':
            task_information.append(slaves_content_objectid)

    # Inserting hostdns string to mongodb

    host_content = {"file_name": "host.txt", "content": host_dns_string}
    database_connection.hostdns.insert_one(host_content)
    host_content_query = database_connection.hostdns.find_one(host_content)
    host_content_objectid = str(host_content_query["_id"])

    # Appending hosts payload to list

    for task_information in task_generator:
        if task_information[2] in ('F1_T1', 'F1_T2'):
            task_information.append(host_content_objectid)
    # inserting name node ip mongo

    database_connection.configurenamenode.insert_one({"content": namenode_payload})
    namenode_ip_info = database_connection.configurenamenode.find_one({"content": namenode_payload})
    namenode_ip_payload = namenode_ip_info["_id"]

    # Appending configure payload to list

    for task_information in task_generator:
        if task_information[2] in ('F1_T4', 'F1_T5'):
            task_information.append(namenode_ip_payload)

    # generating task type mapping dict to give input for dependency task method

    task_tasktype_mapping_dict = {}
    for task_information in task_generator:
        task_tasktype_mapping_dict[task_information[1]] = task_information[2]

    # generating list dependent task dict to give input for dependency task method

    list_dependent_tasks_dict = {}
    dependency_task_types_info = session.query(TblTaskType.char_task_type_id,
                                               TblTaskType.txt_dependency_task_id).filter(
        TblTaskType.char_task_type_id.in_(task_type_list)).all()

    for task_type_dependency in dependency_task_types_info:
        if task_type_dependency[1] == None:
            list_dependent_tasks_dict[task_type_dependency[0]] = []
        else:
            list_of_dependencies_string = task_type_dependency[1].split(",")
            list_of_dependencies_string = map(str, list_of_dependencies_string)
            list_dependent_tasks_dict[task_type_dependency[0]] = list_of_dependencies_string
    dependent_task_info = find_dep_tasks(dict_tasktypes=list_dependent_tasks_dict,
                                         dict_tasks=task_tasktype_mapping_dict)

    # inserting dependency tasks into list

    for task_information in task_generator:
        for taskid, dependency_tasks in dependent_task_info.items():
            if task_information[1] == taskid:
                listoftasks = ''
                for taskids in dependency_tasks:
                    listoftasks += '"' + taskids + '",'
                task_information.append(listoftasks[:-1])

    # adding worker path for each task in list

    task_path = session.query(TblTaskType.char_task_type_id, TblTaskType.txt_agent_worker_version_path).filter(
        TblTaskType.char_task_type_id.in_(task_type_list)).all()
    print "Task_Path", task_path
    for task_information in task_generator:
        for task_type_information in task_path:
            if task_information[2] == task_type_information[0]:
                task_information.append(task_type_information[1])

    # quering data from meta status table

    metatablestatus = session.query(TblMetaTaskStatus.var_task_status, TblMetaTaskStatus.srl_id).all()
    table_status_values = dict(metatablestatus)
    task_status_value = table_status_values['CREATED']

    print "insertion into task table", task_generator

    for task_information in task_generator:
        time_now = datetime.datetime.now()
        if len(task_information) == 7:
            if task_information[5] == '':
                task_insertion = TblTask(uid_task_id=str(task_information[1]),
                                         char_task_type_id=task_information[2], int_task_status=task_status_value,
                                         uid_request_id=str(request_id), char_feature_id=feature_id,
                                         uid_customer_id=str(customer_id), txt_payload_id=str(task_information[4]),
                                         uid_agent_id=str(task_information[0]),
                                         txt_agent_worker_version_path=task_information[6], var_created_by='system',
                                         var_modified_by='system', ts_created_datetime=time_now,
                                         ts_modified_datetime=time_now)
            else:
                task_insertion = TblTask(uid_task_id=str(task_information[1]),
                                         char_task_type_id=task_information[2], int_task_status=task_status_value,
                                         uid_request_id=str(request_id), char_feature_id=feature_id,
                                         uid_customer_id=str(customer_id), txt_payload_id=str(task_information[4]),
                                         txt_dependent_task_id=task_information[5],
                                         uid_agent_id=str(task_information[0]),
                                         txt_agent_worker_version_path=task_information[6], var_created_by='system',
                                         var_modified_by='system', ts_created_datetime=time_now,
                                         ts_modified_datetime=time_now)
        else:
            if task_information[4] == '':
                task_insertion = TblTask(uid_task_id=str(task_information[1]),
                                         char_task_type_id=task_information[2], int_task_status=task_status_value,
                                         uid_request_id=str(request_id), char_feature_id=feature_id,
                                         uid_customer_id=str(customer_id), uid_agent_id=task_information[0],
                                         txt_agent_worker_version_path=task_information[5], var_created_by='system',
                                         var_modified_by='system', ts_created_datetime=time_now,
                                         ts_modified_datetime=time_now)
            else:
                task_insertion = TblTask(uid_task_id=str(task_information[1]),
                                         char_task_type_id=task_information[2], int_task_status=task_status_value,
                                         uid_request_id=str(request_id), char_feature_id=feature_id,
                                         uid_customer_id=str(customer_id),
                                         txt_dependent_task_id=task_information[4],
                                         uid_agent_id=str(task_information[0]),
                                         txt_agent_worker_version_path=task_information[5], var_created_by='system',
                                         var_modified_by='system', ts_created_datetime=time_now,
                                         ts_modified_datetime=time_now)
        print task_insertion, "\n"
        session.add(task_insertion)
        session.commit()

# except Exception as e:
#   my_logger.error(e)
configure_cluster()
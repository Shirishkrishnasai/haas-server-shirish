import sys
import psycopg2
import pymongo
from bson.objectid import ObjectId
import uuid
import time
import json
import datetime
from application import app, conn_string, mongo_conn_string
# from application.modules.azure.subnetcreation import create_subnet
from application.modules.azure.createvm import vmcreation


# requestid=sys.argv
# request_id=requestid[1]
def serverworker(request_id):
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("set search_path to highgear;")
    customerdata = "select txt_payload_id,uid_customer_id,char_feature_id from tbl_customer_request where uid_request_id=" + str(
        request_id)
    print(request_id)
    cur.execute(customerdata)
    customer_data = cur.fetchall()

    payloadid = customer_data[0][0]
    customer_id = customer_data[0][1]
    feature_id = customer_data[0][2]
    cluster_id = uuid.uuid1()
    cluster_statement = "insert into tbl_cluster (uid_cluster_id,uid_customer_id) values ('" + str(
        cluster_id) + "'," + str(customer_id) + ")"
    cur.execute(cluster_statement)
    conn.commit()
    topiclist = ['tasks', 'taskstatus', 'metrics']
    for individualtopic in topiclist:
        topicid = str(uuid.uuid1())
        topicname = individualtopic + "_" + str(customer_id) + "_" + str(cluster_id)
        insert_in_kafka_topic="insert into tbl_kafka_topic (uid_topic_id,var_topic_name,var_topic_type) values('"+str(topicid)+"',"+str(topicname)+",'"+str(individualtopic)+"')"
        #kafka_topic_name_insertion = TblKafkaTopic(uid_topic_id=str(topicid), var_topic_name=topicname,var_topic_type=individualtopic)
        #db.session.add(kafka_topic_name_insertion)
        #db.session.commit()
        cur.execute(insert_in_kafka_topic)
        cur.commit()
        #kafka_topic_id_insertion = TblKafkaPublisher(uid_topic_id=str(topicid), uid_cluster_id=cluster_id,uid_customer_id=customer_id)
        insert_into_kafka_publisher="insert into tbl_kafka_publisher (uid_topic_id,uid_cluster_id,uid_customer_id) values('"+str(topicid)+"','"+str(cluster_id)+"','"+str(customer_id)+"')"
        #db.session.add(kafka_topic_id_insertion)
        #db.session.commit()
        cur.execute(insert_into_kafka_publisher)
        cur.commit()
    print(payloadid, "payload")
    myclient = pymongo.MongoClient(mongo_conn_string)
    mydb = myclient['haas']
    mycol = mydb['highgear']
    querystatment = mycol.find_one({"_id": ObjectId(payloadid)})
    print(querystatment.values())
    # subnet_information=create_subnet(customer_id)
    
   
    slave = open("slaves.txt", "w")
    host = open("hosts.txt", "w")
    tasktypeidstatement = "select char_task_type_id from tbl_feature_type where char_feature_id=" + str(feature_id)
    print tasktypeidstatement
    cur.execute(tasktypeidstatement)
    tasktids = cur.fetchall()
    print tasktids
    listoftasktypeids = []
    print(querystatment.values())
    for values in querystatment.values():
        value = str(values)
        if value != payloadid:
            agentid = uuid.uuid1()
            agent_version = '1.0'
            task_id = uuid.uuid1()
            #            time.sleep(30)
            myclient = pymongo.MongoClient(mongo_conn_string)
            mydb = myclient['haas']
            vm_information = vmcreation(clusterid=cluster_id, customerid=customer_id, agentid=agentid,
                                        role=values["role"])
            time.sleep(10)
            #	    vmdata=vm_information
            # print(vmdata)
            print(vm_information, "vminformation")
            vm_id = vm_information["vm_id"]
            vm_ip = vm_information["vm_ip"]

            vm_fqdn = str(vm_information["name"]) + ".kwartile"

            # slave.write("%s\n" % vm_ip)
            host.write("%s %s\n" % (vm_ip, vm_fqdn))
            
           
           
            registered_datetime = datetime.datetime.now()
            insertstatement = "insert into tbl_agent (uid_agent_id,uid_cluster_id,uid_customer_id,ts_created_datetime) values (" + "'" + str(agentid) + "'" + ",'" + str(cluster_id) + "'," + str(
                customer_id) + ",'" + str(registered_datetime) + "')"
            cur.execute(insertstatement)
            conn.commit()
            meta_task_status_query = "select srl_id,var_task_status from tbl_meta_task_status where var_task_status='CREATED'"
            cur.execute(meta_task_status_query)
            meta_task_status_data = cur.fetchall()
            for tasktypeid in tasktids:
                print tasktypeid
                listoftasktypeids.append(str(tasktypeid[0]))
            tupleoftasktypeids = tuple(listoftasktypeids)
            print tupleoftasktypeids
            if values["role"] == "namenode":
                print request_id, "request_id"
                statement = "select char_task_type_id,txt_agent_worker_version_path,txt_agent_worker_version from tbl_task_types where char_task_type_id in " + str(
                    tupleoftasktypeids) + " and var_role='namenode'"
                cur.execute(statement)
                taskids = cur.fetchall()
                namenode_tasks = taskids
                mydb.configurenamenode.insert_one({"content": vm_ip})
                nodequerystatment = mydb.configurenamenode.find_one({"content": vm_ip})
                namenodepayloadid = nodequerystatment["_id"]
                print(namenode_tasks, "task_ids")
                for tasks in namenode_tasks:
                    task_id = uuid.uuid1()
                    assigned_time = datetime.datetime.now()
                    task_type_id = tasks[0]
                    worker_version_path = tasks[1]
                    worker_version = tasks[2]
                    insert = "insert into tbl_tasks (char_task_type_id,uid_task_id,uid_request_id,char_feature_id,uid_agent_id,uid_customer_id,ts_assigned_time,txt_agent_worker_version_path,txt_agent_worker_version,int_task_status) values (" + str(
                        task_type_id) + ",'" + str(task_id) + "'," + str(request_id) + "," + str(
                        feature_id) + ",'" + str(agentid) + "'," + str(customer_id) + "," + "'" + str(
                        assigned_time) + "','" + str(worker_version_path) + "','" + str(worker_version) + "',"+str(meta_task_status_data[0][0])+")"
                    cur.execute(insert)
                    conn.commit()
            if values["role"] == "datanode":
                statement = "select char_task_type_id,txt_agent_worker_version_path,txt_agent_worker_version from tbl_task_types where char_task_type_id in " + str(
                    tupleoftasktypeids) + "and var_role='datanode'"
                print(statement)
                cur.execute(statement)
                taskids = cur.fetchall()
                datanode_tasks = taskids
                slave.write("%s\n" % vm_ip)
                for tasks in datanode_tasks:
                    task_id = uuid.uuid1()
                    assigned_time = datetime.datetime.now()
                    tast_type_id = tasks[0]
                    worker_version_path = tasks[1]
                    worker_version = tasks[2]
                    insert = "insert into tbl_tasks (char_task_type_id,uid_task_id,uid_request_id,char_feature_id,uid_agent_id,uid_customer_id,txt_agent_worker_version_path,txt_agent_worker_version,int_task_status) values (" + str(
                        tast_type_id) + ",'" + str(task_id) + "'," + str(request_id) + "," + str(
                        feature_id) + ",'" + str(agentid) + "'," + str(customer_id) + ",'"  + str(worker_version_path) + "','" + str(worker_version) + "',"+str(meta_task_status_data[0][0])+")"
                    cur.execute(insert)
                    conn.commit()
    slave.close()
    host.close()
    opendns = open("hosts.txt")
    openslave = open("slaves.txt")
    slave_text = openslave.read()
    slaves_content = {"file_name": "slaves.txt", "content": slave_text}
    mydb.slaves.insert_one(slaves_content)
    querystatment = mydb.slaves.find_one(slaves_content)
    slave_objectid = str(querystatment["_id"])
    querytasktypeids = "select char_task_type_id from tbl_task_types where txt_description=" + "'" + "slaves file" + "'"
    cur.execute(querytasktypeids)
    tasktypeids_list = cur.fetchall()
    print(tasktypeids_list, 1111)
    tasktypeids = tasktypeids_list[0][0]
    task_idsquery = "select uid_task_id from tbl_tasks where char_task_type_id=3"
    cur.execute(task_idsquery)
    task_idslist = cur.fetchall()
    print(task_idslist)
    print(task_idslist)
    slavetask_list = []
    for tasks in task_idslist:
        slavetask_list.append(tasks[0])
    print(slavetask_list)
    if len(slavetask_list) == 1:
        update_payload = "update tbl_tasks set txt_payload_id='" + slave_objectid + "' where uid_task_id  ='" + \
                         slavetask_list[0] + "'"
    else:
        update_payload = "update tbl_tasks set txt_payload_id='" + slave_objectid + "' where uid_task_id in " + str(
            tuple(slavetask_list))
    cur.execute(update_payload)
    conn.commit()
    host_text = opendns.read()
    host_content = {"file_name": "host.txt", "content": host_text}
    mydb.hostdns.insert_one(host_content)
    querystatment = mydb.hostdns.find_one(host_content)
    slave_objectid = str(querystatment["_id"])
    hosttasktypeids = "select char_task_type_id from tbl_task_types where txt_description=" + "'" + "copy host text file" + "'"
    cur.execute(hosttasktypeids)
    host_tasktypeids_list = cur.fetchall()
    host_tasktypeids = host_tasktypeids_list[0][0]
    host_task_idsquery = "select uid_task_id from tbl_tasks where char_task_type_id in (1,2)"
    cur.execute(host_task_idsquery)
    host_task_idslist = cur.fetchall()
    host_task_list = []
    for host_tasks in host_task_idslist:
        host_task_list.append(host_tasks[0])
    if len(host_task_list) == 1:
        update_payload_hosts = "update tbl_tasks set txt_payload_id='" + slave_objectid + "' where uid_task_id=" + \
                               host_task_list[0]
    else:
        update_payload_hosts = "update tbl_tasks set txt_payload_id='" + slave_objectid + "' where uid_task_id in " + str(
            tuple(host_task_list))
    cur.execute(update_payload_hosts)
    conn.commit()
    nodetasktypeids = "select char_task_type_id from tbl_task_types where txt_description=" + "'" + "workerconfiguration" + "'"
    cur.execute(nodetasktypeids)
    node_tasktypeids_list = cur.fetchall()
    node_tasktypeids = node_tasktypeids_list[0][0]
    node_task_idsquery = "select uid_task_id from tbl_tasks where char_task_type_id in (F1_T4,F1_T5)"
    cur.execute(node_task_idsquery)
    node_task_idslist = cur.fetchall()
    node_task_list = []
    for node_tasks in node_task_idslist:
        node_task_list.append(node_tasks[0])
    vmstatement = "select uid_vm_id from tbl_node_information where uid_cluster_id='" + str(
        cluster_id) + "' and char_role='namenode'"
    cur.execute(vmstatement)
    vmids = cur.fetchall()
    vmid = vmids[0][0]
    print(vmid)

    # node_content={"file_name":"configuration.txt","content":vm_ip}
    # mydb.configurenamenode.insert_one(node_content)
    # nodequerystatment = mydb.configurenamenode.find_one(node_content)
    # namenodepayloadid = nodequerystatment["_id"]
    if len(node_task_list) == 1:
        update_payload_hosts = "update tbl_tasks set txt_payload_id='" + str(
            namenodepayloadid) + "' where uid_task_id = '" + str(node_task_list[0]) + "'"
    else:
        update_payload_hosts = "update tbl_tasks set txt_payload_id='" + str(
            namenodepayloadid) + "' where uid_task_id in " + str(tuple(node_task_list))
    cur.execute(update_payload_hosts)
    conn.commit()

    dependent_tasks_list = [['F1_T1', []], ['F1_T2', []], ['F1_T3', []], ['F1_T4', []], ['F1_T5', []], ['F1_T6', ['F1_T1','F1_T3']],
                            ['F1_T7', []], ['F1_T8', ['F1_T7']], ['F1_T9', ['F1_T1','F1_T2','F1_T4','F1_T8']], ['F1_T10', ['F1_T9']],
                            ['F1_T11', ['F1_T10']]]
    for dependenttasks in dependent_tasks_list:
        if dependenttasks[1] == []:
            print("null")
        else:
            print(dependenttasks[1])
            if len(dependenttasks[1]) == 1:

                taskidliststatement = "select uid_task_id from tbl_tasks where char_task_type_id = " + str(
                    dependenttasks[1][0]) + " and uid_request_id=" + str(request_id)
                cur.execute(taskidliststatement)
                taskid = cur.fetchall()
                listoftasks = ''
                for task in taskid:
                    listoftasks += '"' + task[0] + '",'
                splittask = listoftasks.split(",")
                print(splittask, "length")

                tasksstring = "'" + listoftasks[:-1] + "'"
            else:

                taskidliststatement = "select uid_task_id from tbl_tasks where char_task_type_id in " + str(
                    tuple(dependenttasks[1])) + " and uid_request_id=" + str(request_id)
                cur.execute(taskidliststatement)
                taskid = cur.fetchall()
                listoftasks = ''
                for task in taskid:
                    listoftasks += '"' + task[0] + '",'
                splittask = listoftasks.split(",")
                print(len(splittask), "length")
                tasksstring = "'" + listoftasks[:-1] + "'"

            updatedependenttasks = "update tbl_tasks set txt_dependent_task_id =" + str(
                tasksstring) + " where char_task_type_id=" + str(dependenttasks[0])
            print(updatedependenttasks)
            cur.execute(updatedependenttasks)
            conn.commit()
            cur.execute("select txt_dependent_task_id from tbl_tasks where srl_id=452")
            dependenttaskid = cur.fetchall()


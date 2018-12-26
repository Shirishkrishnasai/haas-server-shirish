import sys
import psycopg2
import pymongo
from bson.objectid import ObjectId
import uuid
import json
import datetime
from application import app,conn_string,mongo_conn_string
#from application.modules.azure.subnetcreation import create_subnet
from application.modules.azure.createvm import vmcreation
#requestid=sys.argv
#request_id=requestid[1]
def serverworker(request_id):

    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("set search_path to highgear;")
    customerdata="select txt_payload_id,lng_customer_id,lng_feature_id from tbl_customer_request where uid_request_id="+str(request_id)
    print(request_id)
    cur.execute(customerdata)
    customer_data=cur.fetchall()

    payloadid=customer_data[0][0]
    customer_id=customer_data[0][1]
    feature_id=customer_data[0][2]
    cluster_id =  uuid.uuid1()
    cluster_statement="insert into tbl_cluster (uid_cluster_id,lng_customer_id) values ('"+str(cluster_id)+"',"+str(customer_id)+")"
    cur.execute(cluster_statement)
    conn.commit()


    print(payloadid,"payload")
    myclient = pymongo.MongoClient(mongo_conn_string)
    mydb = myclient['local']
    mycol = mydb['client']
    querystatment=mycol.find_one({"_id" : ObjectId(payloadid)})
    print(querystatment.values())
   # subnet_information=create_subnet(customer_id)
    node_id=2
    network_id='haas'
    resource_group_id='haas'
    n=10
    list1=[]
    list2=[]
    slave=open("slaves.txt","w")
    host=open("hosts.txt","w")
    tasktypeidstatement = "select lng_task_type_id from tbl_feature_type where lng_feature_id=" + str(feature_id)
    print tasktypeidstatement
    cur.execute(tasktypeidstatement)
    tasktids = cur.fetchall()
    print tasktids
    listoftasktypeids = []
    print(querystatment.values())
    for values in querystatment.values():
        value=str(values)
        if value != payloadid:
            agentid=uuid.uuid1()
            agent_version='1.0'
            task_id=uuid.uuid1()
            vm_information=vmcreation(clusterid=cluster_id,customerid=customer_id,agentid=agentid,role=values["role"])
#	    vmdata=vm_information
	    #print(vmdata)
            print(vm_information,"vminformation")
            vm_id=vm_information["vm_id"]
            vm_fqdn=str(vm_information["name"])+".kwartile"
            slave.write("%s\n" % vm_id)
            host.write("%s %s\n" % (vm_id,vm_fqdn))
            vm_insert="insert into tbl_vm_information (uid_vm_id,lng_customer_id,var_group_name,var_virtual_network_name,lng_subnet_id) values ('"+str(vm_id)+"','"+str(customer_id)+"','"+str(resource_group_id)+"','"+str(network_id)+"',"+str(node_id)+")"
            print vm_insert
            cur.execute(vm_insert)
            conn.commit()
            querynodeids="select srl_id from tbl_vm_information where uid_vm_id='"+str(vm_id)+"'"
            cur.execute(querynodeids)
            srl_ids=cur.fetchall()
            vm_node_id=srl_ids[0][0]

            node_statement="insert into tbl_node_information (uid_vm_id,lng_customer_id,uid_cluster_id,txt_fqdn,char_role) values ('"+str(vm_id)+"',"+str(customer_id)+",'"+str(cluster_id)+"','"+str(vm_fqdn)+"'"+",'"+str(values["role"])+"')"
            cur.execute(node_statement)
            conn.commit()
            nodeidquery="select srl_id from tbl_node_information where uid_vm_id='"+str(vm_id)+"'"
            cur.execute(nodeidquery)
            srl_node_ids = cur.fetchall()
            srl_node_id = srl_node_ids[0][0]
            registered_datetime=datetime.datetime.now()
            insertstatement = "insert into tbl_agent (lng_node_id,uid_agent_id,uid_cluster_id,lng_customer_id,ts_registered_datetime) values (" +str(srl_node_id)+","+"'" + str(agentid) + "'" + ",'" +str(cluster_id)+"',"+ str(customer_id)+",'" +str(registered_datetime)+"')"
            cur.execute(insertstatement)
            conn.commit()

            for tasktypeid in tasktids:
                print tasktypeid
                listoftasktypeids.append(str(tasktypeid[0]))
            tupleoftasktypeids=tuple(listoftasktypeids)
            print tupleoftasktypeids
            if values["role"] == "namenode":
                print request_id,"request_id"
                statement="select lng_task_type_id,txt_agent_worker_version_path,txt_agent_worker_version from tbl_task_types where lng_task_type_id in " +str(tupleoftasktypeids)+" and var_role='namenode'"
                cur.execute(statement)
                taskids=cur.fetchall()
                namenode_tasks=taskids
                mydb.namenode.insert_one({"content":vm_id})
                nodequerystatment = mydb.namenode.find_one({"content":vm_id})
                namenodepayloadid=nodequerystatment["_id"]
                print(namenode_tasks,"task_ids")
                for tasks in namenode_tasks:
                    task_id = uuid.uuid1()
                    assigned_time = datetime.datetime.now()
                    task_type_id=tasks[0]
                    worker_version_path=tasks[1]
                    worker_version=tasks[2]
                    insert="insert into tbl_tasks (lng_task_type_id,uid_task_id,uid_request_id,lng_feature_id,uid_agent_id,lng_customer_id,ts_assigned_time,txt_agent_worker_version_path,txt_agent_worker_version) values ("+str(task_type_id)+",'"+str(task_id)+"',"+str(request_id)+","+str(feature_id)+",'"+str(agentid)+"',"+str(customer_id)+","+"'"+str(assigned_time)+"','"+str(worker_version_path)+"','"+str(worker_version)+"')"
                    cur.execute(insert)
                    conn.commit()
            if values["role"] == "datanode":
                statement="select lng_task_type_id,txt_agent_worker_version_path,txt_agent_worker_version from tbl_task_types where lng_task_type_id in "+str(tupleoftasktypeids)+"and var_role='datanode'"
                print(statement)
                worker_version_path=tasks[1]
                worker_version=tasks[2]
                cur.execute(statement)
                taskids=cur.fetchall()
                datanode_tasks=taskids

                for tasks in datanode_tasks:
                    task_id = uuid.uuid1()
                    assigned_time = datetime.datetime.now()
                    tast_type_id=tasks[0]
                    insert="insert into tbl_tasks (lng_task_type_id,uid_task_id,uid_request_id,lng_feature_id,uid_agent_id,lng_customer_id,ts_assigned_time,txt_agent_worker_version_path,txt_agent_worker_version) values ("+str(tast_type_id)+",'"+str(task_id)+"',"+str(request_id)+","+str(feature_id)+",'"+str(agentid)+"',"+str(customer_id)+","+"'"+str(assigned_time)+"','"+str(worker_version_path)+"','"+str(worker_version)+"')"
                    cur.execute(insert)
                    conn.commit()
    slave.close()
    host.close()
    opendns=open("hosts.txt")
    openslave=open("slaves.txt")
    slave_text=openslave.read()
    slaves_content={"file_name":"slaves.txt","content":slave_text}
    mydb.slaves.insert_one(slaves_content)
    querystatment=mydb.slaves.find_one(slaves_content)
    slave_objectid=str(querystatment["_id"])
    querytasktypeids="select lng_task_type_id from tbl_task_types where txt_description="+"'"+"slaves file"+"'"
    cur.execute(querytasktypeids)
    tasktypeids_list=cur.fetchall()
    print(tasktypeids_list,1111)
    tasktypeids=tasktypeids_list[0][0]
    task_idsquery="select uid_task_id from tbl_tasks where lng_task_type_id=3"
    cur.execute(task_idsquery)
    task_idslist=cur.fetchall()
    print(task_idslist)
    print(task_idslist)
    slavetask_list=[]
    for tasks in task_idslist:
        slavetask_list.append(tasks[0])
    print(slavetask_list)
    if len(slavetask_list) == 1:
	update_payload="update tbl_tasks set txt_payload_id='"+slave_objectid+"' where uid_task_id  ='"+ slavetask_list[0] +"'"
    else:
    	update_payload="update tbl_tasks set txt_payload_id='"+slave_objectid+"' where uid_task_id in " +str(tuple(slavetask_list))
    cur.execute(update_payload)
    conn.commit()
    host_text=opendns.read()
    host_content={"file_name":"host.txt","content":host_text}
    mydb.hostdns.insert_one(host_content)
    querystatment = mydb.hostdns.find_one(host_content)
    slave_objectid = str(querystatment["_id"])
    hosttasktypeids = "select lng_task_type_id from tbl_task_types where txt_description=" + "'" + "copy hostdns text file" + "'"
    cur.execute(hosttasktypeids)
    host_tasktypeids_list = cur.fetchall()
    host_tasktypeids = host_tasktypeids_list[0][0]
    host_task_idsquery = "select uid_task_id from tbl_tasks where lng_task_type_id in (1,2)"
    cur.execute(host_task_idsquery)
    host_task_idslist = cur.fetchall()
    host_task_list = []
    for host_tasks in host_task_idslist:
        host_task_list.append(host_tasks[0])
    if len(host_task_list) == 1:
    	update_payload_hosts = "update tbl_tasks set txt_payload_id='" + slave_objectid + "' where uid_task_id="+host_task_list[0]
    else:
    	update_payload_hosts = "update tbl_tasks set txt_payload_id='" + slave_objectid + "' where uid_task_id in " + str(tuple(host_task_list))
    cur.execute(update_payload_hosts)
    conn.commit()
    nodetasktypeids = "select lng_task_type_id from tbl_task_types where txt_description=" + "'" + "workerconfiguration" + "'"
    cur.execute(nodetasktypeids)
    node_tasktypeids_list = cur.fetchall()
    node_tasktypeids = node_tasktypeids_list[0][0]
    node_task_idsquery = "select uid_task_id from tbl_tasks where lng_task_type_id=4" 
    cur.execute(node_task_idsquery)
    node_task_idslist = cur.fetchall()
    node_task_list = []
    for node_tasks in node_task_idslist:
        node_task_list.append(node_tasks[0])
    vmstatement="select uid_vm_id from tbl_node_information where uid_cluster_id='"+str(cluster_id)+"' and char_role='namenode'"
    cur.execute(vmstatement)
    vmids=cur.fetchall()
    vmid=vmids[0][0]
    print(vmid)

    node_content={"file_name":"configuration.txt","content":vmid}
    mydb.configurenamenode.insert_one(node_content)
    nodequerystatment = mydb.configurenamenode.find_one(node_content)
    namenodepayloadid = nodequerystatment["_id"]
    if len(node_task_list) == 1:
    	update_payload_hosts = "update tbl_tasks set txt_payload_id='" + str(namenodepayloadid) + "' where uid_task_id = '"+ str(node_task_list[0])+"'"
    else:
    	update_payload_hosts = "update tbl_tasks set txt_payload_id='" + str(namenodepayloadid) + "' where uid_task_id in " + str(tuple(node_task_list))
    cur.execute(update_payload_hosts)
    conn.commit()

    dependent_tasks_list=[[1,[]],[2,[]],[3,[]],[4,[]],[5,[1,2,3,4,6,7,8,9]],[6,[1,2,3,4,7,8,9]],[7,[8,9,3]],[8,[3,9]],[9,[3]],[10,[1,2,3,4,5,6,7,8,9]]]
    for dependenttasks in dependent_tasks_list:
        if dependenttasks[1] == []:
            print("null")
        else:
            print(dependenttasks[1])
            if len(dependenttasks[1]) == 1:

                taskidliststatement="select uid_task_id from tbl_tasks where lng_task_type_id = "+str(dependenttasks[1][0])+" and uid_request_id="+str(request_id)
                cur.execute(taskidliststatement)
                taskid=cur.fetchall()
                listoftasks=''
                for task in taskid:
                    listoftasks+='"'+task[0]+'",'
                splittask = listoftasks.split(",")
                print(splittask, "length")

                tasksstring = "'" + listoftasks[:-1] + "'"
            else:

                taskidliststatement = "select uid_task_id from tbl_tasks where lng_task_type_id in " + str(tuple(dependenttasks[1])) + " and uid_request_id=" + str(request_id)
                cur.execute(taskidliststatement)
                taskid = cur.fetchall()
                listoftasks = ''
                for task in taskid:
                    listoftasks += '"'+ task[0] +'",'
                splittask=listoftasks.split(",")
                print(len(splittask),"length")
                tasksstring = "'" + listoftasks[:-1] + "'"

            updatedependenttasks="update tbl_tasks set txt_dependent_task_id ="+str(tasksstring)+" where lng_task_type_id="+str(dependenttasks[0])
            print(updatedependenttasks)
            cur.execute(updatedependenttasks)
            conn.commit()
            cur.execute("select txt_dependent_task_id from tbl_tasks where srl_id=452")
            dependenttaskid=cur.fetchall()

import pymongo,time,datetime
from bson.objectid import ObjectId
import uuid
from sqlalchemy.orm import scoped_session
from application import session_factory
from application import mongo_conn_string
from application.models.models import TblAgent, TblCustomerRequest, TblCluster,TblFeature,TblMetaFeatureStatus,TblClusterType
from application.modules.azure.createvm import vmcreation
from application.common.loggerfile import my_logger

def installcluster(request_id):
    db_session = scoped_session(session_factory)
    customer_data = db_session.query(TblCustomerRequest.txt_payload_id, TblCustomerRequest.uid_customer_id,TblCustomerRequest.char_feature_id).filter(TblCustomerRequest.uid_request_id == request_id).all()
    print customer_data
    payloadid = customer_data[0][0]
    customer_id = customer_data[0][1]
    feature_id = customer_data[0][2]
    print  "connected to database and got customer data"
    mongo_connection = pymongo.MongoClient(mongo_conn_string)
    database_connection = mongo_connection['haas']
    collection_connection = database_connection['highgear']
    build_cluster_information = collection_connection.find_one({"_id": ObjectId(payloadid)})
    print  build_cluster_information, "this is mongo collection information"
    cloudtype = build_cluster_information["cloud_type"]
   # clustername=build_cluster_information["cluster_name"]
    clusterlocation = build_cluster_information["cluster_location"]
    print cloudtype, "cloudtype"
    cluster_id = str(uuid.uuid1())
    agent_id_list=[]
    vm_creation_info=[]
    for node, information in build_cluster_information.items():
        print (node,information)
        vm_creation_list = []
        agentid = str(uuid.uuid1())
        agent_id_list.append(agentid)

        if node != "cluster_location" and node != "cloud_type" and node != "_id":
            vm_creation_list.append(cluster_id)
            vm_creation_list.append(customer_id)
            vm_creation_list.append(agentid)
            vm_creation_list.append(information['role'])
            vm_creation_list.append(clusterlocation)
            vm_creation_info.append(vm_creation_list)
    print vm_creation_info
  #  vm_information = vmcreation(vm_creation_info)
    #print vm_information
    metatablestatus = db_session.query(TblMetaFeatureStatus.var_feature_status, TblMetaFeatureStatus.srl_id).all()
    table_status_values = dict(metatablestatus)
    completed_task_status_value = table_status_values['COMPLETED']
    update_assigned_statement = db_session.query(TblFeature).filter(TblFeature.char_feature_id == feature_id)
    update_assigned_statement.update({"int_feature_status": completed_task_status_value})
    db_session.commit()
    date_time=datetime.datetime.now()
    created_by="system"
    modified_by="system"
    cluster_type_query = db_session.query(TblClusterType.uid_cluster_type_id).filter(TblClusterType.char_name == cloudtype).all()

    cluster_insertion = TblCluster(uid_cluster_id=cluster_id,
                                   uid_customer_id=customer_id,
                                   uid_cluster_type_id=cluster_type_query[0][0],
                                   char_cluster_region =clusterlocation ,
#                                   var_cluster_name =clustername,
                                   char_cluster_plan_type = "Plan A",
                                   var_created_by = created_by,
                                    var_modified_by = modified_by,
                                    ts_created_datetime = date_time,
                                    ts_modified_datetime = date_time)

    db_session.add(cluster_insertion)
    db_session.commit()

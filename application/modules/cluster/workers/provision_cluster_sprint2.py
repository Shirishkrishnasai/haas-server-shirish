import pymongo,time,datetime
from bson.objectid import ObjectId
import uuid
from sqlalchemy import and_
from sqlalchemy.orm import scoped_session
from application import session_factory
from application import mongo_conn_string

#from application.models.models import TblAgent, TblCustomerRequest, TblCluster,TblFeature,TblMetaFeatureStatus,TblClusterType,TblMetaRequestStatus

from application.models.models import TblCustomerRequest, TblCustomer,TblCluster,TblPlan,TblPlanClusterSizeConfig,TblFeature,TblMetaRequestStatus,TblAgent,TblFeature,TblMetaFeatureStatus,TblClusterType


from application.modules.azure.createvm import vmcreation
from application.common.loggerfile import my_logger

def installcluster(request_id):
    print request_id,'reqqqqqqqqq'
    db_session = scoped_session(session_factory)
    customer_data = db_session.query(TblCustomerRequest.txt_payload_id, TblCustomerRequest.uid_customer_id,\
                    TblCustomerRequest.char_feature_id).filter(TblCustomerRequest.uid_request_id == request_id).all()
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
    clustername=build_cluster_information["cluster_name"]
    clusterlocation = build_cluster_information["cluster_location"]
    size_id=build_cluster_information["size_type"]

    plan_info = db_session.query(TblCustomer.int_plan_id).filter(TblCustomer.uid_customer_id == customer_id).all()
    print plan_info
    plan_id = plan_info[0][0]
    print plan_id
    cluster_id = str(uuid.uuid1())

    #customer_request_insert = TblCustomerRequest(uid_cluster_id=cluster_id)
    #db_session.add(customer_request_insert)
    #customer_request_update = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.txt_dependency_request_id == request_id)
    #customer_request_update.update({"uid_cluster_id": cluster_id})
    #db_session.commit()


    cluster_size_info = db_session.query(TblPlanClusterSizeConfig.var_role,
                                         TblPlanClusterSizeConfig.int_role_count).filter \
        (and_(TblPlanClusterSizeConfig.int_size_id == size_id, TblPlanClusterSizeConfig.int_plan_id == plan_id)).all()

    agent_id_list=[]
    vm_creation_info=[]

    for data in cluster_size_info:
        role=data[0]
        count_of_role=data[1]
        for i in range(0,count_of_role):
            vm_creation_list = []
            agentid = str(uuid.uuid1())
            agent_id_list.append(agentid)


            vm_creation_list.append(cluster_id)
            vm_creation_list.append(customer_id)
            vm_creation_list.append(agentid)
            vm_creation_list.append(role)
            vm_creation_list.append(clusterlocation)
            vm_creation_list.append(size_id)
            vm_creation_list.append(plan_id)

            vm_creation_info.append(vm_creation_list)
    print vm_creation_info
    vm_information = vmcreation(vm_creation_info)
    print vm_information
    metatablestatus = db_session.query(TblMetaRequestStatus.var_request_status, TblMetaRequestStatus.srl_id).all()
    table_status_values = dict(metatablestatus)

    print metatablestatus,'metaaaaaaaaaa'
    completed_task_status_value = table_status_values['COMPLETED']
    update_assigned_statement = db_session.query(TblFeature).filter(TblFeature.char_feature_id == feature_id)
    update_assigned_statement.update({"int_feature_status": completed_task_status_value})

    completed_request_status_value = table_status_values['COMPLETED']
    update_assigned_statement = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == request_id)
    update_assigned_statement.update({"int_request_status": completed_request_status_value})


    db_session.commit()
    date_time=datetime.datetime.now()
    fqdn=clustername+".kwartile"
    created_by="system"
    modified_by="system"
    cluster_insertion = TblCluster(uid_cluster_id=str(cluster_id),
                                   uid_customer_id=str(customer_id),
                                   uid_cluster_type_id='f5826f72-d135-11e8-84db-3ca9f49ab2cc',
                                   txt_fqdn=fqdn,
                                    var_cluster_name =clustername,
                                   char_cluster_region =clusterlocation ,

                                   char_cluster_plan_type = 'Plan A',

                                   int_size_id = size_id,

                                   var_created_by = created_by,
                                    var_modified_by = modified_by,
                                    ts_created_datetime = str(date_time),
                                    ts_modified_datetime = str(date_time))

    db_session.add(cluster_insertion)
    db_session.commit()

    print 'into custommmmmmmmmmmmm  '
    status_list = db_session.query(TblMetaRequestStatus.srl_id).filter(TblMetaRequestStatus.var_request_status=='COMPLETED').all()
    print status_list,'sttaaaaaaattttt'
    customer_request_update = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.txt_dependency_request_id == request_id)
    customer_request_update.update({"uid_cluster_id": cluster_id,"int_request_status":status_list[0][0]})
    db_session.commit()

    customer_request_update_default = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == request_id)
    customer_request_update_default.update({"uid_cluster_id": cluster_id})
    db_session.commit()
    db_session.close()
installcluster('4a82d464-0aa0-11e9-ba4c-3ca9f49ab2cc')




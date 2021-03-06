import pymongo,time,datetime
from bson.objectid import ObjectId
import uuid
from sqlalchemy import and_
from sqlalchemy.orm import scoped_session
from application import session_factory
from application import mongo_conn_string
from application.models.models import TblCustomerRequest, TblCluster,TblPlan,TblPlanClusterSizeConfig,TblFeature,TblCustomer,TblEdgenode,TblMetaRequestStatus
from application.modules.azure.createvm import vmcreation
from application.common.loggerfile import my_logger


def edgenodeProvision(request_id):
    db_session = scoped_session(session_factory)
    customer_data = db_session.query(TblCustomerRequest.uid_customer_id,
                                     TblCustomerRequest.char_feature_id,
                                     TblCustomerRequest.txt_payload_id).filter(TblCustomerRequest.uid_request_id == request_id).first()
    customer_id = customer_data[0]
    feature_id = customer_data[1]
    payload_id = customer_data[2]
    mongo_connection = pymongo.MongoClient(mongo_conn_string)
    database_connection = mongo_connection['haas']
    collection_name = database_connection['highgear']
    edgenode_mongo_info = collection_name.find_one({"_id": ObjectId(payload_id)})
    my_logger.debug(edgenode_mongo_info)

    cluster_id = edgenode_mongo_info['cluster_id']
    location = edgenode_mongo_info['cluster_location']
    plan_info = db_session.query(TblCustomer.int_plan_id).filter(TblCustomer.uid_customer_id == customer_id).first()
    size_info = db_session.query(TblCluster.int_size_id).filter(TblCluster.uid_cluster_id==cluster_id).first()
    plan_id = plan_info[0]
    size_id = size_info[0]

    edgenode_info = db_session.query(TblEdgenode.var_role,
                                     TblEdgenode.int_role_count).filter(and_(TblEdgenode.int_size_id==size_id,
                                                                             TblEdgenode.int_plan_id == plan_id,
                                                                             TblEdgenode.char_feature_id == feature_id)).all()

    vm_creation_info=[]

    for data in edgenode_info:
        role=data[0]
        count_of_role=data[1]
        for i in range(0,count_of_role):
            vm_creation_list = []
            agentid = str(uuid.uuid1())
            #vm_creation_list.extend([cluster_id,customer_id,agentid,role,location,size_id,plan_id])

            vm_creation_list.append(cluster_id)
            vm_creation_list.append(customer_id)
            vm_creation_list.append(agentid)
            vm_creation_list.append(role)
            vm_creation_list.append(location)
            vm_creation_list.append(size_id)
            vm_creation_list.append(plan_id)
            vm_creation_info.append(vm_creation_list)
    print vm_creation_list
    my_logger.info("calling createvm method")
    vm_information = vmcreation(vm_creation_info)#u should call another function probably
    my_logger.debug(vm_information)
    metatablestatus = db_session.query(TblMetaRequestStatus.var_request_status, TblMetaRequestStatus.srl_id).all()
    table_status_values = dict(metatablestatus)
    completed_task_status_value = table_status_values['COMPLETED']
    update_assigned_statement = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == request_id)
    update_assigned_statement.update({"int_request_status": completed_task_status_value})
    db_session.commit()

import pymongo,time,datetime
from bson.objectid import ObjectId
import uuid
import sys,os
from sqlalchemy import and_
from sqlalchemy.orm import scoped_session
from application import session_factory
from application import mongo_conn_string
from azure.storage.file import FileService, FilePermissions
from configparser import ConfigParser
from application.models.models import TblCustomerRequest, TblCustomer,TblCluster,TblPlan,TblPlanClusterSizeConfig,TblFeature,TblMetaRequestStatus,TblAgent,TblFeature,TblMetaFeatureStatus,TblClusterType
from application.modules.azure.createvm import vmcreation
from application.common.loggerfile import my_logger

def installcluster(request_id):
    try:
        print "in cluster provision worker ............there you go .......... tik-tok"
        #print sys.argv
        #print sys.argv[1]
        #request_id = sys.argv[1]
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
        size_id=build_cluster_information["size_id"]

        plan_info = db_session.query(TblCustomer.int_plan_id).filter(TblCustomer.uid_customer_id == customer_id).all()
        print plan_info
        plan_id = plan_info[0][0]
        print plan_id
        cluster_id = str(uuid.uuid1())
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
                                       uid_cluster_type_id=str(cloudtype),
                                       txt_fqdn=fqdn,
                                        var_cluster_name =clustername,
                                       char_cluster_region =clusterlocation ,
                                       int_size_id = int(size_id),
                                       var_created_by = created_by,
                                        var_modified_by = modified_by,
                                        ts_created_datetime = str(date_time),
                                        ts_modified_datetime = str(date_time))

        db_session.add(cluster_insertion)
        db_session.commit()

        status_list = db_session.query(TblMetaRequestStatus.srl_id).filter(
            TblMetaRequestStatus.var_request_status == 'COMPLETED').all()
        print status_list, 'sttaaaaaaattttt'
        customer_request_update = db_session.query(TblCustomerRequest).filter(
            TblCustomerRequest.txt_dependency_request_id == request_id)
        customer_request_update.update({"uid_cluster_id": cluster_id, "int_request_status": status_list[0][0]})
        db_session.commit()

        customer_request_update_default = db_session.query(TblCustomerRequest).filter(
            TblCustomerRequest.uid_request_id == request_id)
        customer_request_update_default.update({"uid_cluster_id": cluster_id})
        db_session.commit()
        db_session.close()

        cfg = ConfigParser()
        cfg.read('application/config/azure_config.ini')
        account_name = cfg.get('file_storage', 'account_name')
        account_key = cfg.get('file_storage', 'key')

        file_service = FileService(account_name=account_name, account_key=account_key)

        file_service.create_share(cluster_id)
        file_service.create_directory(cluster_id, 'system')
        file_service.create_directory(cluster_id, 'mapreduce')
        print "doneeee"

    # installcluster('4a82d464-0aa0-11e9-ba4c-3ca9f49ab2cc')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(str(e))
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)

if __name__ == '__main__':

        if len(sys.argv)>=1:
            request_id = sys.argv[1]
            my_logger.info("Callign with id "+request_id)

            installcluster(request_id)
        else:
            print "args not passed"


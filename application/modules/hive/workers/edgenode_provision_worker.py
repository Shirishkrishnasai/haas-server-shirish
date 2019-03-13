import uuid
import sys,os
import pymongo
from bson.objectid import ObjectId
from sqlalchemy import and_
from sqlalchemy.orm import scoped_session
from configparser import ConfigParser
from azure.storage.file import FileService, FilePermissions
from application import mongo_conn_string
from application import session_factory
from application.models.models import  TblEdgenode
from application.models.models import TblCustomerRequest, TblCluster, TblCustomer, TblMetaRequestStatus
from application.common.loggerfile import my_logger
from application.modules.azure.createvm import vmcreation


def edgenodeProvision(request_id):
    try:

        db_session = scoped_session(session_factory)
        customer_data = db_session.query(TblCustomerRequest.uid_customer_id,
                                         TblCustomerRequest.char_feature_id,
                                         TblCustomerRequest.uid_cluster_id).filter(TblCustomerRequest.uid_request_id == request_id).first()
        customer_id = customer_data[0]
        feature_id = customer_data[1]

        cluster_id = customer_data[2]
        location = 'south india'
        plan_info = db_session.query(TblCustomer.int_plan_id).filter(TblCustomer.uid_customer_id == customer_id).first()
        size_info = db_session.query(TblCluster.int_size_id).filter(TblCluster.uid_cluster_id==cluster_id).first()
        plan_id = plan_info[0]
        size_id = size_info[0]

        edgenode_info = db_session.query(TblEdgenode.var_role).filter(TblEdgenode.char_feature_id == feature_id).first()
        vm_creation_info=[]
        role=edgenode_info[0]

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
        my_logger.info(vm_creation_list)
        my_logger.info("calling createvm method")
        my_logger.info("calling vm_creation")
        vm_information = vmcreation(vm_creation_info)
        #you should call another function probably
        my_logger.info(vm_information)
        metatablestatus = db_session.query(TblMetaRequestStatus.var_request_status, TblMetaRequestStatus.srl_id).all()
        table_status_values = dict(metatablestatus)
        completed_task_status_value = table_status_values['COMPLETED']
        update_assigned_statement = db_session.query(TblCustomerRequest).filter(TblCustomerRequest.uid_request_id == request_id)
        update_assigned_statement.update({"int_request_status": completed_task_status_value})
        db_session.commit()
        db_session.close()

        cfg = ConfigParser()
        cfg.read('application/config/azure_config.ini')
        account_name = cfg.get('file_storage', 'account_name')
        account_key = cfg.get('file_storage', 'key')

        file_service = FileService(account_name=account_name, account_key=account_key)

        file_service.create_share(cluster_id)
        file_service.create_directory(cluster_id, 'system')
        file_service.create_directory(cluster_id, 'hive')
        file_service.create_directory(cluster_id, 'spark')
        my_logger.info("doneeee")

    except Exception as e:
         exc_type, exc_obj, exc_tb = sys.exc_info()
         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
         my_logger.error(str(e))
         my_logger.error(exc_type)
         my_logger.error(fname)
         my_logger.error(exc_tb.tb_lineno)
    finally:
         db_session.close()

if __name__ == '__main__':
    try:
        if len(sys.argv)>=1:
            my_logger.info(sys.argv)
            request_id = sys.argv[1]
            edgenodeProvision(request_id)
        else:
            my_logger.info("args not passed")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(str(e))
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)








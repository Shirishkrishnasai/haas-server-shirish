''''
author:Arvind
date of completion:18-03-2019
''''
from flask import Blueprint,request,jsonify
from application.models.models import TblCustomerRequestHdfs,TblAgent,TblNodeInformation
from sqlalchemy.orm import scoped_session
from application import session_factory
import sys,os,io
from application.common.loggerfile import my_logger
import uuid
import time
from azure.storage.file import FileService
from configparser import ConfigParser
from application.models.models import  TblFileUpload
from azure.storage.file import FileService, FilePermissions
from datetime import datetime, timedelta


hdfsapi = Blueprint('hdfsapi', __name__)



@hdfsapi.route("/api/hdfs/list", methods=['POST'])

def hdfs_list_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'list'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery=db_session.query(TblNodeInformation.uid_node_id).filter(TblNodeInformation.uid_cluster_id==cluster_id,TblNodeInformation.char_role=='namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery=db_session.query(TblAgent.uid_agent_id).filter(TblAgent.uid_node_id==nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                 uid_customer_id=customer_id,
                                                 uid_cluster_id=cluster_id,
                                                 uid_agent_id=agentinfoquery[0][0],
                                                 var_user_name=user_name,
                                                 ts_requested_time=datetime.now(),
                                                 txt_command_string=command_string,
                                                 txt_hdfs_parameters=hdfs_parameters,
                                                 bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
            filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@hdfsapi.route("/api/hdfs/status", methods=['POST'])
def hdfs_status_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'fsck'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
            TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
            TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                     uid_customer_id=customer_id,
                                                     uid_cluster_id=cluster_id,
                                                     uid_agent_id=agentinfoquery[0][0],
                                                     var_user_name=user_name,
                                                     ts_requested_time=datetime.now(),
                                                     txt_command_string=command_string,
                                                     txt_hdfs_parameters=hdfs_parameters,
                                                     bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@hdfsapi.route("/api/hdfs/count", methods=['POST'])
def hdfs_count_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'count'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
            TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
            TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                     uid_customer_id=customer_id,
                                                     uid_cluster_id=cluster_id,
                                                     uid_agent_id=agentinfoquery[0][0],
                                                     var_user_name=user_name,
                                                     ts_requested_time=datetime.now(),
                                                     txt_command_string=command_string,
                                                     txt_hdfs_parameters=hdfs_parameters,
                                                     bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@hdfsapi.route("/api/hdfs/createdirectory", methods=['POST'])
def hdfs_createdirectory_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'mkdir'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
            TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
            TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                     uid_customer_id=customer_id,
                                                     uid_cluster_id=cluster_id,
                                                     uid_agent_id=agentinfoquery[0][0],
                                                     var_user_name=user_name,
                                                     ts_requested_time=datetime.now(),
                                                     txt_command_string=command_string,
                                                     txt_hdfs_parameters=hdfs_parameters,
                                                     bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@hdfsapi.route("/api/hdfs/remove", methods=['POST'])
def hdfs_remove_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'remove'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
            TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
            TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                     uid_customer_id=customer_id,
                                                     uid_cluster_id=cluster_id,
                                                     uid_agent_id=agentinfoquery[0][0],
                                                     var_user_name=user_name,
                                                     ts_requested_time=datetime.now(),
                                                     txt_command_string=command_string,
                                                     txt_hdfs_parameters=hdfs_parameters,
                                                     bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@hdfsapi.route("/api/hdfs/tail", methods=['POST'])
def hdfs__tail_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'tail'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
            TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
            TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                     uid_customer_id=customer_id,
                                                     uid_cluster_id=cluster_id,
                                                     uid_agent_id=agentinfoquery[0][0],
                                                     var_user_name=user_name,
                                                     ts_requested_time=datetime.now(),
                                                     txt_command_string=command_string,
                                                     txt_hdfs_parameters=hdfs_parameters,
                                                     bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@hdfsapi.route("/api/hdfs/text", methods=['POST'])
def hdfs_text_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'text'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
            TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
            TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                     uid_customer_id=customer_id,
                                                     uid_cluster_id=cluster_id,
                                                     uid_agent_id=agentinfoquery[0][0],
                                                     var_user_name=user_name,
                                                     ts_requested_time=datetime.now(),
                                                     txt_command_string=command_string,
                                                     txt_hdfs_parameters=hdfs_parameters,
                                                     bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


def fileProgress(start, size):
    my_logger.debug("%d%d", start, size)


@hdfsapi.route("/api/hdfs/upload", methods=['POST'])
def hdfs_upload_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.values
        print hdfs_request_parameters
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'upload'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        posted_file = request.files
        str_posted_file = posted_file['files'].read()
        print str_posted_file
        byte_stream = io.BytesIO(str_posted_file)
        no_of_bytes=len(str_posted_file)
        filename=uuid.uuid1()
        file_upload_id=uuid.uuid1()
        cfg = ConfigParser()
        cfg.read('application/config/azure_config.ini')
        account_name = cfg.get('file_storage', 'account_name')
        account_key = cfg.get('file_storage', 'key')

        file_service = FileService(account_name=account_name, account_key=account_key)
        print file_service
        print no_of_bytes

        file_service.create_file_from_stream(share_name=str(cluster_id),
                                             directory_name='hdfs',
                                             file_name=str(filename),
                                             stream=byte_stream,
                                             count=no_of_bytes,
                                             progress_callback=fileProgress)
        file_insert_values = TblFileUpload(uid_upload_id=str(file_upload_id),
                                           uid_customer_id=str(customer_id),
                                           var_share_name=str(cluster_id),
                                           var_directory_name='hdfs',
                                           var_file_name=filename,
                                           var_username=user_name,
                                           ts_uploaded_time=datetime.datetime.now())
        db_session.add(file_insert_values)
        db_session.commit()

        nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
            TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
            TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                     uid_customer_id=customer_id,
                                                     uid_cluster_id=cluster_id,
                                                     uid_agent_id=agentinfoquery[0][0],
                                                     uid_upload_id=str(file_upload_id),
                                                     var_user_name=user_name,
                                                     ts_requested_time=datetime.now(),
                                                     txt_command_string=command_string,
                                                     txt_hdfs_parameters=hdfs_parameters,
                                                     bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@hdfsapi.route("/api/hdfs/download", methods=['POST'])
def hdfs_download_api():
#    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'download'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
            TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
            TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                     uid_customer_id=customer_id,
                                                     uid_cluster_id=cluster_id,
                                                     uid_agent_id=agentinfoquery[0][0],
                                                     var_user_name=user_name,
                                                     ts_requested_time=datetime.now(),
                                                     txt_command_string=command_string,
                                                     txt_hdfs_parameters=hdfs_parameters,
                                                     bool_command_complete=0)

        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:


                cfg = ConfigParser()
                cfg.read('application/config/azure_config.ini')
                account_name = cfg.get('file_storage', 'account_name')
                account_key = cfg.get('file_storage', 'key')
                print hdfs_command_result[0][0]
                expiry_date = str(datetime.now().date() + timedelta(days=3))

                file_service = FileService(account_name=account_name, account_key=account_key)
                access_signature = file_service.generate_file_shared_access_signature(share_name=cluster_id,
                                                                                      directory_name='hdfs',
                                                                                      file_name=hdfs_command_result[0][0],
                                                                                      permission=FilePermissions.READ,
                                                                                      expiry=expiry_date)
                my_logger.info('access signature is generated')
                my_logger.info('now creating fileurl to access')
                # getting file url
                file_url = file_service.make_file_url(share_name=cluster_id,
                                                      directory_name='hdfs',
                                                      file_name=hdfs_command_result[0][0],
                                                      protocol='https',
                                                      sas_token=access_signature)

                return jsonify(command_output=file_url)
 #   except Exception as e:

#        exc_type, exc_obj, exc_tb = sys.exc_info()
 #       fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
  #      my_logger.error(exc_type)
   #     my_logger.error(fname)
    #    my_logger.error(exc_tb.tb_lineno)
    #finally:
     #44    db_session.close()


@hdfsapi.route("/api/hdfs/request", methods=['POST'])
def hdfs_request_sender():
    try:
        db_session = scoped_session(session_factory)
        hdfs_requests_query = db_session.query(TblCustomerRequestHdfs.uid_hdfs_request_id,TblCustomerRequestHdfs.uid_customer_id,TblCustomerRequestHdfs.uid_cluster_id,TblCustomerRequestHdfs.uid_agent_id,TblCustomerRequestHdfs.var_user_name,TblCustomerRequestHdfs.txt_command_string,TblCustomerRequestHdfs.txt_hdfs_parameters).all()
        requests_list=[]
        for requests in hdfs_requests_query:
            hdfs_request_dict={}
            agent_ip_query = db_session.query(TblAgent.private_ips).filter(TblAgent.uid_agent_id == requests[3]).all()
            hdfs_request_dict['hdfs_request_id']=requests[0]
            hdfs_request_dict['customer_id']=requests[1]
            hdfs_request_dict['cluster_id']=requests[2]
            hdfs_request_dict['agent_id']=requests[3]
            hdfs_request_dict['user_name']=requests[4]
            hdfs_request_dict['namenode_ip']=agent_ip_query[0][0]
            hdfs_request_dict['command_type']=requests[5]
            hdfs_request_dict['job_parameters']=requests[6]
            requests_list.append(hdfs_request_dict)
        return jsonify(message=requests_list)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@hdfsapi.route("/api/upload", methods=['POST'])

def hdfs_result_upload():
    try:
        hdfs_output_json=request.json
        print hdfs_output_json
        db_session = scoped_session(session_factory)
        hdfs_customer_request=db_session.query(TblCustomerRequestHdfs).filter(TblCustomerRequestHdfs.uid_hdfs_request_id==hdfs_output_json['request_id'])
        hdfs_customer_request.update({"hdfs_command_output":str(hdfs_output_json['output'])})
        db_session.commit()
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@hdfsapi.route("/api/hdfs/move", methods=['POST'])

def hdfs_move_api():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters = request.json
        customer_id = hdfs_request_parameters['customer_id']
        cluster_id = hdfs_request_parameters['cluster_id']
        user_name = hdfs_request_parameters['user_name']
        command_string = 'move'
        hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
        hdfs_request_id = uuid.uuid1()
        print hdfs_parameters
        nodeinformationquery=db_session.query(TblNodeInformation.uid_node_id).filter(TblNodeInformation.uid_cluster_id==cluster_id,TblNodeInformation.char_role=='namenode').all()
        print nodeinformationquery[0][0]
        agentinfoquery=db_session.query(TblAgent.uid_agent_id).filter(TblAgent.uid_node_id==nodeinformationquery[0][0]).all()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                 uid_customer_id=customer_id,
                                                 uid_cluster_id=cluster_id,
                                                 uid_agent_id=agentinfoquery[0][0],
                                                 var_user_name=user_name,
                                                 ts_requested_time=datetime.now(),
                                                 txt_command_string=command_string,
                                                 txt_hdfs_parameters=hdfs_parameters,
                                                 bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        db_session.close()
        print "commited"
        my_logger.info("committing to database and closing session done")

        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
            filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

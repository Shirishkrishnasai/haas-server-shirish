from flask import Blueprint,request,jsonify
from application.models.models import TblCustomerRequestHdfs,TblAgent,TblNodeInformation
from sqlalchemy.orm import scoped_session
from application import session_factory
import sys,os,io
from application.common.loggerfile import my_logger
import uuid
import time
from configparser import ConfigParser
from application.models.models import  TblFileUpload
from azure.storage.file import FileService, FilePermissions
from datetime import datetime, timedelta
from flask import request
import ast
hdfsapi = Blueprint('hdfsapi', __name__)



@hdfsapi.route("/api/hdfs/directorylisting/<customer_id>/<cluster_id>", methods=['GET'])

def hdfs_listing_api(customer_id,cluster_id):
	 try:
		db_session = scoped_session(session_factory)
		hdfs_request_parameters = request.args
		command_string = 'list'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters'][1:]
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
		agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
			TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
													 uid_customer_id=customer_id,
													 uid_cluster_id=cluster_id,
													 uid_agent_id=agentinfoquery[0][0],
													 ts_requested_time=datetime.now(),
													 txt_command_string=command_string,
													 txt_hdfs_parameters=hdfs_parameters,
													 bool_assigned=0,
													 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()
		my_logger.info("committing to database and closing session done")

		t_end = time.time() + 120
		while time.time() < t_end:
			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
			filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)
				return jsonify(command_output=x)
	 except Exception as e:
	   exc_type, exc_obj, exc_tb = sys.exc_info()
	   fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	   my_logger.error(exc_type)
	   my_logger.error(fname)
	   my_logger.error(exc_tb.tb_lineno)
	 finally:
		db_session.close()

@hdfsapi.route("/api/hdfs/status/<customer_id>/<cluster_id>", methods=['GET'])

def hdfs_status_api(customer_id,cluster_id):
	try:
		db_session = scoped_session(session_factory)
		hdfs_request_parameters = request.args
		command_string = 'fsck'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
		agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
			TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
													 uid_customer_id=customer_id,
													 uid_cluster_id=cluster_id,
													 uid_agent_id=agentinfoquery[0][0],
													 ts_requested_time=datetime.now(),
													 txt_command_string=command_string,
													 txt_hdfs_parameters=hdfs_parameters,
							 bool_assigned=0,
													 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()
		my_logger.info("committing to database and closing session done")

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
				filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)
				return jsonify(command_output=x)
	except Exception as e:

		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		my_logger.error(exc_type)
		my_logger.error(fname)
		my_logger.error(exc_tb.tb_lineno)
	finally:
		db_session.close()


@hdfsapi.route("/api/hdfs/count/<customer_id>/<cluster_id>", methods=['GET'])
def hdfs_count_api(customer_id,cluster_id):
	try:
		db_session = scoped_session(session_factory)
		hdfs_request_parameters = request.args
		command_string = 'count'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
		agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
			TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
													 uid_customer_id=customer_id,
													 uid_cluster_id=cluster_id,
													 uid_agent_id=agentinfoquery[0][0],
													 ts_requested_time=datetime.now(),
													 txt_command_string=command_string,
													 txt_hdfs_parameters=hdfs_parameters,
													 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
				filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)

				return jsonify(command_output=x)
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
		directory_name = hdfs_request_parameters['new_folder']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
		agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
			TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
													 uid_customer_id=customer_id,
													 uid_cluster_id=cluster_id,
													 uid_agent_id=agentinfoquery[0][0],
													 var_user_name=user_name,
							 txt_directory_name = directory_name,
													 ts_requested_time=datetime.now(),
													 txt_command_string=command_string,
													 txt_hdfs_parameters=hdfs_parameters,
							 bool_assigned=0,
													 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
				filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)
				return jsonify(command_output=[{"message":x['message']}])
	except Exception as e:

		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		my_logger.error(exc_type)
		my_logger.error(fname)
		my_logger.error(exc_tb.tb_lineno)
	finally:
		db_session.close()


@hdfsapi.route("/api/hdfs/remove/<customer_id>/<cluster_id>", methods=['GET'])
def hdfs_remove_api(customer_id,cluster_id):
	try:
		db_session = scoped_session(session_factory)
		hdfs_request_parameters = request.args
		command_string = 'remove'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
		agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
			TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
													 uid_customer_id=customer_id,
													 uid_cluster_id=cluster_id,
													 uid_agent_id=agentinfoquery[0][0],
													 ts_requested_time=datetime.now(),
													 txt_command_string=command_string,
													 txt_hdfs_parameters=hdfs_parameters,
							 bool_assigned=0,
													 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()
		my_logger.info("committing to database and closing session done")

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
				filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)
		return jsonify(command_output=x['message'])
	except Exception as e:

		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		my_logger.error(exc_type)
		my_logger.error(fname)
		my_logger.error(exc_tb.tb_lineno)
	finally:
		db_session.close()


@hdfsapi.route("/api/hdfs/tail/<customer_id>/<cluster_id>", methods=['GET'])
def hdfs_tail_api(customer_id,cluster_id):
	try:
		db_session = scoped_session(session_factory)
		hdfs_request_parameters = request.args
		command_string = 'tail'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
		agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
			TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
													 uid_customer_id=customer_id,
													 uid_cluster_id=cluster_id,
													 uid_agent_id=agentinfoquery[0][0],
													 ts_requested_time=datetime.now(),
													 txt_command_string=command_string,
													 txt_hdfs_parameters=hdfs_parameters,
							 bool_assigned=0,
													 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
				filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)
				return jsonify(command_output=x['message'])
	except Exception as e:

		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		my_logger.error(exc_type)
		my_logger.error(fname)
		my_logger.error(exc_tb.tb_lineno)
	finally:
		db_session.close()


@hdfsapi.route("/api/hdfs/head/<customer_id>/<cluster_id>", methods=['GET'])
def hdfs_head_api(customer_id,cluster_id):
	try:
		db_session = scoped_session(session_factory)
		hdfs_request_parameters = request.args
		command_string = 'text'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
		agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
			TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
													 uid_customer_id=customer_id,
													 uid_cluster_id=cluster_id,
													 uid_agent_id=agentinfoquery[0][0],
													 ts_requested_time=datetime.now(),
													 txt_command_string=command_string,
													 txt_hdfs_parameters=hdfs_parameters,
													 bool_assigned=0,
							 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()
		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
				filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)
				output1=x[0]['message']
				return jsonify(command_output=output1)
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
		customer_id = hdfs_request_parameters['customer_id']
		cluster_id = hdfs_request_parameters['cluster_id']
		user_name = hdfs_request_parameters['user_name']
		command_string = 'upload'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
		hdfs_request_id = uuid.uuid1()
		posted_file = request.files
		str_posted_file = posted_file['files'].read()
		byte_stream = io.BytesIO(str_posted_file)
		no_of_bytes=len(str_posted_file)
		filename=uuid.uuid1()
		file_upload_id=uuid.uuid1()
		cfg = ConfigParser()
		cfg.read('application/config/azure_config.ini')
		account_name = cfg.get('file_storage', 'account_name')
		account_key = cfg.get('file_storage', 'key')

		file_service = FileService(account_name=account_name, account_key=account_key)
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
										   ts_uploaded_time=datetime.now())
		db_session.add(file_insert_values)
		db_session.commit()

		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
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
							 bool_assigned=0,
													 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()
		my_logger.info("committing to database and closing session done")

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
				filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)
				return jsonify(command_output=x['message'])
	except Exception as e:

	   exc_type, exc_obj, exc_tb = sys.exc_info()
	   fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	   my_logger.error(exc_type)
	   my_logger.error(fname)
	   my_logger.error(exc_tb.tb_lineno)
	finally:
		db_session.close()


@hdfsapi.route("/api/hdfs/download/<customer_id>/<cluster_id>", methods=['GET'])
def hdfs_download_api(customer_id,cluster_id):
	try:
		db_session = scoped_session(session_factory)
		hdfs_request_parameters = request.args
		command_string = 'download'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery = db_session.query(TblNodeInformation.uid_node_id).filter(
			TblNodeInformation.uid_cluster_id == cluster_id, TblNodeInformation.char_role == 'namenode').all()
		agentinfoquery = db_session.query(TblAgent.uid_agent_id).filter(
			TblAgent.uid_node_id == nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
													 uid_customer_id=customer_id,
													 uid_cluster_id=cluster_id,
													 uid_agent_id=agentinfoquery[0][0],
													 ts_requested_time=datetime.now(),
													 txt_command_string=command_string,
													 txt_hdfs_parameters=hdfs_parameters,
							 bool_assigned=0,
													 bool_command_complete=0)

		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
				filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)


				cfg = ConfigParser()
				cfg.read('application/config/azure_config.ini')
				account_name = cfg.get('file_storage', 'account_name')
				account_key = cfg.get('file_storage', 'key')
				expiry_date = str(datetime.now().date() + timedelta(days=3))

				file_service = FileService(account_name=account_name, account_key=account_key)
				access_signature = file_service.generate_file_shared_access_signature(share_name=cluster_id,
																					  directory_name='hdfs',
																					  file_name=x['message'],
																					  permission=FilePermissions.READ,
																					  expiry=expiry_date)
				# getting file url
				file_url = file_service.make_file_url(share_name=cluster_id,
													  directory_name='hdfs',
													  file_name=x['message'],
													  protocol='https',
													  sas_token=access_signature)

				return jsonify(command_output=file_url)
	except Exception as e:

	   exc_type, exc_obj, exc_tb = sys.exc_info()
	   fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	   my_logger.error(exc_type)
	   my_logger.error(fname)
	   my_logger.error(exc_tb.tb_lineno)
	finally:
		db_session.close()


@hdfsapi.route("/api/hdfs/request/<agent_id>", methods=['GET'])
def hdfs_request_sender(agent_id):
	try:
		db_session = scoped_session(session_factory)
		hdfs_requests_query = db_session.query(TblCustomerRequestHdfs.uid_hdfs_request_id,TblCustomerRequestHdfs.uid_customer_id,TblCustomerRequestHdfs.uid_cluster_id,TblCustomerRequestHdfs.uid_agent_id,TblCustomerRequestHdfs.var_user_name,TblCustomerRequestHdfs.txt_command_string,TblCustomerRequestHdfs.txt_hdfs_parameters,TblCustomerRequestHdfs.txt_directory_name,TblCustomerRequestHdfs.uid_upload_id).filter(TblCustomerRequestHdfs.bool_assigned == 'f',TblCustomerRequestHdfs.uid_agent_id==agent_id).all()
		requests_list=[]
		for requests in hdfs_requests_query:
			hdfs_request_dict={}
			agent_ip_query = db_session.query(TblAgent.private_ips).filter(TblAgent.uid_agent_id == requests[3]).all()
			hdfs_request_dict['request_id']=requests[0]
			hdfs_request_dict['customer_id']=requests[1]
			hdfs_request_dict['cluster_id']=requests[2]
			hdfs_request_dict['agent_id']=requests[3]
			hdfs_request_dict['namenode_ip']=agent_ip_query[0][0]
			hdfs_request_dict['command_type']=requests[5]
			hdfs_list=requests[6].split(" ")
			if len(hdfs_list) == 2:
				hdfs_request_dict['hdfs_parameters']=hdfs_list[0]
				hdfs_request_dict['output_path']=hdfs_list[1]
			else:
				hdfs_request_dict['hdfs_parameters']=requests[6]
				if hdfs_request_dict['command_type'] ==  'upload':
					fileuploaddata=db_session.query(TblFileUpload.var_file_name).filter(TblFileUpload.uid_upload_id == requests[8]).all()
					hdfs_request_dict['input_path']='/opt/mnt/azurefileshare/hdfs/'+fileuploaddata[0][0]
					hdfs_request_dict['directory_name']=requests[7]
			requests_list.append(hdfs_request_dict)
			customer_request_hdfs_query=db_session.query(TblCustomerRequestHdfs).filter(TblCustomerRequestHdfs.uid_hdfs_request_id == hdfs_request_dict['request_id'])
			customer_request_hdfs_query.update({'bool_assigned':1})
			db_session.commit()
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
		db_session = scoped_session(session_factory)
		hdfs_customer_request=db_session.query(TblCustomerRequestHdfs).filter(TblCustomerRequestHdfs.uid_hdfs_request_id==hdfs_output_json['request_id'])
		hdfs_customer_request.update({"hdfs_command_output":str(hdfs_output_json['output'])})
		db_session.commit()
		return  jsonify("success")
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
		command_string = 'mv'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters'] + " " + hdfs_request_parameters['output_path']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery=db_session.query(TblNodeInformation.uid_node_id).filter(TblNodeInformation.uid_cluster_id==cluster_id,TblNodeInformation.char_role=='namenode').all()
		agentinfoquery=db_session.query(TblAgent.uid_agent_id).filter(TblAgent.uid_node_id==nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
												 uid_customer_id=customer_id,
												 uid_cluster_id=cluster_id,
												 uid_agent_id=agentinfoquery[0][0],
												 var_user_name=user_name,
												 ts_requested_time=datetime.now(),
												 txt_command_string=command_string,
												 txt_hdfs_parameters=hdfs_parameters,
						 bool_assigned=0,
												 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
			filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)

				return jsonify(command_output=x['message'])
	except Exception as e:

		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		my_logger.error(exc_type)
		my_logger.error(fname)
		my_logger.error(exc_tb.tb_lineno)
	finally:
		db_session.close()



@hdfsapi.route("/api/hdfs/rename", methods=['POST'])

def hdfs_rename_api():
	try:
		hdfs_request_parameters = request.json
		db_session = scoped_session(session_factory)
		print hdfs_request_parameters, "-----------------------"
		customer_id = hdfs_request_parameters['customer_id']
		cluster_id = hdfs_request_parameters['cluster_id']
		user_name = hdfs_request_parameters['user_name']
		command_string = 'rename'
		hdfs_parameters = hdfs_request_parameters['hdfs_parameters'] + " " + hdfs_request_parameters['new_folder']
		hdfs_request_id = uuid.uuid1()
		nodeinformationquery=db_session.query(TblNodeInformation.uid_node_id).filter(TblNodeInformation.uid_cluster_id==cluster_id,TblNodeInformation.char_role=='namenode').all()
		print nodeinformationquery,"hvZXDfgJZUDGvkjsgvuj"
		agentinfoquery=db_session.query(TblAgent.uid_agent_id).filter(TblAgent.uid_node_id==nodeinformationquery[0][0]).all()
		hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
												 uid_customer_id=customer_id,
												 uid_cluster_id=cluster_id,
												 uid_agent_id=agentinfoquery[0][0],
												 var_user_name=user_name,
												 ts_requested_time=datetime.now(),
												 txt_command_string=command_string,
												 txt_hdfs_parameters=hdfs_parameters,
												 bool_assigned=0,
												 bool_command_complete=0)
		db_session.add(hdfs_request_values)
		db_session.commit()
		db_session.close()

		t_end = time.time() + 120
		while time.time() < t_end:

			hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
			filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
			if hdfs_command_result[0][0] is not None:
				hdfs_output = hdfs_command_result[0][0]
				output=hdfs_output.encode('utf-8')
				x = ast.literal_eval(output)

				return jsonify(command_output=x['message'])
	except Exception as e:

		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		my_logger.error(exc_type)
		my_logger.error(fname)
		my_logger.error(exc_tb.tb_lineno)
	finally:
		db_session.close()


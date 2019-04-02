import datetime
import io, sys, uuid, os
from ConfigParser import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import json
from sqlalchemy.orm import sessionmaker
from azure.storage.file import FileService
from application.common.loggerfile import my_logger
from application.models.models import TblCustomerSparkRequest, TblFileUpload, TblMetaMrRequestStatus, TblNodeInformation, \
    TblVmCreation
from application.config.config_file import SQLALCHEMY_DATABASE_URI
from sqlalchemy.orm import scoped_session
from flask import Blueprint, request, jsonify

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_size=100)
session_factory = sessionmaker(bind=engine)

spark_update = Blueprint('spark_update', __name__)


@spark_update.route('/sparkjobstatus', methods=['POST'])
def sparkJobStatus():
    try:
        db_session = scoped_session(session_factory)
        data = request.json
        print data,"rei ide dataaaaaaa"
        spark_status = data['status']
        request_id = data['request_id']
        app_id=data['application_id']
        print spark_status,request_id
        spark_insert = db_session.query(TblCustomerSparkRequest).filter(TblCustomerSparkRequest.uid_request_id == request_id)
        spark_insert.update({"var_status": spark_status,"var_application_id":app_id})
        db_session.commit()
        return jsonify(message='Success')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@spark_update.route('/api/add_spark_job', methods=['POST'])
def sparkJobInsert():
    try:
        customer_request = request.values.to_dict()
        db_session = scoped_session(session_factory)
        request_id = str(uuid.uuid1())
        date_time = datetime.datetime.now()
        customer_id=customer_request['customer_id']
        cluster_id=customer_request['cluster_id']
        agent_id=db_session.query(TblVmCreation.uid_agent_id).filter(TblVmCreation.var_role=='spark',TblVmCreation.uid_cluster_id==cluster_id).first()
        user_name = customer_request['user_name']
        job_name = customer_request['job_name']
        job_description = customer_request['job_description']
        filename = request.files['files'].filename
        job_parameters = customer_request['job_arguments']
        posted_file = request.files
        str_posted_file = posted_file['files'].read()
        no_of_bytes = len(str_posted_file)
        # converting unicoded file to bytestream
        byte_stream = io.BytesIO(str_posted_file)
        cfg = ConfigParser()
        cfg.read('application/config/azure_config.ini')
        account_name = cfg.get('file_storage', 'account_name')
        account_key = cfg.get('file_storage', 'key')
        file_service = FileService(account_name=account_name, account_key=account_key)
        file_service.create_file_from_stream(share_name=cluster_id,
                                             directory_name="SPARK",
                                             file_name=filename,
                                             stream=byte_stream,
                                             count=no_of_bytes,
                                             progress_callback=fileProgres)
        file_upload_id = str(uuid.uuid1())
        file_insert_values = TblFileUpload(uid_upload_id=file_upload_id,
                                           uid_customer_id=customer_id,
                                           var_share_name=cluster_id,
                                           var_directory_name="spark",
                                           var_file_name=filename,
                                           var_username=user_name,
                                           ts_uploaded_time=datetime.datetime.now())
        db_session.add(file_insert_values)
        db_session.commit()
        jar_uid = uuid.UUID(file_upload_id).hex
        data = TblCustomerSparkRequest(uid_customer_id=str(customer_id),
                                       var_user_name=user_name,
                                       uid_request_id=str(request_id),
                                       uid_cluster_id=str(cluster_id),
                                       uid_agent_id=agent_id[0],
                                       uid_jar_upload_id=str(jar_uid),
                                       var_spark_job_name=job_name,
                                       txt_job_description=job_description,
                                       var_job_parameters=job_parameters,
                                       int_request_status=1,
                                       var_created_by='system',
                                       var_modified_by='system',
                                       ts_modified_datetime=date_time,
                                       ts_created_datetime=date_time,
                                       ts_requested_time=date_time
                                       )
        db_session.add(data)
        db_session.commit()
        return jsonify(requestid=request_id, status="success")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


def fileProgres(start, size):
    my_logger.debug("%d%d", start, size)


@spark_update.route('/sparkjob/<agent_id>', methods=['GET'])
def sparkJobSubmit(agent_id):
    try:
        db_session = scoped_session(session_factory)
        customer_job_request_query = db_session.query(TblCustomerSparkRequest.uid_request_id,
                                                      TblCustomerSparkRequest.uid_customer_id,
                                                      TblCustomerSparkRequest.uid_cluster_id,
                                                      TblCustomerSparkRequest.txt_job_description,
                                                      TblCustomerSparkRequest.uid_jar_upload_id,
                                                      TblCustomerSparkRequest.var_job_parameters,
                                                      ).filter(
            TblCustomerSparkRequest.bool_assigned == 'f',TblCustomerSparkRequest.uid_agent_id==agent_id).all()
        list_spark_job = []
        if customer_job_request_query != []:
            for req_data in customer_job_request_query:
                request_id = req_data[0]
                customerid = req_data[1]
                clusterid = req_data[2]
                job_description = req_data[3]
                uid_jar_upload_id = req_data[4]
                job_parameters = req_data[5]
                resourcemanager_ip="192.168.100.179"
                file_information = db_session.query(TblFileUpload.var_file_name).filter(
                    TblFileUpload.uid_upload_id == uid_jar_upload_id)
                filename = file_information[0][0]
                spark_job_data = {}
                spark_job_data["request_id"] = request_id
                spark_job_data["customer_id"] = customerid
                spark_job_data["cluster_id"] = clusterid
                spark_job_data["filename"] = filename
                spark_job_data["jar_id"] = uid_jar_upload_id
                spark_job_data["job_description"] = job_description
                spark_job_data["job_parameters"] = job_parameters
                spark_job_data["resourcemanager_ip"] = resourcemanager_ip
                list_spark_job.append(spark_job_data)
                update_customer_request_query = db_session.query(TblCustomerSparkRequest).filter(TblCustomerSparkRequest.uid_request_id == request_id)
                update_customer_request_query.update({"bool_assigned": 1})
                db_session.commit()
                return jsonify(message=list_spark_job)
        else:
            return jsonify("null")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@spark_update.route('/sparkjobdiagnostics', methods=['POST'])
def sparkJobDiagnotics():
    try:
        db_session = scoped_session(session_factory)
        data = request.json
        spark_diagno = data['diagnostics']
        request_id = data['request_id']
        spark_insert = db_session.query(TblCustomerSparkRequest).filter(
            TblCustomerSparkRequest.uid_request_id == request_id)
        spark_insert.update({"var_job_diagnostics": spark_diagno})
        db_session.commit()
        return jsonify(message='Success')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@spark_update.route("/sparklist/<customer_id>/<cluster_id>", methods=['GET'])
def job_list(customer_id, cluster_id):
    try:
        db_session = scoped_session(session_factory)
        spark_request_query = db_session.query(TblCustomerSparkRequest.var_application_id,
                                               TblCustomerSparkRequest.var_job_diagnostics,
                                               TblCustomerSparkRequest.uid_request_id,
                                               TblCustomerSparkRequest.txt_job_description,
                                               TblCustomerSparkRequest.var_spark_job_name).filter(
            TblCustomerSparkRequest.uid_customer_id == customer_id,
            TblCustomerSparkRequest.uid_cluster_id == cluster_id).all()
        spark_list = []
        if len(spark_request_query) != 0:
            for each_job in spark_request_query:
                if each_job[2] is not None:
                    sri_job= eval(each_job[2])
                    spark_diagnostics = {}
                    spark_details=sri_job.values()
                    for valuessss in spark_details:
                        spark_diagnostics['application_id'] = each_job[0]
                        spark_diagnostics['task_startedTime'] = valuessss["startedTime"]
                        spark_diagnostics['task_endTime'] = valuessss["finishedTime"]
                        spark_diagnostics['spark_request_id'] = each_job[3]
                        spark_diagnostics['spark_app_description'] = each_job[4]
                        spark_diagnostics['spark_file_name'] = each_job[5]
                        spark_list.append(spark_diagnostics)
            return jsonify(spark_records=spark_list)
        else:
            return jsonify(spark_records='null')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@spark_update.route("/spark_status/<request_id>",methods=['GET'])
def mrJobStatus(request_id):
    try :
        session = scoped_session(session_factory)
        result_dict = {}
        customer_job_request_id_list = session.query(TblCustomerSparkRequest.var_status).filter(TblCustomerSparkRequest.uid_request_id == request_id).all()
        if customer_job_request_id_list == []:
            return jsonify(message="no jobs found for the request id")
        else:
            result_dict[request_id] = customer_job_request_id_list[0]
            return jsonify(result_dict)
    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
    finally:
        session.close()


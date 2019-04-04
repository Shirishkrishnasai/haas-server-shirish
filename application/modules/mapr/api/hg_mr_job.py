
import datetime
import io
from azure.storage.file import FileService
from configparser import ConfigParser
import uuid
import os,sys
from flask import request, Blueprint,jsonify
from sqlalchemy import and_
from application.models.models import TblCustomerJobRequest, TblMetaFileUpload, TblFileUpload,TblMetaCloudType,TblMetaVmSize,TblPlanClusterSizeConfig ,TblMetaMrRequestStatus
from application.common.loggerfile import my_logger
from sqlalchemy.orm import scoped_session
from application import session_factory
mrapi = Blueprint('mrapi', __name__)


@mrapi.route("/api/calculator", methods=['POST'])
def configuration():
    try:

        data = request.json
        filesize = data["filesize"]
        plan_id = data["plan_id"]
        size_id = data["size_id"]

        blocksize = 128
        map_tasks = int(filesize) / int(blocksize)
        db_session = scoped_session(session_factory)
        vm_size_info = db_session.query(TblMetaVmSize.var_vm_type).filter(
            and_(TblMetaVmSize.int_plan_id == plan_id, TblMetaVmSize.int_size_id == size_id,
                 TblMetaVmSize.var_role == "datanode"))
        vm_type = vm_size_info[0][0]
        vcores_data = db_session.query(TblMetaCloudType.float_cpu).filter(TblMetaCloudType.var_vm_type == vm_type).first()
        vcores=int(vcores_data[0])
        no_of_datanodes=db_session.query(TblPlanClusterSizeConfig.int_role_count).filter(
            and_(TblPlanClusterSizeConfig.int_plan_id == plan_id,TblPlanClusterSizeConfig.int_size_id == size_id,
                 TblPlanClusterSizeConfig.var_role == "datanode")).first()
        count=no_of_datanodes[0]
        vcores=vcores*count
        configurations_dict = {}
        if map_tasks <= vcores:
            configurations_dict["total_map_tasks"] = map_tasks
        else:
            configurations_dict["total_map_tasks"] = vcores
        configurations_dict["reducer_tasks"] = round(configurations_dict["total_map_tasks"] * 0.5)

        if configurations_dict["total_map_tasks"] < 2:
            configurations_dict["total_map_tasks"] = 2
        if configurations_dict["reducer_tasks"] < 2:
            configurations_dict["reducer_tasks"] = 2
        javaopts = 400
        configurations_dict["sortmb"] = int(0.4 * javaopts)
        configurations_dict["sortfactor"] = int(configurations_dict["sortmb"] / 10)
        configurations_dict["map_output_compress"] = 'true'
        configurations_dict["javaopts"] = "-Xmx" + str(javaopts) + "m"
        return jsonify(configurations_dict)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@mrapi.route("/api/addmrjob", methods=['POST'])
def hg_mrjob_client():

    #try:
        db_session = scoped_session(session_factory)
        request_id = str(uuid.uuid1())
        date_time = datetime.datetime.now()
        posted_args = request.args
        customer_request = request.values.to_dict()
        customer_id = str(customer_request["customer_id"])
        cluster_id = str(customer_request['cluster_id'])
        user_name = customer_request['user_name']
        job_name = customer_request['job_name']
        job_description = customer_request['job_description']
        filename = request.files['files'].filename
        job_parameters = customer_request['job_arguments']
        posted_file = request.files
        str_posted_file = posted_file['files'].read()
        no_of_bytes=len(str_posted_file)
	print cluster_id,"yyyyyyyyyyyyyyyyy"
        # converting unicoded file to bytestream
        byte_stream = io.BytesIO(str_posted_file)

        # reads config file to get accountname and key
        cfg = ConfigParser()
        cfg.read('application/config/azure_config.ini')
        account_name = cfg.get('file_storage', 'account_name')
        account_key = cfg.get('file_storage', 'key')

        # passing accountname and key to function
        file_service = FileService(account_name=account_name, account_key=account_key)
        # connecting to database to get sharename and directoryname against customerid
        file_service.create_file_from_stream(share_name=cluster_id,
                                             directory_name="mapreduce",
                                             file_name=filename,
                                             stream=byte_stream,
                                             count=no_of_bytes,
                                             progress_callback=fileProgress)

        file_upload_id = str(uuid.uuid1())
        file_insert_values = TblFileUpload(uid_upload_id=file_upload_id,
                                           uid_customer_id=customer_id,
                                           var_share_name=cluster_id,
                                           var_directory_name="mapreduce",
                                           var_file_name=filename,
                                           var_username=user_name,
                                           ts_uploaded_time=datetime.datetime.now())
        db_session.add(file_insert_values)
        db_session.commit()
        jar_uid = uuid.UUID(file_upload_id).hex
        data = TblCustomerJobRequest(uid_customer_id=str(customer_id),
                                     var_user_name=user_name,
                                     uid_request_id=str(request_id),
                                     uid_cluster_id=str(cluster_id),
                                     uid_jar_upload_id=str(jar_uid),
                                     var_job_name=job_name,
                                     txt_job_description=job_description,
                                     var_job_parameters=job_parameters,
                                     conf_mapreduce_framework_name='yarn',
                                     conf_mapreduce_task_io_sort_mb=(customer_request['sortmb']),
                                     conf_mapreduce_task_io_sort_factor=(customer_request['sortfactor']),
                                     conf_output_compress=1,
                                     int_request_status=1,
                                     conf_mapreduce_job_maps=(customer_request['total_map_tasks']),
                                     conf_mapreduce_job_reduces=(customer_request['reducer_tasks']),
                                     var_created_by='system',
                                     var_modified_by='system',
                                     ts_modified_datetime=date_time,
                                     ts_created_datetime=date_time,
                                     ts_requested_time=date_time,
                                     )
        db_session.add(data)
        db_session.commit()
        return jsonify(requestid=request_id,status="success")
    #except Exception as e:
     #    exc_type, exc_obj, exc_tb = sys.exc_info()
      #   fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
       #  my_logger.error(exc_type)
        # my_logger.error(fname)
         #my_logger.error(exc_tb.tb_lineno)
    #finally:
     #    db_session.close()


def fileProgress(start, size):
    my_logger.debug("%d%d", start, size)

mrjobstatus=Blueprint('mrjobstatus',__name__)
@mrjobstatus.route("/api/mrjobstatus/<mr_job_id>",methods=['GET'])
def mrJobStatus(mr_job_id):
    try :
        session = scoped_session(session_factory)
        result_dict = {}
        customer_job_request_id_list = session.query(TblCustomerJobRequest.int_request_status).filter(TblCustomerJobRequest.uid_request_id == mr_job_id).all()
        if customer_job_request_id_list == []:
            return jsonify(message="no jobs found for the request id")
        else:
            mr_request_id_list = session.query(TblMetaMrRequestStatus.var_mr_request_status).\
                filter(TblMetaMrRequestStatus.srl_id == customer_job_request_id_list[0][0]).all()
            result_dict[mr_job_id] = mr_request_id_list[0][0]
            return jsonify(result_dict)
    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
    finally:
        session.close()




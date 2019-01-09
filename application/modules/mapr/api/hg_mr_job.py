import requests
import datetime
import io
from azure.storage.file import FileService
from sqlalchemy import exc
from configparser import ConfigParser
from msrestazure.azure_exceptions import CloudError
import uuid
import lxml.etree as ET
from flask import request, Blueprint,jsonify
from sqlalchemy import and_
from application.config.config_file import file_upload_url, path
from application.models.models import TblCustomerJobRequest, TblMetaFileUpload, TblFileUpload,TblMetaCloudType,TblMetaVmSize,TblPlanClusterSizeConfig ,TblMetaMrRequestStatus
from application.common.loggerfile import my_logger
from sqlalchemy.orm import scoped_session
from application import session_factory
from werkzeug.datastructures import ImmutableMultiDict
import json

mrapi = Blueprint('mrapi', __name__)


@mrapi.route("/api/calculator", methods=['POST'])
def configuration():
    try:


        data = request.json
        filesize = data["filesize"]
        plan_id = data["plan_id"]
        size_id = data["size_id"]
        my_logger.info(size_id)
        blocksize = 128
        map_tasks = int(filesize) / int(blocksize)
        db_session = scoped_session(session_factory)
        vm_size_info = db_session.query(TblMetaVmSize.var_vm_type).filter(
            and_(TblMetaVmSize.int_plan_id == plan_id, TblMetaVmSize.int_size_id == size_id,
                 TblMetaVmSize.var_role == "datanode"))
        my_logger.info(vm_size_info)
        vm_type = vm_size_info[0][0]
        my_logger.info(vm_type)
        vcores_data = db_session.query(TblMetaCloudType.float_cpu).filter(TblMetaCloudType.var_vm_type == vm_type).first()
        vcores=int(vcores_data[0])
        my_logger.info(vcores)
        no_of_datanodes=db_session.query(TblPlanClusterSizeConfig.int_role_count).filter(
            and_(TblPlanClusterSizeConfig.int_plan_id == plan_id,TblPlanClusterSizeConfig.int_size_id == size_id,
                 TblPlanClusterSizeConfig.var_role == "datanode")).first()
        count=no_of_datanodes[0]
        my_logger.info(count)
        vcores=vcores*count
        my_logger.info(vcores)
        my_logger.info('finalllllllllllllll')


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
        my_logger.info(configurations_dict)
        return jsonify(configurations_dict)

    except exc.SQLAlchemyError as e:
        return jsonify(e.message)
    except Exception as e:
        return jsonify(e.message)
    finally:
        db_session.close()
        return jsonify("ok")

@mrapi.route("/api/addmrjob", methods=['POST'])
def hg_mrjob_client():

    try:
        #data = dict(request.form)
        #data = request.values
        #my_logger.info(dir(request))
        #my_logger.info(data['cluster_id'])

        #my_logger.info(data)

        request_id = str(uuid.uuid1())
        date_time = datetime.datetime.now()
        posted_args = request.args
        input_path = posted_args['input_file_path']
        output_path = posted_args['output_file_path']
        my_logger.info(input_path)
        customer_request = request.values
        my_logger.info(customer_request)
        customer_id = customer_request['customer_id']
        my_logger.info(customer_id)
        cluster_id = customer_request['cluster_id']
        my_logger.info(cluster_id)
        user_name = customer_request['user_name']
        my_logger.info(user_name )
        job_name = customer_request['job_name']
        my_logger.info(job_name)
        job_description = customer_request['job_description']
        my_logger.info(job_description)
        #my_logger.info("hey"
        filename = request.files['files'].filename
        my_logger.info('nameeeeeeeeeeeeeeeeeeee')
        posted_file = request.files
        my_logger.info(filename) 
        my_logger.info(posted_file)
        str_posted_file = posted_file['files'].read()
        my_logger.info(str_posted_file)
        utf_posted_file = str_posted_file.encode('base64')
        # getting no of bytes to give value for count
        no_of_bytes = len(utf_posted_file)
        my_logger.info(no_of_bytes)

        # converting unicoded file to bytestream
        byte_stream = io.BytesIO(utf_posted_file)

        # reads config file to get accountname and key
        cfg = ConfigParser()
        cfg.read('application/config/azure_config.ini')
        account_name = cfg.get('file_storage', 'account_name')
        account_key = cfg.get('file_storage', 'key')

        # passing accountname and key to function
        file_service = FileService(account_name=account_name, account_key=account_key)
        my_logger.info('file account credentials ok')

        # connecting to database to get sharename and directoryname against customerid
        db_session = scoped_session(session_factory)
        share_values = db_session.query(TblMetaFileUpload.var_share_name, TblMetaFileUpload.var_directory_name).\
            filter(TblMetaFileUpload.uid_customer_id == customer_id).first()
        my_logger.info(share_values)

        my_logger.info(byte_stream)
        file_service.create_file_from_stream(share_name=share_values[0],
                                             directory_name=share_values[1],
                                             file_name=filename,
                                             stream=byte_stream,
                                             count=no_of_bytes,
                                             progress_callback=fileProgress)
        my_logger.info('file transfer is over')
        my_logger.info('file created in azure file storage')
        my_logger.info('now inserting values in database')

        file_upload_id = str(uuid.uuid1())
        my_logger.info(file_upload_id)

        my_logger.info("passed argument is user_name")
        file_insert_values = TblFileUpload(uid_upload_id=file_upload_id,
                                           uid_customer_id=customer_id,
                                           var_share_name=share_values[0],
                                           var_directory_name=share_values[1],
                                           var_file_name=filename,
                                           var_username=user_name,
                                           ts_uploaded_time=datetime.datetime.now())
        db_session.add(file_insert_values)
        db_session.commit()
        my_logger.info('values inserted and now returning file file_upload_url')
        my_logger.info(file_upload_id)
        jar_uid = file_upload_id
        with open('/opt/mapred-site.xml')as f:
            my_logger.info("in file opennnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")

            tree = ET.parse(f)
            root = tree.getroot()
            for elem in root.getiterator():
                try:

                    elem.text = elem.text.replace('mapsvalue', str(customer_request["total_map_tasks"]))
                    elem.text = elem.text.replace('reducesvalue', str(customer_request["reducer_tasks"]))
                    elem.text = elem.text.replace('sortmb', str(customer_request["sortmb"]))
                    elem.text = elem.text.replace('sortfactor', str(customer_request["sortfactor"]))
                    elem.text = elem.text.replace('javaopts', str(customer_request["javaopts"]))
                    elem.text = elem.text.replace('outputcompress', str(customer_request["map_output_compress"]))
                    my_logger.info("tryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy endedddddddddddddddddd")
                except AttributeError:
                    pass

        # Adding the xml_declaration and method helped keep the header info at the top of the file.
        tree.write('/opt/mapred-site.xml', xml_declaration=True, method='xml', encoding="utf8")
        up = {'files': open(path, 'rb')}
        params = {"user_name": user_name, "customer_id": customer_id}
        r = requests.post(file_upload_url, files=up, params=params)
        conf_uid = r.text
        my_logger.info('hiiiiiiiiiiiiiiiiiiiii uuuuuuuuuuuuuuuiiiiiiiiiiiiidddddddddddd')
        data = TblCustomerJobRequest(uid_customer_id=customer_id,
                                     var_user_name=user_name,
                                     uid_request_id=request_id,
                                     uid_cluster_id=cluster_id,
                                     uid_conf_upload_id=conf_uid,
                                     uid_jar_upload_id=jar_uid,
                                     var_job_name=job_name,
                                     txt_job_description=job_description,
                                     var_input_file_path=input_path,
                                     var_output_file_path=output_path,
                                     conf_mapreduce_framework_name='yarn',
                                     conf_mapreduce_task_io_sort_mb=int(customer_request["sortmb"]),
                                     conf_mapreduce_task_io_sort_factor=int(customer_request["sortfactor"]),
                                     conf_output_compress=1,
                                     conf_mapreduce_job_maps=int(customer_request["total_map_tasks"]),
                                     conf_mapreduce_job_reduces=int(customer_request["reducer_tasks"]),
                                     var_created_by='system',
                                     var_modified_by='system',
                                     ts_modified_datetime=date_time,
                                     ts_created_datetime=date_time,
                                     ts_requested_time=date_time,
                                     )
        db_session.add(data)
        db_session.commit()
        my_logger.info("commmmmmmmmmmmmmmmmmmmmmmmmmmmmiiiiiiiiiiiiiiiitttttttttttttttttttttttttttttteeeeeeeeeeeeeeeeeeeedddddddddddddddd")

        with open('/opt/mapred-site.xml')as f:
            tree = ET.parse(f)
            root = tree.getroot()

            for elem in root.getiterator():
                try:
                    #my_logger.info('i am almost done')
                    elem.text = elem.text.replace(str(customer_request["total_map_tasks"]), 'mapsvalue')
                    elem.text = elem.text.replace(str(customer_request["reducer_tasks"]), 'reducesvalue')
                    elem.text = elem.text.replace(str(customer_request["sortmb"]), 'sortmb')
                    elem.text = elem.text.replace(str(customer_request["sortfactor"]), 'sortfactor')
                    elem.text = elem.text.replace(str(customer_request["javaopts"]), 'javaopts')
                    elem.text = elem.text.replace(str(customer_request["map_output_compress"]), 'outputcompress')
                except AttributeError:
                    pass

        # Adding the xml_declaration and method helped keep the header info at the top of the file.
        tree.write('/opt/mapred-site.xml', xml_declaration=True, method='xml', encoding="utf8")
        f.close()
        db_session.close()
        my_logger.info("hello")
        return jsonify(message=request_id)
    except exc.SQLAlchemyError as e:
        my_logger.info(e)
        my_logger.error(e)
        return jsonify(e)
    except Exception as e:
        my_logger.info(e)
        my_logger.error(e)
    finally:
        my_logger.info("done")
        #return "in finall"


def fileProgress(start, size):
    my_logger.debug("%d%d", start, size)

mrjobstatus=Blueprint('mrjobstatus',__name__)
@mrjobstatus.route("/api/mrjobstatus/<mr_job_id>",methods=['GET'])
def mrJobStatus(mr_job_id):
    my_logger.info("inside")
    #data = request.headers
    #data= request.args
    #my_logger.info(data,type(data)
    #my_logger.info(data,type(data)
    #id_list = data["mr_job_id"]
    #my_logger.info(id_list,type(id_list),"lllllllll"
    #id_data = eval(mr_job_id)
    #my_logger.info(id_data,type(id_data)
    session = scoped_session(session_factory)
    result_dict = {}
    #for ids in id_data :
    #    my_logger.info(ids,type(ids))
    customer_job_request_id_list = session.query(TblCustomerJobRequest.int_request_status).filter(TblCustomerJobRequest.uid_request_id == mr_job_id).all()
    my_logger.info(customer_job_request_id_list)
    for mr_request_id in customer_job_request_id_list:
        mr_request_id_list = session.query(TblMetaMrRequestStatus.var_mr_request_status).filter(TblMetaMrRequestStatus.srl_id == mr_request_id).all()
        my_logger.info(mr_request_id_list)
        result_dict[mr_job_id] = mr_request_id_list[0][0]
    my_logger.info(result_dict)
    return jsonify(result_dict)

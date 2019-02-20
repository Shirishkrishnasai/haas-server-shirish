import io
from azure.storage.file import FileService, FilePermissions
from configparser import ConfigParser
from msrestazure.azure_exceptions import CloudError
from flask import Flask, jsonify, request, Blueprint
from datetime import datetime
from application.models.models import TblMetaFileUpload, TblFileUpload
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.loggerfile import my_logger
import uuid

azfile = Blueprint('azfile', __name__)


@azfile.route("/fileupload", methods=['POST'])
def fileUpload():
    try:

        posted_args = request.args
        print posted_args
        copied_args = posted_args.copy()
        print copied_args
        normal_dict = dict(copied_args)
        my_logger.debug(normal_dict)
        print normal_dict
        customerid = normal_dict['customer_id'][0]

        # getting filename and file
        filename = request.files['files'].filename
        posted_file = request.files

        # converts posted file to string
        str_posted_file = posted_file['files'].read()
        # print str_posted_file

        # converting file string to unicode
        utf_posted_file = str_posted_file.encode('base64')

        # getting no of bytes to give value for count
        no_of_bytes = len(utf_posted_file)
        print no_of_bytes

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
        share_values = db_session.query(TblMetaFileUpload.var_share_name, TblMetaFileUpload.var_directory_name). \
            filter(TblMetaFileUpload.uid_customer_id == customerid).first()
        my_logger.debug(share_values)
        try:

            print byte_stream
            file_service.create_file_from_stream(share_name=share_values[0],
                                                 directory_name=share_values[1],
                                                 file_name=filename,
                                                 stream=byte_stream,
                                                 count=no_of_bytes,
                                                 progress_callback=fileProgress,content_type=application/java-archive)
            my_logger.info('file transfer is over')
            my_logger.info('file created in azure file storage')
            my_logger.info('now inserting values in database')

            file_upload_id = str(uuid.uuid1())

            if normal_dict.has_key('agent_id'):
                my_logger.info("passed argiment is agent_id")
                agent_id_value = normal_dict['agent_id'][0]

                file_insert_values = TblFileUpload(uid_upload_id=str(file_upload_id),
                                                   uid_customer_id=str(customerid),
                                                   var_share_name=share_values[0],
                                                   var_directory_name=share_values[1],
                                                   var_file_name=filename,
                                                   uid_agent_id=agent_id_value,
                                                   ts_uploaded_time=datetime.now())
                db_session.add(file_insert_values)
                db_session.commit()
                db_session.close()
                my_logger.info('values inserted and now returning file url')
                return file_upload_id

            elif normal_dict.has_key('user_name'):
                my_logger.info("passed argument is user_name")
                user_name_value = normal_dict['user_name'][0]
                file_insert_values = TblFileUpload(uid_upload_id=str(file_upload_id),
                                                   uid_customer_id=str(customerid),
                                                   var_share_name=share_values[0],
                                                   var_directory_name=share_values[1],
                                                   var_file_name=filename,
                                                   var_username=user_name_value,
                                                   ts_uploaded_time=datetime.now())
                db_session.add(file_insert_values)
                db_session.commit()
                my_logger.info('values inserted and now returning file url')
                return file_upload_id
        except Exception as e:
            my_logger.error(e)
    except CloudError as e:
        my_logger.debug("Got Cloud Error")
        my_logger.error(e)
    except Exception as e:
        my_logger.debug("Got Exception")
        my_logger.error(e)
    finally:
        my_logger.debug("its finally block and its over")
        db_session.close()

def fileProgress(start, size):
    my_logger.debug("%d %d", start, size)


@azfile.route("/fileuploadbytes", methods=['POST'])
def fileUploadBytes():
    try:

        posted_args = request.args
        print posted_args
        copied_args = posted_args.copy()
        print copied_args
        normal_dict = dict(copied_args)
        my_logger.debug(normal_dict)
        print normal_dict
        customerid = normal_dict['customer_id'][0]

        # getting filename and file
        filename = request.files['files'].filename
        posted_file = request.files

        # converts posted file to string
        str_posted_file = posted_file['files'].read()

        # converting file string to bytes
        byte_array = bytes(str_posted_file)
        sizy = len(byte_array)
        print "yeah----------yeah------------yeahhhhhhhhhhhhhhhhh", sizy

        print 'hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii', type(byte_array)
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
        share_values = db_session.query(TblMetaFileUpload.var_share_name, TblMetaFileUpload.var_directory_name). \
            filter(TblMetaFileUpload.uid_customer_id == customerid).first()
        my_logger.debug(share_values)
        # print byte_array
        try:
            # print byte_array
            # for i in range(sizy):

            file_service.create_file_from_bytes(share_name=share_values[0],
                                                directory_name=share_values[1],
                                                file_name=filename,
                                                file=byte_array,
                                                index=0,
                                                count=273437,
                                                progress_callback=fileProgress)

            my_logger.info('file transfer is over')
            my_logger.info('file created in azure file storage')
            my_logger.info('now inserting values in database')

            file_upload_id = str(uuid.uuid1())

            if normal_dict.has_key('agent_id'):
                my_logger.info("passed argiment is agent_id")
                agent_id_value = normal_dict['agent_id'][0]

                file_insert_values = TblFileUpload(uid_upload_id=file_upload_id,
                                                   uid_customer_id=customerid,
                                                   var_share_name=share_values[0],
                                                   var_directory_name=share_values[1],
                                                   var_file_name=filename,
                                                   uid_agent_id=agent_id_value,
                                                   ts_uploaded_time=datetime.now())
                db_session.add(file_insert_values)
                db_session.commit()
                db_session.close()
                my_logger.info('values inserted and now returning file url')
                return file_upload_id

            elif normal_dict.has_key('user_name'):
                my_logger.info("passed argument is user_name")
                user_name_value = normal_dict['user_name'][0]
                file_insert_values = TblFileUpload(uid_upload_id=file_upload_id,
                                                   uid_customer_id=customerid,
                                                   var_share_name=share_values[0],
                                                   var_directory_name=share_values[1],
                                                   var_file_name=filename,
                                                   var_username=user_name_value,
                                                   ts_uploaded_time=datetime.now())
                db_session.add(file_insert_values)
                db_session.commit()
                db_session.close()
                my_logger.info('values inserted and now returning file url')
                return file_upload_id
        except Exception as e:
             my_logger.error(e)
    except CloudError as e:
        my_logger.debug("Got Cloud Error")
        my_logger.error(e)
    except Exception as e:
        my_logger.debug("Got Exception")
        my_logger.error(e)
    finally:
        my_logger.debug("its finally block and its over")
        db_session.close()


def fileProgress(start, size):
    my_logger.debug("%d%d", start, size)


@azfile.route("/createdirectory", methods=['POST'])
def createDirectory():
    # u should have clusterid,customerid

    # try:

    # reads config file to get accountname and key
    customerid = 1
    clusterid = 2
    cfg = ConfigParser()
    cfg.read('application/config/azure_config.ini')
    account_name = cfg.get('file_storage', 'account_name')
    account_key = cfg.get('file_storage', 'key')

    # passing accountname and key to function
    file_service = FileService(account_name=account_name, account_key=account_key)
    my_logger.info('file account credentials ok')

    # connecting to database to get sharename and directoryname against customerid
    db_session = scoped_session(session_factory)
    # share_values = db_session.query(TblMetaFileUpload.var_share_name, TblMetaFileUpload.var_directory_name). \
    #   filter(TblMetaFileUpload.uid_customer_id == customerid).first()
    # share_name = db_session.query(TblMetaFileUpload.var_share_name).filter(TblMetaFileUpload.uid_customer_id == customerid).first()
    # my_logger.debug(share_name)
    share_name = 'haasfiles'
    directory_creation = file_service.create_directory(share_name=share_name, directory_name=clusterid / clusterid,
                                                       metadata=None, fail_on_exist=True, timeout=None)
    if directory_creation:
        print "directory created"
    else:
        print "directory nottttttt created, try again"

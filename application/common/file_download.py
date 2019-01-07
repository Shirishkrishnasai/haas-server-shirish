from azure.storage.file import FileService,FilePermissions
from configparser import ConfigParser
from msrestazure.azure_exceptions import CloudError
from flask import request,Blueprint,jsonify
from datetime import datetime, timedelta
from application.models.models import TblFileUpload,TblFileDownload
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.loggerfile import my_logger

azfiledownload = Blueprint('azfiledownload',__name__)

@azfiledownload.route("/filedownload/<uploadid>",methods=['GET'])
def fileDownload(uploadid):
        try:

            #reads config file to get accountname and key
            cfg = ConfigParser()
            cfg.read('application/config/azure_config.ini')
            account_name=cfg.get('file_storage','account_name')
            account_key = cfg.get('file_storage','key')

            #passing accountname and key to function
            file_service = FileService(account_name=account_name, account_key=account_key)
            my_logger.info('file account credentials ok')

            #connecting to database to get sharename and directoryname against customerid
            db_session = scoped_session(session_factory)
            file_values = db_session.query(TblFileUpload.var_share_name,
                                           TblFileUpload.var_directory_name,
                                           TblFileUpload.var_file_name).filter(TblFileUpload.uid_upload_id==uploadid).first()
            my_logger.debug(file_values)
            try:

                #creating expiry date for access signature and converting to str as expiry sparam shouldnt contain tzinfo
                expiry_date=str(datetime.now().date()+timedelta(days=3))

                access_signature = file_service.generate_file_shared_access_signature(share_name=file_values[0],
                                                                                      directory_name=file_values[1],
                                                                                      file_name=file_values[2],
                                                                                      permission=FilePermissions.READ,
                                                                                      expiry=expiry_date)
                my_logger.info('access signature is generated')
                my_logger.info('now creating fileurl to access')
                #getting file url
                file_url = file_service.make_file_url(share_name=file_values[0],
                                                      directory_name=file_values[1],
                                                      file_name=file_values[2],
                                                      protocol='https',
                                                      sas_token=access_signature)
                my_logger.info('file url generated')
                my_logger.info('inserting values into file upload table')

                #getting arguments
                posted_args = request.args
                copied_args = posted_args.copy()
                normal_dict = dict(copied_args)
                my_logger.debug(normal_dict)

                if normal_dict.has_key('agent_id'):
                    my_logger.info("passed argument is agent_id")
                    agent_id_value = normal_dict['agent_id'][0]
                    file_download_insert_values = TblFileDownload(uid_upload_id = str(uploadid),
                                                                  var_file_name = file_values[2],
                                                                  txt_file_url = file_url,
                                                                  uid_agent_id=agent_id_value,
                                                                  ts_file_expiry_time = expiry_date,
                                                                  ts_requested_time = datetime.now())
                    db_session.add(file_download_insert_values)
                    db_session.commit()
                    db_session.close()
                    my_logger.info("file url inserted into database now returning url")
                    return file_url

                elif normal_dict.has_key('user_name'):
                    my_logger.info("passed argument is user_name")
                    user_name_value = normal_dict['user_name'][0]
                    file_download_insert_values = TblFileDownload(uid_upload_id=uploadid,
                                                                  var_username=user_name_value,
                                                                  var_file_name=file_values[2],
                                                                  txt_file_url=file_url,
                                                                  ts_file_expiry_time=expiry_date,
                                                                  ts_requested_time=datetime.now())
                    db_session.add(file_download_insert_values)
                    db_session.commit()
                    db_session.close()
                    my_logger.info("file url committed to database now returning url")
                    return file_url
                else:
                    return jsonify(message="not enough values given")


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


def fileProgress(start, size):
    my_logger.debug("%d%d",start, size)

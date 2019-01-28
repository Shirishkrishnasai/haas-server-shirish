from apscheduler.schedulers.background import BackgroundScheduler

from azure.storage.file import FileService,FilePermissions
from configparser import ConfigParser
from msrestazure.azure_exceptions import CloudError
from flask import Flask,jsonify,request,Blueprint
from datetime import datetime
from application.models.models import TblMetaFileUpload,TblFileUpload,TblHiveRequest
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.loggerfile import my_logger
from sqlalchemy import and_
import sys,os
from datetime import datetime, timedelta



def selectQueryUrl():
    #while True:
        #try:
            # reads config file to get accountname and key
            print "heyyyyyyyyyyyyyyyyyyyyyyyyyy"
            cfg = ConfigParser()
            cfg.read('application/config/azure_config.ini')
            account_name = cfg.get('file_storage', 'account_name')
            account_key = cfg.get('file_storage', 'key')

            # passing accountname and key to function
            file_service = FileService(account_name=account_name, account_key=account_key)
            print('file account credentials ok')
            print "in hive select query url creating file"

            db_session = scoped_session(session_factory)
            hive_request_ids = db_session.query(TblHiveRequest.uid_cluster_id,
                                                TblHiveRequest.uid_hive_request_id).filter\
                (and_(TblHiveRequest.bool_select_query=='t',TblHiveRequest.bool_url_created=='f')).all()
            print hive_request_ids

        #conditions select query and bool url created
            for each_tuple in hive_request_ids:
                direcs = list(file_service.list_directories_and_files(share_name=each_tuple[0],
                                                                 directory_name='hive'))
                print direcs

                for dire in direcs:
                    print dire.name

                # creating expiry date for access signature and converting to str as expiry sparam shouldnt contain tzinfo
                expiry_date = str(datetime.now().date() + timedelta(days=3))

                access_signature = file_service.generate_file_shared_access_signature(share_name=each_tuple[0],
                                                                                      directory_name='hive',
                                                                                      file_name=each_tuple[1],
                                                                                      permission=FilePermissions.READ,
                                                                                      expiry=expiry_date)
                print('access signature is generated')
                print('now creating fileurl to access')
                # getting file url
                file_url = file_service.make_file_url(share_name=each_tuple[0],
                                                      directory_name='hive',
                                                      file_name=each_tuple[1],
                                                      protocol='https',
                                                      sas_token=access_signature)
                print('file url generated')
                print('inserting values into file upload table')
                hive_request_tbl_url_update = db_session.query(TblHiveRequest.txt_url_value).filter(TblHiveRequest.uid_hive_request_id==each_tuple[1])
                hive_request_tbl_url_update.update({"txt_url_value":str(file_url),
                                                    "bool_url_created":1})
                db_session.commit()
            db_session.close()

        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     my_logger.error(exc_type)
        #     my_logger.error(fname)
        #     my_logger.error(exc_tb.tb_lineno)


def hgSelectQueryUrlScheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(selectQueryUrl,'cron',minute='*/1')
    scheduler.start()
    print("in hgselectqueryurl")
    print "in select query urllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"


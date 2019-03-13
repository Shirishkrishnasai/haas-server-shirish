from flask import Blueprint,request
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerRequestHdfs
from application.common.loggerfile import my_logger
import sys,os,json

hdfsoutputupload=Blueprint('hdfsoutputupload',__name__)
@hdfsoutputupload.route('/api/upload',methods=["POST"])
def hdfs_result_upload():
    try:
        hdfs_output_json=request.json
        print hdfs_output_json
        db_session = scoped_session(session_factory)
        hdfs_customer_request=db_session.query(TblCustomerRequestHdfs).filter(TblCustomerRequestHdfs.uid_hdfs_request_id==hdfs_output_json['request_id'])
        hdfs_customer_request.update({"hdfs_command_output":str(hdfs_output_json['output'])})
        db_session.commit()
        #hddddddfs
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()
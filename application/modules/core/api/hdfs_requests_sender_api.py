from flask import jsonify, Blueprint
from application.models.models import TblCustomerRequestHdfs,TblAgent
from sqlalchemy.orm import scoped_session
from application import session_factory
import sys,os,json

hdfsrequestsender = Blueprint('hdfsrequestsender', __name__)
@hdfsrequestsender.route("/api/hdfsrequests", methods=['GET'])
def request_sender():
    try:
        db_session = scoped_session(session_factory)
        hdfs_requests_query = db_session.query(TblCustomerRequestHdfs.uid_hdfs_request_id,TblCustomerRequestHdfs.uid_customer_id,TblCustomerRequestHdfs.uid_cluster_id,TblCustomerRequestHdfs.uid_agent_id,TblCustomerRequestHdfs.var_user_name,TblCustomerRequestHdfs.txt_command_string,TblCustomerRequestHdfs.txt_hdfs_parameters).all()
        requests_list=[]
        for requests in hdfs_requests_query:
            hdfs_request_dict={}psycopg2
            agent_ip_query = db_session.query(TblAgent.private_ips).filter(TblAgent.uid_agent_id == requests[3]).all()
            hdfs_request_dict['hdfs_request_id']=requests[0]
            hdfs_request_dict['customer_id']=requests[1]
            hdfs_request_dict['cluster_id']=requests[2]
            hdfs_request_dict['agent_id']=requests[3]
            hdfs_request_dict['user_name']=requests[4]
            hdfs_request_dict['namenode_ip']=agent_ip_query[0][0]
            if requests[5] == 'status':
                hdfs_request_dict['command_type']='fsck'
            elif requests[5] == 'create directory':
                hdfs_request_dict['command_type']='mkdir'
            elif requests[5] == 'text file':
                hdfs_request_dict['command_type']='text'
            elif requests[5] == 'move':
                hdfs_request_dict['command_type']='mv'
            else:
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
import time,os,sys

from application import session_factory
from application.config.config_file import kafka_bootstrap_server
from application.models.models import TblCustomerJobRequest, TblAgent, TblNodeInformation, TblMetaMrRequestStatus
from sqlalchemy.orm import scoped_session
from kafka import KafkaProducer
from application.common.loggerfile import my_logger

def mrjobproducer():
    while True:
        try:
            db_session = scoped_session(session_factory)
            meta_request_status_query=db_session.query(TblMetaMrRequestStatus.srl_id).filter(TblMetaMrRequestStatus.var_mr_request_status == 'CREATED').all()
            print meta_request_status_query[0][0],"in"
            customer_job_request_query = db_session.query(TblCustomerJobRequest.uid_request_id,TblCustomerJobRequest.uid_customer_id,TblCustomerJobRequest.uid_cluster_id,
                                            TblCustomerJobRequest.uid_conf_upload_id,TblCustomerJobRequest.uid_jar_upload_id).filter(TblCustomerJobRequest.int_request_status == meta_request_status_query[0][0],TblCustomerJobRequest.bool_assigned == 'f').all()

            for req_data in customer_job_request_query:
                print req_data
                request_id=req_data[0]
                customerid=req_data[1]
                clusterid=req_data[2]
                uid_conf_upload_id=req_data[3]
                uid_jar_upload_id=req_data[4]


                resourcemanager_data=db_session.query(TblAgent.uid_agent_id,TblAgent.private_ips).filter(TblAgent.uid_node_id==TblNodeInformation.uid_node_id)\
                                    .filter(TblNodeInformation.char_role=="resourcemanager",TblNodeInformation.uid_cluster_id==clusterid).first()

                agent_id=resourcemanager_data[0]
                private_ip=resourcemanager_data[1]

                producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_server)
                kafkatopic="mrjob_"+customerid+"_"+clusterid
                kafkatopic = kafkatopic.decode('utf-8')
                mrjob_data={}
                mrjob_data["event_type"]= "mapreducejob"
                mrjob_data["request_id"]=request_id
                mrjob_data["customer_id"]=customerid
                mrjob_data["cluster_id"]=clusterid
                mrjob_data["agent_id"]=agent_id
                mrjob_data["uid_conf_upload_id"]=uid_conf_upload_id
                mrjob_data["uid_jar_upload_id"]=uid_jar_upload_id
                mrjob_data["resourcemanager_ip"]=str(private_ip)
                producer.send(kafkatopic, str(mrjob_data))
                time.sleep(1)
                producer.flush()
                update_customer_request_query=db_session.query(TblCustomerJobRequest).filter(TblCustomerJobRequest.uid_request_id==request_id)
                update_customer_request_query.update({"bool_assigned":1})
                db_session.commit()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
        finally:
            print "mapr job_producer in Finally"
            db_session.close()
        time.sleep(15)

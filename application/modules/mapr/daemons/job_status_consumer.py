from kafka import KafkaConsumer
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest,TblMetaMrRequestStatus
import json,os,sys
from application.common.loggerfile import my_logger


def statusconsumer():
    try:
        session = scoped_session(session_factory)
        my_logger.info("in status consumerrrrrrrrrrrrrrrrrrrrrr")
        consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server)
        consumer.subscribe(pattern='job_status*')
        my_logger.info("after subscribesssssssssssssssssssssssssssss")
        for message in consumer:

            job_data = message.value
            my_logger.info(job_data)
            my_logger.info("innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
            data = job_data.replace("'", '"')
            json_loads_job_data = json.loads(data)
            my_logger.info(json_loads_job_data['customer_id'])
            my_logger.info(json_loads_job_data['application_id'])
            meta_request_status_query = session.query(TblMetaMrRequestStatus.srl_id).filter(TblMetaMrRequestStatus.var_mr_request_status == json_loads_job_data['status'])

            update_customer_job_request=session.query(TblCustomerJobRequest).filter(TblCustomerJobRequest.uid_customer_id==json_loads_job_data['customer_id'],TblCustomerJobRequest.var_application_id==json_loads_job_data['application_id'])
            # my_logger.info(update_customer_job_request
            update_customer_job_request.update({"int_request_status":meta_request_status_query[0][0]})
            session.commit()
            my_logger.info('in')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
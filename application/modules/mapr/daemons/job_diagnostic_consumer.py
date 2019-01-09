from kafka import KafkaConsumer
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest
import json,os,sys
from application.common.loggerfile import my_logger

def diagnosticsconsumer():
    try:
        session = scoped_session(session_factory)
        my_logger.info("in job diagnostics consumerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")

        consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server)
        consumer.subscribe(pattern='job_diagnostics*')
        my_logger.info("after subscribesssssssssssssssssssssssssssss , diganoooooooooooo")
        for message in consumer:
            job_data = message.value
            my_logger.info(job_data)
            my_logger.info("innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
            data = job_data.replace("'", '"')
            json_loads_job_data = json.loads(data)
            update_customer_job_request=session.query(TblCustomerJobRequest).filter(TblCustomerJobRequest.uid_customer_id==json_loads_job_data['customer_id'],TblCustomerJobRequest.uid_request_id==json_loads_job_data['request_id'])
            update_customer_job_request.update({"var_request_status":json_loads_job_data})
            session.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)


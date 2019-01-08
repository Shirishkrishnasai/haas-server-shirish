from kafka import KafkaConsumer
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest
import json,os,sys
from application.common.loggerfile import my_logger


def jobinsertion():
    try:
        print 'insert application id'
        consumer=KafkaConsumer(bootstrap_servers=kafka_bootstrap_server)
        print 'in consumer'
        consumer.subscribe(pattern='mrjobapplication_*')
        print consumer
        session = scoped_session(session_factory)
        for message in consumer:

            job_information=message.value
            print job_information,'job'
            data = job_information.replace("'", '"')
            print data
            job_information_dict = json.loads(data)
            print 'in'
            print job_information_dict['request_id']
            print job_information_dict['application_id']
            update_customer_job_request=session.query(TblCustomerJobRequest).filter(TblCustomerJobRequest.uid_request_id == "4953039a-e807-11e8-aed7-3ca9f491576c")
            print update_customer_job_request,"in"
            update_customer_job_request.update({"var_application_id":job_information_dict['application_id']})
            session.commit()
            session.close()
            print 'completed'
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
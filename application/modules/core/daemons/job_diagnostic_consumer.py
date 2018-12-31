from kafka import KafkaConsumer
from application.config.config_file import kafka_bootstrap_server, kafka_api_version
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomerJobRequest
import json

def diagnosticsconsumer():
    try:
        session = scoped_session(session_factory)
        print "in job diagnostics consumerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"

        consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_server)
        consumer.subscribe(pattern='job_diagnostics*')
        print "after subscribesssssssssssssssssssssssssssss , diganoooooooooooo"
        for message in consumer:
            job_data = message.value
            print job_data,"innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"
            data = job_data.replace("'", '"')
            json_loads_job_data = json.loads(data)
            update_customer_job_request=session.query(TblCustomerJobRequest).filter(TblCustomerJobRequest.uid_customer_id==json_loads_job_data['customer_id'],TblCustomerJobRequest.uid_request_id==json_loads_job_data['request_id'])
            update_customer_job_request.update({"var_request_status":json_loads_job_data})
            session.commit()
    except Exception as e:
		return e.message


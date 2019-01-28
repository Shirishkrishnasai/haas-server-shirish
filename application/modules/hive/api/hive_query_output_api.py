import yaml
from flask import jsonify, request, Blueprint
from application.models.models import TblHiveRequest
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.loggerfile import my_logger
import json,sys,os
hivequeryoutput = Blueprint('hivequeryoutput', __name__)
@hivequeryoutput.route("/hivequeryoutput", methods = ['POST'])
def hiveQueryOutput():
   try:


        hive_query_result = request.json
        print hive_query_result
        message = hive_query_result
        if message.has_key('output'):
            decoded_output = json.loads(message['output'].decode('base64', 'strict'))
            decoded_output = yaml.load(decoded_output)
            message['output'] = decoded_output
            print message, type(
                message), 'message', message.keys()

        db_session = scoped_session(session_factory)
        query_output = db_session.query(TblHiveRequest.hive_query_output).filter(TblHiveRequest.uid_hive_request_id == message['hive_request_id'])
        query_output.update({"hive_query_output":str(message)})
        db_session.commit()
        db_session.close()
        print "all hive query output is inserted to table"
        return jsonify(message="success")
   except Exception as e:
       exc_type, exc_obj, exc_tb = sys.exc_info()
       fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
       my_logger.error(exc_type)
       my_logger.error(fname)
       my_logger.error(exc_tb.tb_lineno)

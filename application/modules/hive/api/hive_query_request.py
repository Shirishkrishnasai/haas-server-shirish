import re,datetime,os,sys
from flask import jsonify, Blueprint
from application.models.models import TblHiveMetaStatus, TblHiveRequest
from sqlalchemy.orm import scoped_session
from sqlalchemy import and_
from application import session_factory
from application.common.loggerfile import my_logger
hivequery = Blueprint('hivequery', __name__)

@hivequery.route("/hivequery/<agentid>", methods=['GET'])
def hiveQuery(agentid):
    try:
        my_logger.info("in hive request query api called by agent with its agent id")
        hive_req_data = []
        db_session = scoped_session(session_factory)
        agent_queries_reqids=db_session.query(TblHiveRequest.txt_query_string,
                                              TblHiveRequest.uid_hive_request_id,
                                              TblHiveRequest.txt_hive_database).filter(and_(TblHiveRequest.uid_agent_id==agentid,
                                                                                            TblHiveRequest.bool_query_complete=='f')).all()
        my_logger.info(agent_queries_reqids)
        if agent_queries_reqids :
            for tuplees in agent_queries_reqids:
                posted_query = str(tuplees[0]).strip()

                if posted_query.endswith(';'):
                    posted_query = posted_query[:-1]
                # splitting query for checking select statement
                splitted_string = posted_query.split()
                # query data to send
                hive_query_data = {}
                splitted_string[0] = splitted_string[0].upper()
                resultset_words = 'describe|show'
                no_resultset_words = 'create|alter|load|insert|use|drop|truncate'

                if splitted_string[0] == 'SELECT':

                    explain_query = "explain " + posted_query

                    posted_query = "insert overwrite directory '/" + str(tuplees[1]) + "' " + posted_query

                    encoded_explain = explain_query.encode('base64', 'strict')
                    # url
                    hive_query_data['output_type'] = "url"
                    hive_query_data['explain'] = encoded_explain


                elif re.search(resultset_words, posted_query, re.IGNORECASE):
                    hive_query_data['output_type'] = 'tuples'
                elif re.search(no_resultset_words, posted_query, re.IGNORECASE):
                    hive_query_data['output_type'] = 'noresult'
                else:
                    hive_query_data['output_type'] = 'null'

                encoded_string = posted_query.encode('base64', 'strict')

                hive_query_data['query_string'] = encoded_string

                hive_query_data['hive_request_id'] = str(tuplees[1])
                hive_query_data['database'] = str(tuplees[2])
                my_logger.info(hive_query_data)
                hive_req_data.append(hive_query_data)

                hive_meta_status_values = db_session.query(TblHiveMetaStatus.var_status, TblHiveMetaStatus.srl_id).all()
                hive_meta_status_values_dict = dict(hive_meta_status_values)
                hive_query_status = db_session.query(TblHiveRequest).filter(TblHiveRequest.uid_hive_request_id==str(tuplees[1]))
                hive_query_status.update({"int_query_status" : hive_meta_status_values_dict['INITIALIZED'],
                                          "ts_status_time" : datetime.datetime.now(),
                                          "bool_query_complete" : 1
                                          })


                db_session.commit()
                my_logger.info("committing to database and closing session done")


            return jsonify(hive_req_data)
        else:
            return jsonify(404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

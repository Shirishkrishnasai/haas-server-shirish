import yaml
import re
import psycopg2,sys,os,json
import io
from azure.storage.file import FileService, FilePermissions
from application.models.models import TblMetaFileUpload, TblFileUpload, TblMetaHdfsUpload, TblClusterType
from configparser import ConfigParser
from msrestazure.azure_exceptions import CloudError
import pymongo
import uuid
import datetime
# from datetime import datetime
import time
from flask import Flask, jsonify, request, Request, Blueprint
from application import app,  conn_string, mongo_conn_string, session_factory
from application.common.loggerfile import my_logger
from application.config.config_file import schema_statement, request_status, kafka_bootstrap_server
from application.models.models import TblCustomerRequest, TblAgentConfig, TblAgent, TblNodeInformation, \
    TblMetaCloudLocation, TblHiveMetaStatus, TblHiveRequest, TblFeature, TblPlan, TblSize, TblMetaRequestStatus, \
    TblCluster, TblVmCreation,TblMetaTaskStatus,TblTask
from sqlalchemy.orm import scoped_session
from application import session_factory
from kafka import KafkaProducer
from kafka import KafkaConsumer

api = Blueprint('api', __name__)


@api.route("/api/agent/tasks", methods=['POST'])
def monitor():
    try:

        data = request.json
        status = data['status']
        posted_status_value = str(status)
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("set search_path to highgear")
        metatable_status_values = "select var_task_status,srl_id from tbl_meta_task_status"
        cur.execute(metatable_status_values)

        metatable_rows_list = cur.fetchall()
        table_status_values = dict(metatable_rows_list)

        my_logger.debug(table_status_values)

        insert_status_value = table_status_values[posted_status_value]
        my_logger.debug(insert_status_value)

        date = datetime.datetime.now()
        task_id = data['task_id']

        insert_task_status_log = "insert into tbl_task_status_log(uuid_task_id,int_tbl_meta_task_status,time_updated) values ('%s','%s','%s')"
        cur.execute(insert_task_status_log % (task_id, insert_status_value, date))

        task_status_update_statement = "update tbl_tasks set var_task_status='%s' where uid_task_id='%s'"
        cur.execute(task_status_update_statement % (status, task_id))

        conn.commit()
        request_id_for_taskid = "select uid_request_id from tbl_tasks where uid_task_id='%s'"
        cur.execute(request_id_for_taskid % task_id)
        request_id = cur.fetchone()
        tasks_status_statement = "select uid_task_id,var_task_status from tbl_tasks where uid_request_id='%s'"
        cur.execute(tasks_status_statement % request_id)
        tasks_status_tuples = cur.fetchall()

        tasks_id = []
        tasks_status = []
        for each_tuple in tasks_status_tuples:
            tasks_id.append(each_tuple[0])
            task_id_status = each_tuple[1]
            if each_tuple[1] == "completed":
                tasks_status.append(each_tuple[1])
        if len(tasks_id) == len(tasks_status):
            customer_request_update_statement = "update tbl_customer_request set var_request_status='completed' where uid_request_id='%s'"
            cur.execute(customer_request_update_statement)
            conn.commit()
        else:
            customer_request_update_statement = "update tbl_customer_request set var_request_status='pending' where uid_request_id='%s'"
            cur.execute(customer_request_update_statement % request_id)
            conn.commit()

        return jsonify(message="successful")


    except Exception as e:
        return e.message


    except psycopg2.DatabaseError, e:
        my_logger.debug(e.pgerror)
        return jsonify(message='database error')
    except psycopg2.OperationalError, e:
        my_logger.debug(e.pgerror)
        return jsonify(message='Operational error')
    except Exception:
        return jsonify(error='value error', message='not in json format')


@api.route("/api/addcluster", methods=['POST'])
def hg_client():
    try:
        print 'hello client'
        # try:
        customer_request = request.json
        print customer_request
        feature_request = customer_request['features']
        db_session = scoped_session(session_factory)
        requests = []
        cluster_id = None
        for customer_data in feature_request:
            feature_request_id = {}
            request_id = str(uuid.uuid1())
            feature_id = customer_data['feature_id']
            print feature_id, 'featureiddd'

            # creating request id against feature id
            feature_request_id[feature_id] = request_id
            print feature_request_id, 'featt_req_id'
            requests.append(feature_request_id)

        print requests
        for customer_data in feature_request:
            feature_id = customer_data['feature_id']
            print feature_id
            if customer_data.has_key('payload'):
                print "in azure"

                payload = customer_data['payload']
                if payload.has_key('cluster_id'):
                    cluster_id = payload['cluster_id']
                    insert = TblCluster(uid_cluster_id=cluster_id)
                    db_session.add(insert)
                    db_session.commit()
                print cluster_id, "kjbdvdhjbdhfgduidfh"
                print payload
                mongo_connection = pymongo.MongoClient(mongo_conn_string)
                database_connection = mongo_connection["haas"]
                collection_connection = database_connection["highgear"]
                insertstatement = collection_connection.insert_one(payload)
                cluster_info_querystatment = collection_connection.find_one(payload)
                cluster_info_payloadid = str(cluster_info_querystatment["_id"])
                feature_dependency = db_session.query(TblFeature.txt_dependency_feature_id).filter(
                    TblFeature.char_feature_id == feature_id).first()
                dependents = feature_dependency[0]
                print dependents, 'dependents'
                request_id_list = [d.get(str(feature_id)) for d in requests]
                print request_id_list, 'listi'
                dependency_request_id_list = [d.get(str(dependents)) for d in requests]
                request_id = [x for x in request_id_list if x != None]
                print 'rrrrrrrrrrrrrrrrrr', request_id
                dependency_request_id = [x for x in dependency_request_id_list if x != None]
                print dependency_request_id, 'dddddddddd'

                if dependents == None:
                    print 'in dependents payload'
                    insert_customer = TblCustomerRequest(txt_payload_id=cluster_info_payloadid,
                                                         uid_request_id=request_id[0],
                                                         uid_customer_id=customer_request['customer_id'],
                                                         char_feature_id=feature_id,
                                                         uid_cluster_id=cluster_id)
                    db_session.add(insert_customer)
                    db_session.commit()
                    print 'finish'

                else:
                    print 'hi i am in dependents else'
                    insert_customer = TblCustomerRequest(txt_payload_id=cluster_info_payloadid,
                                                         uid_request_id=request_id[0],
                                                         uid_customer_id=customer_request['customer_id'],
                                                         txt_dependency_request_id=dependency_request_id[0],
                                                         char_feature_id=feature_id,
                                                         uid_cluster_id=cluster_id)
                    db_session.add(insert_customer)
                    db_session.commit()

            else:
                feature_dependency = db_session.query(TblFeature.txt_dependency_feature_id).filter(
                    TblFeature.char_feature_id == feature_id).first()
                dependents = feature_dependency[0]
                print dependents, 'without payload dependents'
                request_id_list = [d.get(str(feature_id)) for d in requests]
                dependency_request_id_list = [d.get(str(dependents)) for d in requests]
                request_id = [x for x in request_id_list if x != None]
                print 'rrrrrrr', request_id
                dependency_request_id = [x for x in dependency_request_id_list if x != None]
                if dependents == None:
                    print "in else"
                    insert_customer = TblCustomerRequest(uid_request_id=request_id[0],
                                                         uid_customer_id=customer_request['customer_id'],
                                                         char_feature_id=feature_id,
                                                         uid_cluster_id=cluster_id)
                    db_session.add(insert_customer)
                    db_session.commit()

                else:
                    print "in non payload else"
                    print feature_id, 'fffffffffff'
                    print requests
                    print [d.get(str(feature_id)) for d in requests]
                    insert_customer = TblCustomerRequest(uid_request_id=request_id[0],
                                                         uid_customer_id=customer_request['customer_id'],
                                                         txt_dependency_request_id=dependency_request_id[0],
                                                         char_feature_id=feature_id,
                                                         uid_cluster_id=cluster_id)
                    db_session.add(insert_customer)
                    db_session.commit()


                    # except Exception as e:
                    #	return e.message
                    # finally:
                    #   db_session.close()
        return jsonify(request_id=request_id[0], message='success')
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@api.route('/api/agent/register', methods=['POST'])
def register():
    try:
        my_logger.debug('in server register api')
        agent_data = request.json
        my_logger.debug(agent_data)
        agent_id = agent_data['agent_id']
        customer_id = agent_data['customer_id']
        cluster_id = agent_data['cluster_id']
        agent_version = agent_data['agent_version']
        registered_time = datetime.datetime.now()
        db_session = scoped_session(session_factory)
        required_data = db_session.query(TblAgent.bool_registered).filter(TblAgent.uid_agent_id == agent_id,
                                                                          TblAgent.uid_customer_id == customer_id,
                                                                          TblAgent.uid_cluster_id == cluster_id,
                                                                          TblAgent.str_agent_version == agent_version).first()

        if required_data[0] == False:
            update_statement = db_session.query(TblAgent.bool_registered, TblAgent.ts_registered_datetime).filter(
                TblAgent.uid_agent_id == agent_id,
                TblAgent.uid_cluster_id == cluster_id)
            update_statement.update({"bool_registered": 1, "ts_registered_datetime": registered_time})
            db_session.commit()
            my_logger.debug("committing to database done")

            agent_config_data = db_session.query(TblAgentConfig.config_entity_name,
                                                 TblAgentConfig.config_entity_value).all()
            db_session.close()

            agent_config_data_json = dict(
                (column_name, column_value) for column_name, column_value in agent_config_data)
            return jsonify(agent_config_data_json)

        else:
            my_logger.debug('i am in else')
            return jsonify(message="either registration is done previously or agent_data is not correct")

    except psycopg2.DatabaseError, e:
        my_logger.error(e.pgerror)
        return jsonify(message='database error')

    except Exception as e:
        my_logger.error(e)
        return jsonify(message='wrong data format')
    finally:
        db_session.close()


@api.route('/api/hivequery', methods=['POST'])
def hg_hive_client():
    #try:
        # posted data
        data = request.json
        my_logger.info(data)
        customerid = data['customer_id']
        clusterid = data['cluster_id']
        username = data['user_name']
        database = data['database']
        agentid = data['agent_id']
        # # trimming query
        posted_query = data['query_string'].strip()
        # splitting query for checking select statement
        splitted_string = posted_query.split()
        # generating hive request id
        hive_request_id_value = str(uuid.uuid1())
        splitted_string[0] = splitted_string[0].upper()

        select_query_bool_value = 0
        if splitted_string[0] == 'SELECT':
            select_query_bool_value = 1

        db_session = scoped_session(session_factory)

        hive_request_status_values = TblHiveRequest(uid_hive_request_id=hive_request_id_value,
                                                    uid_customer_id=customerid,
                                                    uid_cluster_id=clusterid,
                                                    uid_agent_id=agentid,
                                                    var_user_name=username,
                                                    ts_requested_time=datetime.datetime.now(),
                                                    txt_query_string=posted_query,
                                                    ts_status_time=datetime.datetime.now(),
                                                    bool_url_created=0,
                                                    bool_select_query = select_query_bool_value,
                                                    txt_hive_database = database,
                                                    bool_query_complete = 0)
        db_session.add(hive_request_status_values)
        db_session.commit()
        db_session.close()
        my_logger.info("committing to database and closing session done")
        return jsonify(hive_request_id=hive_request_id_value, select_query=select_query_bool_value, role = 'hive')

    #except Exception as e:
     #   exc_type, exc_obj, exc_tb = sys.exc_info()
      #  fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
       # my_logger.error(exc_type)
        #my_logger.error(fname)
       # my_logger.error(exc_tb.tb_lineno)
    #finally:
     #   db_session.close()


@api.route('/api/hivedatabase/<customer_id>/<cluster_id>/<agent_id>', methods=['GET'])
def hiveDatabaseQuery(customer_id, cluster_id, agent_id):

    db_session = scoped_session(session_factory)
    hive_request_id = uuid.uuid1()
    print hive_request_id,'hive requestssss'
    query_string = "show databases"
    hive_request_database_values = TblHiveRequest(uid_hive_request_id=str(hive_request_id),
                                                uid_customer_id=customer_id,
                                                uid_cluster_id=cluster_id,
                                                uid_agent_id=agent_id,
                                                ts_requested_time=datetime.datetime.now(),
                                                txt_query_string=query_string,
                                                ts_status_time=datetime.datetime.now(),
                                                bool_url_created=0,
                                                bool_select_query=0,
                                                txt_hive_database='default',
                                                bool_query_complete=0)
    db_session.add(hive_request_database_values)
    db_session.commit()
    db_session.close()
    my_logger.info("committing to database and closing session done")

    #time.sleep(120)
    t_end = time.time() + 120
    while time.time() < t_end:

        hive_databases_result = db_session.query(TblHiveRequest.hive_query_output). \
            filter(TblHiveRequest.uid_hive_request_id == str(hive_request_id)).all()
        if hive_databases_result[0][0] is not None:
            print hive_databases_result, type(hive_databases_result), 'hiveeeeeeeeeee'

            databases = eval(hive_databases_result[0][0])
            print databases, type(databases), 'databases'
            databases_output = databases[str('output')]

            return jsonify(databases=databases_output)
	else:
	    return jsonify(databases=[])

@api.route('/api/hiveselectqueryresult/<request_id>', methods=['GET'])
def hiveSelectQueryResult(request_id):
    try:
        print "haaaaaiiiiieieeeeee"
        db_session = scoped_session(session_factory)

        hive_select_query_statement = db_session.query(TblHiveRequest.txt_url_value).filter(
            TblHiveRequest.uid_hive_request_id == request_id, TblHiveRequest.bool_url_created == True).first()
        print hive_select_query_statement

        return jsonify(hive_select_query_statement)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@api.route('/api/hivestatus/<request>', methods=['GET'])
def hivestatus(request):
    #try:
        db_session = scoped_session(session_factory)
        result = db_session.query(TblHiveRequest.hive_query_output).filter(
            TblHiveRequest.uid_hive_request_id == request).first()
        #print result, type(result)
        if result[0] == None:
            db_session.close()

            return jsonify(message="query under execution..please wait")
        else:
            result = eval(result[0])
            #print result, type(result),"11111111111111111111111"
            tup= {}
            for key, value in result.iteritems():
                dict = {}
                dict[str(key)]=str(value)

                tup.update({key:value})
                #print tup,"helloooooooooooooo"
            db_session.close()

            return jsonify(tup)

@api.route('/api/customer_plan', methods=['GET'])
def customerPlan():
    try:
        db_session = scoped_session(session_factory)

        plan_select_query_statement = db_session.query(TblPlan.int_plan_id, TblPlan.var_plan_type).all()
        print plan_select_query_statement
        result_list = []

        for tups in plan_select_query_statement:
            plan_dicts = {}
            plan_dicts['id'] = tups[0]
            plan_dicts['plan_name'] = str(tups[1])
            # print plan_dicts,'dulllllllllllll'
            result_list.append(plan_dicts)
        print     result_list
        return jsonify(cluster_plans=result_list)

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@api.route('/api/cluster_size', methods=['GET'])
def clusterSize():
    try:
        db_session = scoped_session(session_factory)

        size_select_query_statement = db_session.query(TblSize.int_size_id, TblSize.var_size_type).all()
        print size_select_query_statement
        result_list = []

        for tups in size_select_query_statement:
            # print tups,'tuppppppppppppppp'
            size_dicts = {}
            size_dicts['id'] = tups[0]
            size_dicts['size'] = str(tups[1])
            # print plan_dicts,'dulllllllllllll'
            result_list.append(size_dicts)
        print result_list
        return jsonify(cluster_size=result_list)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@api.route('/api/cluster_status/<request_id>', methods=['GET'])
def clusterStatus(request_id):
    try:
        db_session = scoped_session(session_factory)
        status_select_query_statement = db_session.query(TblCustomerRequest.int_request_status,
                                                         TblCustomerRequest.uid_cluster_id).filter(
            TblCustomerRequest.uid_request_id == request_id).all()
        # status_select_query_statement = db.session.query(TblCustomerRequest.int_request_status,TblCustomerRequest.uid_customer_id).filter(TblCustomerRequest.uid_request_id == request_id).all()
        status = None
        if len(status_select_query_statement) == 0:
            return jsonify(message="request id not available")
        else:
            cluster_id = status_select_query_statement[0][1]
            request_status = status_select_query_statement[0][0]
            print cluster_id, "hi"
            print request_status, "hello"
            request_status_select_query_statement = db_session.query(TblMetaRequestStatus.var_request_status).filter(
                TblMetaRequestStatus.srl_id == request_status).all()
            cluster_details = db_session.query(TblCluster.var_cluster_name, TblCluster.char_cluster_region).filter(
                TblCluster.uid_cluster_id == cluster_id).all()
            # cluster_details = db.session.query(TblCluster.var_cluster_name, TblCluster.char_cluster_region).filter(TblCluster.uid_customer_id == customer_id).all()
            if len(cluster_details) == 0:
                return jsonify(message="cluster_Id not avilable", request_id=request_id)
            cluster_name = cluster_details[0][0]
            cluster_region = cluster_details[0][1]
            print cluster_name
            print cluster_region
            if len(request_status_select_query_statement) == 0:
                return jsonify(request_id=request_id, cluster_status=status, cluster_name=cluster_details[0][0],
                               cluster_location=cluster_details[0][1])
            else:
                status = request_status_select_query_statement[0][0]
                return jsonify(request_id=request_id, cluster_status=status, cluster_name=cluster_details[0][0],
                               cluster_location=cluster_details[0][1])
    except Exception as e:

                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                my_logger.error(exc_type)
                my_logger.error(fname)
                my_logger.error(exc_tb.tb_lineno)
    finally:
            db_session.close()


@api.route("/api/customerlocation", methods=['GET'])
def customerLocation():
    try:
        db_session = scoped_session(session_factory)
        meta_cloud_location_query = db_session.query(TblMetaCloudLocation.srl_id, TblMetaCloudLocation.var_location,
                                                  TblMetaCloudLocation.var_cloud_type).all()
        dict_location = {}
        for cluster_location in meta_cloud_location_query:
            cloud_type = cluster_location[0]

            if cloud_type in dict_location:
                dict_location[cluster_location].append(cluster_location[1])
            else:
                dict_location[cluster_location] = (cluster_location[1])
        print dict_location, type(dict_location)
        tuplist = []
        for tups in sorted(dict_location):
            dic = {}
            dic['key'] = str(tups[0])
            dic['location'] = str(tups[1]) + '-' + str(tups[2])
            tuplist.append(dic)
        return jsonify(tuplist)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@api.route("/api/<cluster_id>/<role>", methods=['GET'])
def customer(cluster_id, role):
    #try:
        print "hello "
        print cluster_id
        print role
        db_session = scoped_session(session_factory)
        required_data = db_session.query(TblVmCreation.uid_agent_id).filter(TblVmCreation.uid_cluster_id == cluster_id,
                                                                            TblVmCreation.var_role == role).first()
        print required_data, type(required_data)
	db_session.close()

        return jsonify(agent_id=required_data[0])
    #except Exception as e:

   #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
     #   my_logger.error(exc_type)
      #  my_logger.error(fname)
       # my_logger.error(exc_tb.tb_lineno)
    #finally:
     #   db_session.close()


@api.route('/api/cluster/<customer_id>', methods=['GET'])
def cluster_info(customer_id):
    try:
        #print customer_id
        db_session = scoped_session(session_factory)
        customer_cluster_info = db_session.query(TblCluster.uid_customer_id,TblCluster.uid_cluster_id,TblCluster.uid_cluster_type_id,TblCluster.valid_cluster,TblCluster.ts_created_datetime,TblCluster.var_cluster_name)\
            .filter(TblCluster.uid_customer_id == customer_id).all()
        #print customer_cluster_info, "cciiiiiiiiiiiiiiiiiiiiiiiii"
        if customer_cluster_info == []:
            return jsonify(message="No clusters to be displayed")
        else:
            list_customer_cluster_info = []
            for cluster_info in customer_cluster_info:
                if cluster_info[3] == True:
                    mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
                    database_conn = mongo_db_conn['local']
                    customer_id_metrics_list = list(database_conn[customer_id].find())
                    #print customer_id_metrics_list,type(customer_id_metrics_list),'cusososoosos'
                    if customer_id_metrics_list == []:
                        available_storage = 'NA'

                    #print customer_id_metrics_list[-1]['payload'][3],'payyyyyyyyyyyylllllll'
                    #print customer_id_metrics_list[-1]['payload'][-2], 'paoooooooooyyyyylllllll'
                    else:
                        available_storage = customer_id_metrics_list[-1]['payload'][-2]['available_storage']
                    #print available_storage,'vallllll'
                    # metrics_dict =  customer_id_metrics_list[-1]
                    #for keys, values in metrics_dict['payload'][3].items():
                        # print keys,values , "valoooooooooooeeeeeees"
                    #    if keys == 'available_storage':
                            #print values, 'looooooooooooooooooooooooooooooooooooooooooo'
                    #        available_storage = values
                else:
                    available_storage = 0
                #clustername = db_session.query(TblClusterType.char_name).\
                #    filter(TblClusterType.uid_cluster_type_id == cluster_info[2]).all()
                #clus_name = clustername[0][0].rstrip()

                cus_node_info = db_session.query(TblNodeInformation.uid_node_id,TblNodeInformation.char_role).\
                    filter(TblNodeInformation.uid_cluster_id == cluster_info[1]).all()

                node_info_list = []

                for cus in cus_node_info:
                    node_info_list.append({"node_id": cus[0], "char_role": cus[1]})

                list_customer_cluster_info.append(
                    {"customer_id": cluster_info[0], "node_information": node_info_list, "cluster_id": cluster_info[1],
                     "cluster_type_id": cluster_info[2], "clustername": cluster_info[5], "valid_cluster": cluster_info[3],
                     "cluster_up_time":cluster_info[4],"available_storage": available_storage})

            reversed_list_customer_cluster_info = list_customer_cluster_info[::-1]

            return jsonify(clusterinformation=reversed_list_customer_cluster_info)
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@api.route("/api/status/<customer_id>/<cluster_id>", methods=['GET'])
def status(customer_id,cluster_id):
        db_session = scoped_session(session_factory)
        valid_cluster= db_session.query(TblCluster.valid_cluster).filter(TblCluster.uid_cluster_id == cluster_id,TblCluster.uid_customer_id == customer_id).first()
        print valid_cluster,"validcluster"
        if valid_cluster[0]== True :
            db_session.close()
            return jsonify(status="completed")
        else :
            return jsonify(message="not a valid cluster")
@api.route("/api/addhivenode", methods=['POST'])
def edgenode():
    try:
        customer_request = request.json
        db_session = scoped_session(session_factory)
        customer_id=customer_request['customer_id']
        cluster_id = customer_request['cluster_id']
        request_id1 = str(uuid.uuid1())
        request_id2 = str(uuid.uuid1())
        print request_id1,request_id2
        insert_customer = TblCustomerRequest(uid_request_id=request_id1,
                                                        uid_customer_id=customer_id,
                                                        char_feature_id=11,
                                                        uid_cluster_id=cluster_id)
        db_session.add(insert_customer)
        db_session.commit()
        insert_customer = TblCustomerRequest(uid_request_id=request_id2,
                                                    uid_customer_id=customer_id,
                                                     txt_dependency_request_id=request_id1,
                                                    char_feature_id=12,
                                                     uid_cluster_id=cluster_id)
        db_session.add(insert_customer)
        db_session.commit()
        return jsonify(request_id=request_id1, message='success')
    except Exception as e:

        my_logger.debug(e)
    finally:
        db_session.close()

from pytz import timezone
import sys,os
import pymongo
import uuid
import datetime
import time
from flask import jsonify, request, Blueprint
from application import  mongo_conn_string
from application.common.loggerfile import my_logger
from application.models.models import TblCustomerRequest, TblAgentConfig, TblAgent, TblNodeInformation, \
    TblMetaCloudLocation, TblHiveRequest, TblFeature, TblPlan, TblSize, TblMetaRequestStatus, \
    TblCluster, TblVmCreation,TblCustomerRequestHdfs
from sqlalchemy.orm import scoped_session
from application import session_factory
from sqlalchemy import and_

api = Blueprint('api', __name__)

@api.route("/api/addcluster", methods=['POST'])
def hg_client():
    try:
        db_session = scoped_session(session_factory)
        mongo_connection = pymongo.MongoClient(mongo_conn_string)
        customer_request = request.json
        feature_request = customer_request['features']
        clustername = customer_request['features'][0]['payload']['cluster_name']
        requests = []
        cluster_id = None
        for customer_data in feature_request:
            feature_request_id = {}
            request_id = str(uuid.uuid1())
            feature_id = customer_data['feature_id']
            # creating request id against feature id
            feature_request_id[feature_id] = request_id
            requests.append(feature_request_id)
        for customer_data in feature_request:
            feature_id = customer_data['feature_id']
            if customer_data.has_key('payload'):
                payload = customer_data['payload']
                if payload.has_key('cluster_id'):
                    cluster_id = payload['cluster_id']
                    insert = TblCluster(uid_cluster_id=cluster_id)
                    db_session.add(insert)
                    db_session.commit()
                database_connection = mongo_connection["haas"]
                collection_connection = database_connection["highgear"]
                collection_connection.insert_one(payload)
                cluster_info_querystatment = collection_connection.find_one(payload)
                cluster_info_payloadid = str(cluster_info_querystatment["_id"])
                feature_dependency = db_session.query(TblFeature.txt_dependency_feature_id).filter(
                    TblFeature.char_feature_id == feature_id).first()
                dependents = feature_dependency[0]
                request_id_list = [d.get(str(feature_id)) for d in requests]
                dependency_request_id_list = [d.get(str(dependents)) for d in requests]
                request_id = [x for x in request_id_list if x != None]
                dependency_request_id = [x for x in dependency_request_id_list if x != None]
                if dependents == None:
                    insert_customer = TblCustomerRequest(txt_payload_id=cluster_info_payloadid,
                                                         uid_request_id=request_id[0],
                                                         uid_customer_id=customer_request['customer_id'],
                                                         char_feature_id=feature_id,
                                                         uid_cluster_id=cluster_id)
                    db_session.add(insert_customer)
                    db_session.commit()
                else:
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
                request_id_list = [d.get(str(feature_id)) for d in requests]
                dependency_request_id_list = [d.get(str(dependents)) for d in requests]
                request_id = [x for x in request_id_list if x != None]
                dependency_request_id = [x for x in dependency_request_id_list if x != None]
                if dependents == None:
                    insert_customer = TblCustomerRequest(uid_request_id=request_id[0],
                                                         uid_customer_id=customer_request['customer_id'],
                                                         char_feature_id=feature_id,
                                                         uid_cluster_id=cluster_id)
                    db_session.add(insert_customer)
                    db_session.commit()

                else:
                    insert_customer = TblCustomerRequest(uid_request_id=request_id[0],
                                                         uid_customer_id=customer_request['customer_id'],
                                                         txt_dependency_request_id=dependency_request_id[0],
                                                         char_feature_id=feature_id,
                                                         uid_cluster_id=cluster_id)
                    db_session.add(insert_customer)
                    db_session.commit()
        mongo_connection.close()
        return jsonify(provision_request_id=requests[0]['9'],configure_request_id =requests[1]['10'], cluster_name =clustername,message='success')
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
        agent_data = request.json
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
        if required_data !=[] :
            if required_data[0] == False:
                update_statement = db_session.query(TblAgent.bool_registered, TblAgent.ts_registered_datetime).filter(
                    TblAgent.uid_agent_id == agent_id,
                    TblAgent.uid_cluster_id == cluster_id)
                update_statement.update({"bool_registered": 1, "ts_registered_datetime": registered_time})
                db_session.commit()
                agent_config_data = db_session.query(TblAgentConfig.config_entity_name,
                                                     TblAgentConfig.config_entity_value).all()

                agent_config_data_json = dict(
                    (column_name, column_value) for column_name, column_value in agent_config_data)
                return jsonify(agent_config_data_json)
            else:
                return jsonify(message="either registration is done previously or agent_data is not correct")
        else :
            my_logger.info("no such agent at all")
            return  jsonify(message="no such agent at all")
    except Exception as e:
       exc_type, exc_obj, exc_tb = sys.exc_info()
       fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
       my_logger.error(exc_type)
       my_logger.error(fname)
       my_logger.error(exc_tb.tb_lineno)
    finally:
       db_session.close()


@api.route('/api/hivequery', methods=['POST'])
def hg_hive_client():
    try:
        # posted data
        data = request.json
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
        return jsonify(hive_request_id=hive_request_id_value, select_query=select_query_bool_value, role = 'hive')
    except Exception as e:
       exc_type, exc_obj, exc_tb = sys.exc_info()
       fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
       my_logger.error(exc_type)
       my_logger.error(fname)
       my_logger.error(exc_tb.tb_lineno)
    finally:
       db_session.close()


@api.route('/api/hivedatabase/<customer_id>/<cluster_id>/<agent_id>', methods=['GET'])
def hiveDatabaseQuery(customer_id, cluster_id, agent_id):
    try:
        db_session = scoped_session(session_factory)
        hive_request_id = uuid.uuid1()
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
        t_end = time.time() + 120
        while time.time() < t_end:
            hive_databases_result = db_session.query(TblHiveRequest.hive_query_output). \
                filter(TblHiveRequest.uid_hive_request_id == str(hive_request_id)).all()
            if hive_databases_result[0][0] is not None:


                databases = eval(hive_databases_result[0][0])
                databases_output = databases[str('output')]
                result_databases = []
                for databases_lists in databases_output:
                    result_databases.append(databases_lists[0])
                return jsonify(databases=result_databases)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@api.route('/api/hiveselectqueryresult/<request_id>', methods=['GET'])
def hiveSelectQueryResultUrl(request_id):
    try:
        db_session = scoped_session(session_factory)
        hive_select_query_statement = db_session.query(TblHiveRequest.txt_url_value).filter(
            TblHiveRequest.uid_hive_request_id == request_id, TblHiveRequest.bool_url_created == True).first()
        if hive_select_query_statement != []:
            return jsonify(url=hive_select_query_statement[0])
        else :
            return jsonify(url="File not yet uploaded please wait ...")
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
    try:
        db_session = scoped_session(session_factory)
        result = db_session.query(TblHiveRequest.hive_query_output).filter(
            TblHiveRequest.uid_hive_request_id == request).first()
        if result[0] == None:
            return jsonify(message="query under execution....please wait")
        else:
            result = eval(result[0])
            hive_stat= {}
            for message, out_put in result.iteritems():
                dict = {}
                dict[str(message)]=str(out_put)
                hive_stat.update({message:out_put})
            return jsonify(hive_stat)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@api.route('/api/customer_plan', methods=['GET'])
def customerPlan():
    try:
        db_session = scoped_session(session_factory)
        plan_select_query_statement = db_session.query(TblPlan.int_plan_id, TblPlan.var_plan_type).all()
        result_list = []
        for plans in plan_select_query_statement:
            plan_dicts = {}
            plan_dicts['id'] = plans[0]
            plan_dicts['plan_name'] = str(plans[1])
            result_list.append(plan_dicts)
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
        result_list = []
        for size_cluster in size_select_query_statement:
            size_dicts = {}
            size_dicts['id'] = size_cluster[0]
            size_dicts['size'] = str(size_cluster[1])
            result_list.append(size_dicts)
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
        status = None
        if len(status_select_query_statement) == 0:
            return jsonify(message="request id not available")
        else:
            cluster_id = status_select_query_statement[0][1]
            request_status = status_select_query_statement[0][0]
            request_status_select_query_statement = db_session.query(TblMetaRequestStatus.var_request_status).filter(
                TblMetaRequestStatus.srl_id == request_status).all()
            cluster_details = db_session.query(TblCluster.var_cluster_name, TblCluster.char_cluster_region).filter(
                TblCluster.uid_cluster_id == cluster_id).all()
            if len(cluster_details) == 0:
                return jsonify(message="cluster_Id not avilable", request_id=request_id)
            if len(request_status_select_query_statement) == 0:
                return jsonify(request_id=request_id, cluster_status=status, cluster_name=cluster_details[0][0],
                               cluster_location=cluster_details[0][1],cluster_id = cluster_id)
            else:
                status = request_status_select_query_statement[0][0]
                return jsonify(request_id=request_id, cluster_status=status, cluster_name=cluster_details[0][0],
                               cluster_location=cluster_details[0][1],cluster_id=cluster_id)
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
        location_list = []
        for location in sorted(dict_location):
            cloud_location = {}
            cloud_location['key'] = str(location[0])
            cloud_location['location'] = str(location[1]) + '-' + str(location[2])
            location_list.append(cloud_location)
        return jsonify(location_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@api.route("/api/<cluster_id>/<role>", methods=['GET'])
def roleAgentId(cluster_id, role):
    try:
        db_session = scoped_session(session_factory)
        required_data = db_session.query(TblVmCreation.uid_agent_id).filter(TblVmCreation.uid_cluster_id == cluster_id,
                                                                            TblVmCreation.var_role == role).first()
        return jsonify(agent_id=required_data[0])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@api.route('/api/cluster/<customer_id>', methods=['GET'])
def cluster_info(customer_id):
    try:
        db_session = scoped_session(session_factory)
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['local']
        customer_cluster_info = db_session.query(TblCluster.uid_customer_id,TblCluster.uid_cluster_id,TblCluster.uid_cluster_type_id,TblCluster.valid_cluster,TblCluster.cluster_created_datetime,TblCluster.var_cluster_name)\
            .filter(TblCluster.uid_customer_id == customer_id).all()
        if customer_cluster_info == []:
            return jsonify(message="No clusters to be displayed")
        else:
            list_customer_cluster_info = []
            for cluster_info in customer_cluster_info:
                if cluster_info[3] is True:
                    valid_cluster = cluster_info[3]
                    collection = database_conn[cluster_info[0]]
                    customer_id_metrics_list = list(collection.find({"cluster_id": cluster_info[1]}))
                    if customer_id_metrics_list == []:
                        available_storage = 0

                    else:
                        storage = customer_id_metrics_list[-1]['payload'][1]
                        available_storage=0
                        for data in storage :
                            value=float(data['metric_value'])
                            available_storage=available_storage+value
                else:
                    valid_cluster = False
                    available_storage = 0

                cus_node_info = db_session.query(TblNodeInformation.uid_node_id,TblNodeInformation.char_role).\
                    filter(TblNodeInformation.uid_cluster_id == cluster_info[1]).all()

                node_info_list = []

                for cus in cus_node_info:
                    node_info_list.append({"node_id": cus[0], "char_role": cus[1]})
                et = timezone('Asia/Kolkata')
                if cluster_info[4] is None:
                    cluster_created_datetime = "00-00-0000 00:00:00"
                    up_time_string = "0d,0h:0m"
                else:
                    cluster_created_datetime = cluster_info[4]
                    now_time = datetime.datetime.now(et)
                    up_time = (now_time - cluster_info[4])
                    def strfdelta(tdelta, fmt):
                        d = {"days": tdelta.days}
                        d["hours"], rem = divmod(tdelta.seconds, 3600)
                        d["minutes"], d["seconds"] = divmod(rem, 60)
                        return fmt.format(**d)
                    up_time_string = strfdelta(up_time,"{days}d,{hours}h:{minutes}m")
                cus_hivenode_info = db_session.query(TblNodeInformation.uid_node_id,TblNodeInformation.char_role).\
                    filter(TblNodeInformation.uid_cluster_id == cluster_info[1],TblNodeInformation.char_role == 'hive').all()
                if cus_hivenode_info == []:
                    hive_node = 0
                else:
                    hive_node = 1
                cus_sparknode_info = db_session.query(TblNodeInformation.uid_node_id,TblNodeInformation.char_role).\
                    filter(TblNodeInformation.uid_cluster_id == cluster_info[1],TblNodeInformation.char_role == 'spark').all()
                if cus_sparknode_info == []:
                    spark_node = 0
                else:
                    spark_node = 1
                list_customer_cluster_info.append({"customer_id": cluster_info[0], "node_information": node_info_list, "hive_node":hive_node, "spark_node":spark_node, "cluster_id": cluster_info[1],
                     "cluster_type_id": cluster_info[2], "clustername": cluster_info[5],"valid_cluster": valid_cluster,
                     "cluster_up_time":up_time_string,"cluster_created_datetime":str(cluster_created_datetime),"available_storage": available_storage})
            reversed_list_customer_cluster_info = list_customer_cluster_info[::-1]
            mongo_db_conn.close()
            return jsonify(clusterinformation=reversed_list_customer_cluster_info)

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
       db_session.close()



@api.route('/api/hdfs', methods=['POST'])
def customerrequesthdfs():
    try:
        db_session = scoped_session(session_factory)
        hdfs_request_parameters=request.json
        customer_id=hdfs_request_parameters['customer_id']
        cluster_id=hdfs_request_parameters['cluster_id']
        user_name=hdfs_request_parameters['user_name']
        comand_string=hdfs_request_parameters['command_string']
        hdfs_parameters=hdfs_request_parameters['hdfs_parameters']
        agent_id=hdfs_request_parameters['agent_id']
        hdfs_request_id = uuid.uuid1()
        hdfs_request_values = TblCustomerRequestHdfs(uid_hdfs_request_id=str(hdfs_request_id),
                                                    uid_customer_id=customer_id,
                                                    uid_cluster_id=cluster_id,
                                                    uid_agent_id=agent_id,
                                                    var_user_name=user_name,
                                                    ts_requested_time=datetime.datetime.now(),
                                                    txt_command_string=comand_string,
                                                    txt_hdfs_parameters=hdfs_parameters,
                                                    bool_command_complete=0)
        db_session.add(hdfs_request_values)
        db_session.commit()
        t_end = time.time() + 120
        while time.time() < t_end:

            hdfs_command_result = db_session.query(TblCustomerRequestHdfs.hdfs_command_output). \
                filter(TblCustomerRequestHdfs.uid_hdfs_request_id == str(hdfs_request_id)).all()
            if hdfs_command_result[0][0] is not None:
                hdfs_output = hdfs_command_result[0][0]
                return jsonify(command_output=hdfs_output)
    except Exception as e:
       exc_type, exc_obj, exc_tb = sys.exc_info()
       fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
       my_logger.error(exc_type)
       my_logger.error(fname)
       my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()



@api.route("/api/status/<provision_request_id>/<configuration_request_id>", methods=['GET'])
def StatusForRequestId(provision_request_id,configuration_request_id):
    try:
        provision_request=provision_request_id
        configure_request=configuration_request_id
        db_session = scoped_session(session_factory)
        provision_request_query=db_session.query(TblCustomerRequest.bool_assigned,TblCustomerRequest.int_request_status).filter(TblCustomerRequest.uid_request_id == str(provision_request)).all()
        configuration_request_query=db_session.query(TblCustomerRequest.bool_assigned,TblCustomerRequest.int_request_status).filter(TblCustomerRequest.uid_request_id == str(configure_request)).all()
        provisioning_assigned=provision_request_query[0][0]
        provisioning_status=provision_request_query[0][1]
        configuration_assigned=configuration_request_query[0][0]
        configuration_status=configuration_request_query[0][1]
        if provisioning_assigned is False and configuration_assigned is False and configuration_status == None and provisioning_status == None:
            return jsonify(message="not assigned")
        elif provisioning_assigned is True and configuration_assigned is False and configuration_status == None  and provisioning_status == None:
            return jsonify(message=" provision running")
        elif provisioning_assigned is True and configuration_assigned is False and provisioning_status == 4 and configuration_status == None:
            return jsonify(message="provision completed")
        elif provisioning_assigned is True and configuration_assigned is True and configuration_status == None and provisioning_status == 4:
            return jsonify(message=" configuration in process")
        elif provisioning_assigned is True and configuration_assigned is True and configuration_status == 3 and provisioning_status == 4:
            return jsonify(message=" configuration running")
        elif provisioning_assigned is True and configuration_assigned is True and configuration_status == 4 and provisioning_status == 4:
            return jsonify(message="completed")
        else:
            return jsonify(message="failed")
    except Exception as e:
       exc_type, exc_obj, exc_tb = sys.exc_info()
       fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
       my_logger.error(exc_type)
       my_logger.error(fname)
       my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@api.route("/api/addhivenode", methods=['POST'])
def edgenodeProvisionRequest():
    try:
        customer_request = request.json
        db_session = scoped_session(session_factory)
        customer_id=customer_request['customer_id']
        cluster_id = customer_request['cluster_id']
        request_id1 = str(uuid.uuid1())
        request_id2 = str(uuid.uuid1())
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@api.route("/api/edgenode/<cluster_id>/<role>", methods=['GET'])
def edgeNodeIfExists(cluster_id,role):
    try:
        db_session = scoped_session(session_factory)
        edge_node_info = db_session.query(TblVmCreation).\
            filter(and_(TblVmCreation.uid_cluster_id==str(cluster_id),TblVmCreation.var_role == str(role),TblVmCreation.bool_edge == 'True')).all()
        if edge_node_info != []:
            return jsonify(bool_value=1)
        else:
            return jsonify(bool_value=0)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@api.route("/api/clusterstatus/<customer_id>/<cluster_id>",methods=['GET'])
def StatusWithMetrics(customer_id,cluster_id) :
    try :
        db_session = scoped_session(session_factory)
        host_names = []
        valid_cluster = db_session.query(TblCluster.valid_cluster).filter(TblCluster.uid_cluster_id == cluster_id,
                                                                          TblCluster.uid_customer_id == customer_id).first()
        if valid_cluster[0] == True:
            mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
            database_conn = mongo_db_conn['local']
            collection = database_conn[customer_id]
            date_time = datetime.datetime.now()
            from_time_params_str = str((int(round(time.mktime(date_time.timetuple()))) * 1000) - (1 * 1000 * 60))
            to_time_params_str = str(int(round(time.mktime(date_time.timetuple()))) * 1000)
            req_data = list(collection.find(
                    {"cluster_id": cluster_id, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}}))
            if req_data != []:
                metric=req_data[0]['payload']
                for clust_data in metric:
                    for node_data in clust_data :
                        if int(node_data['metric_value'])!=0 :
                            host_names.append(node_data['host_name'])
                no_dup_host_names=list(dict.fromkeys(host_names))
                vm_name=db_session.query(TblVmCreation.var_name).filter(TblVmCreation.uid_cluster_id==cluster_id,TblVmCreation.var_role=='datanode').all()
                from_table_vm_nam=[]
                for data_dase_vm_name in vm_name:
                    from_table_vm_nam.append(data_dase_vm_name[0])
                dead_nodes = [vm for vm in no_dup_host_names+ from_table_vm_nam if vm not in no_dup_host_names or vm not in from_table_vm_nam]
                clust_status=[]
                if len(dead_nodes)==0:
                    status=1
                    message="Cluster running"
                else :
                    message = str(len(dead_nodes)) + " datanode not running"
                    status = 0
                cluster_data = {}
                cluster_data['cluster_id'] = cluster_id
                cluster_data['status'] = status
                cluster_data['message'] = message
                edge_node = hiveStatusAfterConfiguration(customer_id, cluster_id, from_time_params_str, to_time_params_str)
                cluster_data['edgenode'] = edge_node
                clust_status.append(cluster_data)
                return jsonify(clust_status)
            else :
                fail=[]
                failed_data={}
                failed_data['cluster_id'] = cluster_id
                failed_data['status'] = 0
                failed_data['message'] ='Cluster configuration in progress'
                fail.append(failed_data)
                return jsonify(fail)
        else :
            config_data=[]
            configuration_staus={}
            configuration_staus['cluster_id']=cluster_id
            configuration_staus['message']='Cluster configuration in progress'
            configuration_staus['status'] = 1
            config_data.append(configuration_staus)
            return jsonify(config_data)
        mongo_db_conn.close()
    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

def hiveStatusAfterConfiguration(customer_id,cluster_id,from_time_params_str,to_time_params_str):
    try :
        db_session = scoped_session(session_factory)
        hive_node = db_session.query(TblVmCreation.var_name).filter(TblVmCreation.uid_cluster_id == cluster_id,
                                                                    TblVmCreation.var_role == 'hive').first()
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['hive_status']
        db_collection = database_conn[customer_id]
        return_edgenode_status=[]
        req_data = list(db_collection.find({"cluster_id": cluster_id, "time_stamp": {"$gte": from_time_params_str, "$lte": to_time_params_str}}))
        if req_data == []:
            return []
        else:
            payload = req_data[0]['payload']
            status = payload['status']
            if status == 'running':
                edgenode_status = {}
                edgenode_status['name'] = hive_node[0]
                edgenode_status['message'] = 'Running'
                edgenode_status['role'] = payload['role']
                edgenode_status['edgenode_status'] = 1
                return_edgenode_status.append(edgenode_status)
            else:
                edgenode_status = {}
                edgenode_status['name'] = hive_node[0]
                edgenode_status['message'] = 'Failed'
                edgenode_status['role'] = payload['role']
                edgenode_status['edgenode_status'] = 0
                return_edgenode_status.append(edgenode_status)
        mongo_db_conn.close()
        return (return_edgenode_status)
    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@api.route("/hive_stat", methods=['POST'])
def hiveStatusPostedFromAgent():
    try :
        role=request.json
        customerid = role["customer_id"]
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['hive_status']
        db_collection = database_conn[customerid]
        db_collection.insert_one(role)
        mongo_db_conn.close()
        return jsonify(message='success')

    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)

@api.route("/api/addsparknode", methods=['POST'])
def sparknodeProvisionRequest():
    try:
        customer_request = request.json
        db_session = scoped_session(session_factory)
        customer_id=customer_request['customer_id']
        cluster_id = customer_request['cluster_id']
        request_id1 = str(uuid.uuid1())
        request_id2 = str(uuid.uuid1())
        insert_customer = TblCustomerRequest(uid_request_id=request_id1,
                                                        uid_customer_id=customer_id,
                                                        char_feature_id=13,
                                                        uid_cluster_id=cluster_id)
        db_session.add(insert_customer)
        db_session.commit()
        insert_customer = TblCustomerRequest(uid_request_id=request_id2,
                                                    uid_customer_id=customer_id,
                                                     txt_dependency_request_id=request_id1,
                                                    char_feature_id=14,
                                                     uid_cluster_id=cluster_id)
        db_session.add(insert_customer)
        db_session.commit()
        return jsonify(request_id=request_id1, message='success')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

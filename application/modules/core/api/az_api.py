import datetime
import json
import random
import time
from functools import partial
from itertools import groupby
from operator import is_not

import jwt
import ldap
import psycopg2
import pymongo
from application import app, db, mongo_conn_string, conn_string, session_factory
from application.config.config_file import ldap_connection, ldap_connection_dn, ldap_connection_password
from application.models.models import TblUsers, TblNodeInformation, TblCustomer, TblAzureFileStorageCredentials
from flask import jsonify, request, Blueprint
# import ldap.modlist
from sqlalchemy.orm import scoped_session

# import ldap.modlist as modList
azapi = Blueprint('azapi', __name__)

my_logger = app.logger
"""
Getting list of customers from LDAP
"""
@azapi.route("/api/customer/<customer_id>", methods=['GET'])
def getCustomerUsers(customer_id):
    try:

        select_customer_dn = db.session.query(TblCustomer.txt_customer_dn).filter(
            TblCustomer.uid_customer_id == customer_id).all()
        customer_dn = select_customer_dn[0][0]
        my_logger.debug(customer_dn)
        ldap_conn = ldap.initialize(ldap_connection)
        ldap_conn.simple_bind_s(ldap_connection_dn, ldap_connection_password)
        searchScope = ldap.SCOPE_SUBTREE
        ldap_search_result = ldap_conn.search_s(customer_dn, ldap.SCOPE_SUBTREE)
        users_count = len(ldap_search_result) - 2
        users_list = []
        for each_user in range(users_count):
            users_dict = {}
            user_name = ldap_search_result[each_user + 2][1]['uid']
            users_dict['user_name'] = user_name[0]
            users_dict['active'] = "true"
            users_list.append(users_dict)
            my_logger.debug(users_list)
        return jsonify(users_list)
    except ldap.LDAPError as e:
        return jsonify(str(e))
    except Exception as e:
        return e.message


"""
Create Customer user in LDAP
"""

@azapi.route('/api/customer/user/ldap', methods=['POST'])
def createUserLdap():
    try:
        content = request.json
        my_logger.debug(content)
        display_name = content['first_name'] + content['second_name']
        sn = content['second_name']
        password = content['password']
        uid = content['email']
        customer_id = content['customer_id']
        cn = content['first_name'] + content['second_name']
        connect = ldap.initialize(ldap_connection)
        connect.simple_bind_s(ldap_connection_dn, ldap_connection_password)
        select_customer_dn = db.session.query(TblCustomer.txt_customer_dn).filter(
            TblCustomer.uid_customer_id == customer_id).all()
        customer_dn = select_customer_dn[0][0]
        my_logger.debug(customer_dn)
        customer_gid_query = db.session.query(TblCustomer.int_gid_id).filter(
            TblCustomer.uid_customer_id == customer_id).all()
        customer_gid_id = customer_gid_query[0][0]
        my_logger.debug(customer_gid_id)

        my_logger.debug(customer_dn)
        dn = "cn=" + cn + "," + customer_dn

        modlist = {
            "objectClass": ["inetOrgPerson", "posixAccount"],
            "uid": [str(uid)],
            "sn": [str(sn)],
            "displayName": [str(display_name)],
            "userPassword": [str(password)],
            "uidNumber": ["1021"],
            "gidNumber": [str(customer_gid_id)],
            "loginShell": ["/bin/bash"],
            "homeDirectory": ["/home/users/"]
        }
        # addModList transforms your dictionary into a list that is conform to ldap input.
        addinguser = connect.add_s(dn, ldap.modlist.addModlist(modlist))
        my_logger.debug(addinguser)
        if addinguser:
            data = TblUsers(uid_customer_id=customer_id,
                            var_user_name=uid,
                            txt_dn=dn,
                            bool_active=1,
                            ts_created_time=datetime.datetime.now(),
                            var_created_by='system')
            db.session.add(data)
            db.session.commit()

            select_user_dn = db.session.query(TblUsers).filter(TblUsers.var_user_name == uid).order_by(
                TblUsers.srl_id.desc()).all()

            get_data = [rows.to_json() for rows in select_user_dn]
            my_logger.debug(get_data)
            return jsonify(message="user is added", userdata=get_data)
        else:
            return jsonify(message="user is not added")



    except ldap.INVALID_CREDENTIALS:
        return jsonify(message="Your username or password is incorrect.")
    except ldap.LDAPError as e:
        my_logger.debug(e)
        return jsonify(message=e)
        connect.unbind_s()
    except psycopg2.DatabaseError, e:
        my_logger.debug(e.pgerror)
        return jsonify(message='database error')
    except psycopg2.OperationalError, e:
        my_logger.debug(e.pgerror)
        return jsonify(message='Operational error')
    except Exception:
        return jsonify(message='not in json format')


"""
Authenticating user
"""


@azapi.route('/api/customer/user/auth', methods=['POST'])
def userAuthenticate():
    try:
        content = request.json
        my_logger.debug(content)
        mail = content['email']
        password = content['password']
        select_user_dn = db.session.query(TblUsers.uid_customer_id).filter(TblUsers.var_user_name == mail).all()
        customer_id = select_user_dn[0][0]
        my_logger.debug(customer_id)

        payload = {'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
                   'uid': mail,
                   'customerid': customer_id}
        algorithm = 'HS256'
        secret_key = "qwartile"
        connect = ldap.initialize(ldap_connection)
        select_user_dn = db.session.query(TblUsers.txt_dn).filter(TblUsers.var_user_name == mail).all()
        dn = select_user_dn[0][0]
        my_logger.debug(dn)
        connect.bind_s(dn, password)
        token = jwt.encode(payload, secret_key, algorithm)
        data = {}
        data['user_name'] = dn
        data['token'] = token
        data['customer_id'] = customer_id
        return jsonify(data=data)

    except ldap.INVALID_CREDENTIALS:
        return jsonify(message="Your username or password is incorrect.")
    except ldap.LDAPError as e:
        my_logger.debug(e)
        return jsonify(message=e)
        connect.unbind_s()
    except psycopg2.DatabaseError, e:
        my_logger.debug(e.pgerror)
        return jsonify(message='database error')
    except psycopg2.OperationalError, e:
        my_logger.debug(e.pgerror)
        return jsonify(message='Operational error')
    except Exception:
        return jsonify(message='general errors')


"""
Deleting user
"""


@azapi.route('/api/customer/user/del', methods=['POST'])
def removeUser():
    try:
        content = request.json
        uid = content['user_name']
        select_user_dn = db.session.query(TblUsers.txt_dn).filter(TblUsers.var_user_name == uid).all()
        # get_data = [rows.to_json() for rows in select_user_dn]
        dn = select_user_dn[0][0]
        my_logger.debug(dn)
        connect = ldap.initialize(ldap_connection)
        connect.simple_bind_s(ldap_connection_dn, ldap_connection_password)
        del_user = connect.delete_s(dn)
        my_logger.debug(del_user)
        if del_user:
            object = db.session.query(TblUsers).filter(TblUsers.var_user_name == uid)
            object.update({"bool_active": 0})
            db.session.commit()
            return jsonify(message="user deleted")
        else:
            return jsonify(message="user deletion is un successful")

    except ldap.INVALID_CREDENTIALS:
        return "Your username or password is incorrect."
    except ldap.LDAPError as e:
        my_logger.debug(e)
        return jsonify(message=e)
        connect.unbind_s()
    except psycopg2.DatabaseError, e:
        my_logger.debug(e.pgerror)
        return jsonify(message='database error')
    except psycopg2.OperationalError, e:
        my_logger.debug(e.pgerror)
        return jsonify(message='Operational error')
    except Exception:
        return jsonify(message='not in json format')


"""
Get cluster Metrics
"""
@azapi.route('/api/customer/<cusid>/<cluid>', methods=['GET'])
def cluster(cusid, cluid):
    try:
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['local']
        collection = database_conn[cusid]
        from_time_params = request.args.get('from')
        from_time_params_str = str(from_time_params)
        to_time_params = request.args.get('to')
        to_time_params_str = str(to_time_params)
        metric = request.args.get('metric')
        req_data = collection.find(
            {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
        payload_list = []
        for data in req_data:
            payload_list.append(data['payload'])
        my_logger.debug(payload_list)
        ram_data = {}
        cpu_data = {}
        storage_data = {}
        disk_data = {}
        network_data = {}
        ram = []
        cpu = []
        network_in = []
        network_out = []
        disk_read = []
        disk_write = []
        storage = []
        for payload in payload_list:
            for metrics in payload:

                if metrics['metric_name'] == 'ram':
                    ram.append(metrics['metric_value'])
                    ram_data['measured_in'] = metrics['measured_in']
                    my_logger.debug(ram)

                elif metrics['metric_name'] == 'cpu':
                    cpu.append(metrics['metric_value'])
                    cpu_data['measured_in'] = metrics['measured_in']
                    my_logger.debug(cpu)

                elif metrics['metric_name'] == 'network':
                    network_in.append(metrics['data_in'])
                    network_out.append(metrics['data_out'])
                    network_data['measured_in'] = metrics['measured_in']
                    my_logger.debug(network_in, network_out)
                elif metrics['metric_name'] == 'storage':
                    storage.append(metrics['available_storage'])
                    storage_data['measured_in'] = metrics['measured_in']
                    my_logger.debug(storage)

                else:
                    disk_read.append(metrics['disk_read'])
                    disk_write.append(metrics['disk_write'])
                    disk_data['measured_in'] = metrics['measured_in']
                    my_logger.debug(disk_read, disk_write)
        ram_data['ram_value'] = sum(ram)
        network_data['network_data_in'] = sum(network_in)
        storage_data['storage_value'] = sum(storage)
        cpu_data['cpu_value'] = sum(cpu)
        network_data['network_data_out'] = sum(network_out)
        disk_data['disk_write'] = sum(disk_write)
        disk_data['disk_read'] = sum(disk_read)
        result = []
        if metric == 'ram':
            result.append(ram_data)
            return jsonify(data=result)
        elif metric == 'storage':
            result.append(storage_data)
            return jsonify(data=result)
        elif metric == 'cpu':
            result.append(cpu_data)
            return jsonify(data=result)
        elif metric == 'network':
            result.append(network_data)
            return jsonify(data=result)
        elif metric == 'disk':
            result.append(disk_data)
            return jsonify(data=result)
        else:

            result.extend((ram_data, network_data, storage_data, cpu_data, network_data, disk_data,))
            return jsonify(data=result)
    except Exception:
        return jsonify(message='general errors')


"""
Get Metrics by node in cluster
"""
@azapi.route('/api/customer/metrics/<cusid>/<cluid>', methods=['GET'])
def cluster_metrics(cusid, cluid):
    mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
    database_conn = mongo_db_conn['local']
    collection = database_conn[cusid]
    from_time_params = request.args.get('from')
    to_time_params = request.args.get('to')
    metric = request.args.get('metric')
    if from_time_params and to_time_params:
        print 'hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii from cluster metrics api'
        from_time_params_str = str(from_time_params)
        to_time_params_str = str(to_time_params)
        req_data = collection.find(
            {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
        # print to_time_params_str,from_time_params_str
        minutes = divideMilliSeconds(from_time_params_str, to_time_params_str)
    else:
        date_time = datetime.datetime.now()
        from_time_params = (int(round(time.mktime(date_time.timetuple()))) * 1000) - (5 * 1000 * 60)
        from_time_params_str = str(from_time_params)
        to_time_params_str = str(int(round(time.mktime(date_time.timetuple()))) * 1000)
        req_data = collection.find(
            {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
        # print to_time_params_str, from_time_params_str
        minutes = divideMilliSeconds(from_time_params_str, to_time_params_str)

    metrics_data = list(req_data)
    # print minutes
    agentlist_info = []

    for data in metrics_data:
        # print data.get('time'), data.get("_id")
        agentlist_info.append(data.get("agent_id"))

    set_agentlist = set(agentlist_info)
    agentlist = list(set_agentlist)
    # print agentlist

    # req_data=[]
    re = list(metrics_data)
    re = [change(v, minutes) for v in re]
    # print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    # for data in re:
    #    print data.get("time"), data.get("_id")

    """
    reduceByMetricForCluster for Cluster level metrics
    reduceByMetric for node level metrics
    """

    cpu = filter(partial(is_not, None), [reduceByMetricForCluster(v, 'cpu') for v in re])
    ram = filter(partial(is_not, None), [reduceByMetricForCluster(v, 'ram') for v in re])
    disk = filter(partial(is_not, None), [reduceByMetricForCluster(v, 'disk') for v in re])
    network = filter(partial(is_not, None), [reduceByMetricForCluster(v, 'network') for v in re])
    storage = filter(partial(is_not, None), [reduceByMetricForCluster(v, 'storage') for v in re])
    cpuMetrics = [reduce(cpu_reduce, group) for _, group in groupby(cpu, lambda v: v.get('time'))]
    ramMetrics = [reduce(ram_reduce, group) for _, group in groupby(ram, lambda v: v.get('time'))]
    diskMetrics = [reduce(disk_reduce, group) for _, group in groupby(disk, lambda v: v.get('time'))]
    networkMetrics = [reduce(network_reduce, group) for _, group in groupby(network, lambda v: v.get('time'))]
    storageMetrics = [reduce(storage_reduce, group) for _, group in groupby(storage, lambda v: v.get('time'))]
    my_logger.debug(cpuMetrics)
    my_logger.debug(storageMetrics)
    my_logger.debug(networkMetrics)
    my_logger.debug(diskMetrics)
    my_logger.debug(ramMetrics)

    if metric == 'cpu':
        return jsonify(cpuMetrics)
    elif metric == 'ram':
        return jsonify(ramMetrics)
    elif metric == 'storage':
        return jsonify(storageMetrics)
    elif metric == 'network':
        return jsonify(networkMetrics)
    elif metric == 'disk':
        return jsonify(diskMetrics)
    else:
        metrics = cpuMetrics + ramMetrics + storageMetrics + networkMetrics + diskMetrics
        return jsonify(metrics)


def cpu_reduce(cpu1, cpu2):
    cpu3 = {}
    # print cpu1,cpu2
    cpu3["time"] = cpu1.get("time")
    cpu3['metric_value'] = float(cpu1["metric_value"]) + float(cpu2["metric_value"])
    cpu3['metric_name'] = cpu1.get("metric_name")
    cpu3['measured_in'] = cpu1.get("measured_in")

    return cpu3


def network_reduce(n1, n2):
    n3 = {}

    n3["time"] = n1.get("time")
    n3['data_in'] = float(n1["data_in"]) + float(n2["data_in"])
    n3['data_out'] = float(n1["data_out"]) + float(n2["data_out"])
    n3['metric_name'] = n1.get("metric_name")
    n3['measured_in'] = n1.get("measured_in")

    return n3


def ram_reduce(ram1, ram2):
    ram3 = {}
    ram3["time"] = ram1.get("time")
    ram3['metric_value'] = float(ram1["metric_value"]) + float(ram2["metric_value"])
    ram3['metric_name'] = ram1.get("metric_name")
    ram3['measured_in'] = ram1.get("measured_in")

    return ram3


def storage_reduce(s1, s2):
    s3 = {}
    s3["time"] = s1.get("time")
    s3['available_storage'] = float(s1["available_storage"]) + float(s2["available_storage"])
    s3['metric_name'] = s1.get("metric_name")
    s3['measured_in'] = s1.get("measured_in")
    print s3

    return s3


def disk_reduce(d1, d2):
    d3 = {}
    d3["time"] = d1.get("time")
    d3['disk_read'] = float(d1["disk_read"]) + float(d2["disk_read"])
    d3['disk_write'] = float(d1["disk_write"]) + float(d2["disk_write"])
    d3['metric_name'] = d1.get("metric_name")
    d3['measured_in'] = d1.get("measured_in")

    return d3


def reduceByMetric(value, metricName, agent_id):
    metric_dict = {}
    payload = value.get("payload")
    # print payload

    for index, data in enumerate(payload):
        if (str(data.get("metric_name")) == metricName and str(value.get("agent_id")) == agent_id):
            metric_dict['time'] = value.get("time")
            metric_dict['agent_id'] = value.get("agent_id")

            metric_dict['metric_value'] = data.get('metric_value')
            metric_dict['measured_in'] = data.get('measured_in')
            metric_dict.update(data)
            return metric_dict


def reduceByMetricForCluster(value, metricName):
    metric_dict = {}
    payload = value.get("payload");
    # print payload
    for index, data in enumerate(payload):
        # print data,index
        # print str(data.get("mertic_name")),metricName
        if (str(data.get("metric_name")) == metricName):
            metric_dict['time'] = value.get("time")
            metric_dict['agent_id'] = value.get("agent_id")

            metric_dict['metric_value'] = data.get('metric_value')
            metric_dict.update(data)
            return metric_dict


def change(value, minutes):
    # print value
    v = {}

    for timemetric in minutes:
        # print "For time",int(value.get('time'))
        if timemetric[0] < int(value.get('time')) <= timemetric[1]:
            v['time'] = timemetric[0]
        else:
            pass

    value.update(v)
    return value


def divideMilliSeconds(fromtime, totime):
    fromtime = int(fromtime)
    totime = int(totime)
    # print fromtime,type(fromtime),totime
    totime = int(totime)

    minutes = []
    # type(fromtime)
    from_time = (fromtime / 1000 / 60)
    to_time = (totime / 1000 / 60) + 1
    # print "for times",from_time,to_time
    for i in range(from_time, to_time):
        # print "in minutes",i*60
        minutes.append([i * 1000 * 60, (i + 1) * 1000 * 60])
    return minutes


@azapi.route('/api/cluster/<customer_id>', methods=['GET'])
def cluster_info(customer_id):
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("set search_path to highgear;")

    customer_cluster_query_stmnt = "SELECT uid_customer_id,uid_cluster_id,uid_cluster_type_id,valid_cluster,var_cluster_name FROM tbl_cluster where uid_customer_id='" + str(
        customer_id) + "'"
    cur.execute(customer_cluster_query_stmnt)
    customer_cluster_info = cur.fetchall()
    print customer_cluster_info, "cciiiiiiiiiiiiiiiiiiiiiiiii"
    mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
    database_conn = mongo_db_conn['local']

    customer_id_metrics_list = list(database_conn[customer_id].find())
    print customer_id_metrics_list,type(customer_id_metrics_list),'cusososoosos'
    db_collection_list = []
    if customer_id_metrics_list == []:

        available_storage = 0
    else:
        for db_collection in customer_id_metrics_list:
            print db_collection,type(db_collection),'dbdbdbdbbdbdbdbd'
            # print db_collection,type(db_collection),'typeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeedbbbb'
            db_collection_list.append(db_collection)

        dicto = db_collection_list[-1]
        print dicto,'loooooooooooooool'
        for keys, values in dicto['payload'][3].items():
            print keys,values , "valoooooooooooeeeeeees"
            # print keys,values,'kakakakak'
            if keys == 'available_storage':
                print values, 'looooooooooooooooooooooooooooooooooooooooooo'
                available_storage = values
        print available_storage, 'avaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

    if customer_cluster_info == []:
        return jsonify(clusterinformation=[])
    else:
        # list_cus=[]
        list_customer_cluster_info = []
        for cluster_info in customer_cluster_info:
            if cluster_info[3] == True:

                cloud_type_query = "select char_name from tbl_cluster_type where uid_cluster_type_id='" + str(
                    cluster_info[2]) + "'"
                cur.execute(cloud_type_query)
                clustername = cur.fetchall()

                cloud_name = clustername[0][0].rstrip()
                # list_customer_cluster_info=[]
                #node_info_stmnt = "select uid_node_id,char_role,edge_node from tbl_node_information where uid_cluster_id='" + str(
                #    cluster_info[1]) + "' and edge_node = true"

                node_info_stmnt = "select uid_node_id,char_role from tbl_node_information where uid_cluster_id='" + str(
                    cluster_info[1])+"'"
                cur.execute(node_info_stmnt)
                cus_node_info = cur.fetchall()

                list_cus = []

                for cus in cus_node_info:
                    list_cus.append({"node_id": cus[0], "char_role": cus[1]})

                list_customer_cluster_info.append(
                    {"customer_id": cluster_info[0], "node_information": list_cus, "cluster_id": cluster_info[1],
                     "cluster_type_id": cluster_info[2], "clustername": cluster_info[4], "valid_cluster": cluster_info[3],
                     "available_storage": available_storage,"cloud_tytpe":cloud_name})

        reversed_list_customer_cluster_info = list_customer_cluster_info[::-1]

        return jsonify(clusterinformation=reversed_list_customer_cluster_info)


@azapi.route("/api/cluster_members/<customer_id>/<cluster_id>", methods=['GET'])
def clustermembers(customer_id, cluster_id):
    # customer_request=request.json
    try:
        customer_id = customer_id
        cluster_id = cluster_id
        # Query cluster members from tbl_node_information

        cluster_info_query_statement = db.session.query(TblNodeInformation). \
            filter(TblNodeInformation.uid_customer_id == customer_id,
                   TblNodeInformation.uid_cluster_id == cluster_id).all()

        list_cluster_info = [i.to_json() for i in cluster_info_query_statement]

        cluster_roles = []
        if list_cluster_info == []:
            return jsonify(cluster_members=cluster_roles)
        else:
            for dict_cluster_info in list_cluster_info:
                json_cluster_info = json.loads(dict_cluster_info)
                cluster_roles.append(
                    {"role": json_cluster_info['char_role'], "node_id": json_cluster_info['uid_node_id']})
            return jsonify(cluster_members=cluster_roles)
    except Exception as e:
        return e.message


@azapi.route("/api/azure_credentials/<customer_id>", methods=['GET'])
def azureFileStorageCredentials(customer_id):
	# customer_request=request.json
	try:
		db_session = scoped_session(session_factory)
		azure_file_storage_credentials_statement = db.session.query(TblAzureFileStorageCredentials).all()
		print azure_file_storage_credentials_statement,'azureeeee'
		values_list = []
		keys_list = []
		for val in azure_file_storage_credentials_statement:
			values_dict = dict(val)
			print values_dict,'valllllllllll'
			azure_account_name = values_dict['account_name']
			keys_list.append(values_dict['account_primary_key'])
			keys_list.append(values_dict['account_secondary_key'])
			# azure_file_storage_credentials_statement_result  = zip(*val)[0]

		return jsonify(account_name=azure_account_name, key=str(random.choice(keys_list)))
	except Exception as e:
		print e.message
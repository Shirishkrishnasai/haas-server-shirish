from functools import partial
from itertools import groupby
from operator import is_not
import datetime
import time
from azure.mgmt.monitor import MonitorManagementClient
from msrestazure.azure_active_directory import ServicePrincipalCredentials
from application.config.config_file import schema_statement, request_status, kafka_bootstrap_server, secret, client_id, \
    tenant, subscription_id
import pymongo
from application import app, mongo_conn_string, conn_string, session_factory
from application.models.models import TblUsers, TblNodeInformation, TblCustomer, TblAzureFileStorageCredentials,TblVmCreation
from flask import jsonify, request, Blueprint
from sqlalchemy.orm import scoped_session
from application.common.loggerfile import my_logger

metricapi = Blueprint('metricapi', __name__)

@metricapi.route("/api/metrics/<customer_id>/<cluster_id>/<metrics>", methods=['GET'])
def metric(customer_id,cluster_id,metrics):
    db_session= scoped_session(session_factory)
    resource_group_name = str(customer_id)
    mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
    database_conn = mongo_db_conn['local']
    db_collection = database_conn[resource_group_name]
    metrics_dat={}
    vm_names= db_session.query(TblVmCreation.var_name).filter(TblVmCreation.uid_customer_id==customer_id,TblVmCreation.uid_cluster_id==cluster_id).all()
    lis = []
    val=[]
    for names in vm_names:
        vm_names=str(names[0])
        credentials = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant)
        subscription_id
        resource_id = ("subscriptions/"+subscription_id+"/resourceGroups/"+resource_group_name
                       +"/providers/Microsoft.Compute/virtualMachines/"+vm_names)
        client = MonitorManagementClient(credentials, subscription_id)
        metrics_data = client.metrics.list(resource_id,interval="PT1M",metricnames=metrics,aggregation='Total')
        for item in metrics_data.value:
            for timeserie in item.timeseries:
                for data in timeserie.data:
                     dicto={}
                     timestam = data.time_stamp
                     time_milliseconds = (int(round(time.mktime(timestam.timetuple()))) * 1000)
                     dicto['vm_name']=vm_names
                     dicto['metric_value']=data.total
                     dicto['time']=time_milliseconds
                     lis.append(dicto)
        val.append(lis[-5:])
    metrics_dat['customer_id'] = customer_id
    metrics_dat['cluster_id'] = cluster_id
    metrics_dat['payload'] = val
    # result = db_collection.insert_one(metrics_dat)

    dic_list = []
    for lis in val:
        for n in range(0,len(lis)):
            dic = [lis[n] for lis in val]
            dic_list.append(dic)
        break
    lissto=[]
    for lis in dic_list:
        metric_value_lis = []
        for line in lis :
            metric_value = line['metric_value']
            if metric_value != None:
                metric_value_lis.append(metric_value)
                metric_sum = sum(metric_value_lis)
        dicton={}
        dicton['metric_value'] = metric_sum
        dicton['time'] = line['time']
        dicton['measured_in'] = "bytes"
        dicton['metric_name'] = metrics
        lissto.append(dicton)
    return jsonify(lissto)


@metricapi.route("/api/metrics/<customer_id>/<cluster_id>/<vm_id>/<metrics>", methods=['GET'])
def metrics_node(customer_id,cluster_id,metrics,vm_id):
    db_session= scoped_session(session_factory)
    resource_group_name = str(customer_id)
    print customer_id,cluster_id,vm_id
    vmname= db_session.query(TblVmCreation.var_name).filter(TblVmCreation.uid_cluster_id==cluster_id,TblVmCreation.uid_vm_id==vm_id).first()
    print vmname
    tups = []
    vm_names=str(vmname[0])
    credentials = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant)
    subscription_id
    resource_id = ("subscriptions/"+subscription_id+"/resourceGroups/"+resource_group_name
                       +"/providers/Microsoft.Compute/virtualMachines/"+vm_names)
    client = MonitorManagementClient(credentials, subscription_id)
    metrics_data = client.metrics.list(resource_id,interval="PT1M",metricnames=metrics,aggregation='Total')
    for item in metrics_data.value:
        for timeserie in item.timeseries:
            for data in timeserie.data:
                dicto={}
                timestam = data.time_stamp
                time_milliseconds = (int(round(time.mktime(timestam.timetuple()))) * 1000)
                dicto['vm_name']=vm_names
                dicto['data']=data.total
                dicto['time']=time_milliseconds
                dicto['measured_in'] = "bytes"
                dicto['metric_type'] = metrics
                tups.append(dicto)
    return jsonify(tups[-5:])


    """

  Get cluster Metrics
    """
@metricapi.route('/api/customer/<cusid>/<cluid>/<vm_id>', methods=['GET'])
def cluster(cusid, cluid, vm_id):
    try:
        db_session = scoped_session(session_factory)
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['local']
        collection = database_conn[cusid]
        from_time_params = request.args.get('from')
        to_time_params = request.args.get('to')
        metric = request.args.get('metric')
        vm_name = db_session.query(TblVmCreation.var_name).filter(TblVmCreation.uid_cluster_id == cluid,
                                                                  TblVmCreation.uid_vm_id == vm_id).first()
        print vm_name
        if from_time_params and to_time_params:
            print 'hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii from cluster metrics api'
            from_time_params_str = str(from_time_params)
            to_time_params_str = str(to_time_params)
            req_data = collection.find(
                {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
            print req_data
            minutes = divideMilliSeconds(from_time_params_str, to_time_params_str)
        else:
            date_time = datetime.datetime.now()
            from_time_params = (int(round(time.mktime(date_time.timetuple()))) * 1000) - (5 * 1000 * 60)
            from_time_params_str = str(from_time_params)
            print from_time_params_str
            to_time_params_str = str(int(round(time.mktime(date_time.timetuple()))) * 1000)
            print to_time_params_str
            req_data = collection.find(
                {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
            minutes = divideMilliSeconds(from_time_params_str, to_time_params_str)
            print req_data, "req_data"
        ram = []
        cpu = []
        storage = []
        for data in req_data:
            if len(data) == 0:
                return jsonify(data='null')
            else:
                for lists in data['payload']:
                    for dicts in lists:
                        dicts['time'] = data['time']
                        if dicts['metric_name'] == 'ram' and dicts['host_name'] == vm_name[0]:
                            dicts['vm_id'] = vm_id
                            ram.append(dicts)
                        elif dicts['metric_name'] == 'storage' and dicts['host_name'].strip() == vm_name[0]:
                            dicts['vm_id'] = vm_id
                            storage.append(dicts)
                        elif dicts['metric_name'] == 'cpu' and dicts['host_name'] == vm_name[0]:
                            dicts['vm_id'] = vm_id
                            cpu.append(dicts)
                        else:
                            pass
        if metric == 'ram':
            return jsonify(data=ram)
        elif metric == 'storage':
            return jsonify(data=storage)
        elif metric == 'cpu':
            return jsonify(data=cpu)
        else:
            metricss = ram + cpu + storage
            return jsonify(data=metricss)
    except Exception:
         return jsonify(message='general errors')
    finally:
         db_session.close

"""
Get Metrics by node in cluster
"""

@metricapi.route('/api/customer/metrics/<cusid>/<cluid>', methods=['GET'])
def cluster_metrics(cusid, cluid):
        print cusid, cluid
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
            print req_data
            # print to_time_params_str,from_time_params_str
            minutes = divideMilliSeconds(from_time_params_str, to_time_params_str)
        else:
            date_time = datetime.datetime.now()
            from_time_params = (int(round(time.mktime(date_time.timetuple()))) * 1000) - (5 * 1000 * 60)
            from_time_params_str = str(from_time_params)
            print from_time_params_str
            to_time_params_str = str(int(round(time.mktime(date_time.timetuple()))) * 1000)
            print to_time_params_str
            req_data = collection.find(
                {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
            # print to_time_params_str, from_time_params_str
            minutes = divideMilliSeconds(from_time_params_str, to_time_params_str)
            print req_data, "req_data"
        metrics_data = list(req_data)
        re = list(metrics_data)
        re = [change(v, minutes) for v in re]
        if len(re) == 0:
            return jsonify('null')
        else:
            """
            reduceByMetricForCluster for Cluster level metrics
            reduceByMetric for node level metrics
            """
            cpumetrics = []
            rammetrics = []
            storagemetrics = []
            cpu = filter(partial(is_not, None), [reduceByMetricForCluster(v, 'cpu') for v in re])
            ram = filter(partial(is_not, None), [reduceByMetricForCluster(v, 'ram') for v in re])
            storage = filter(partial(is_not, None), [reduceByMetricForCluster(v, 'storage') for v in re])
            for value in cpu:
                cpuMetrics = [reduce(cpu_reduce, group) for _, group in groupby(value, lambda v: v.get('time'))]
                cpumetrics.append(cpuMetrics[0])
            for value in ram:
                ramMetrics = [reduce(ram_reduce, group) for _, group in groupby(value, lambda v: v.get('time'))]
                rammetrics.append(ramMetrics[0])
            for value in storage:
                storageMetrics = [reduce(storage_reduce, group) for _, group in groupby(value, lambda v: v.get('time'))]
                storagemetrics.append(storageMetrics[0])
            # my_logger.info(cpumetrics)
            # my_logger.info(storagemetrics)
            # my_logger.info(rammetrics)

            if metric == 'cpu':
                return jsonify(cpumetrics)
            elif metric == 'ram':
                return jsonify(rammetrics)
            elif metric == 'storage':
                return jsonify(storagemetrics)
            else:
                metrics = cpumetrics + rammetrics + storagemetrics
                return jsonify(metrics)

def cpu_reduce(cpu1, cpu2):
        cpu3 = {}
        cpu3["time"] = cpu1.get("time")
        cpu3['metric_value'] = float(cpu1["metric_value"]) + float(cpu2["metric_value"])
        cpu3['metric_name'] = "cpu_cores"
        # cpu3['measured_in'] = cpu1.get("measured_in")
        return cpu3

    #

def ram_reduce(ram1, ram2):
        ram3 = {}
        ram3["time"] = ram1.get("time")
        ram3['metric_value'] = float(ram1["metric_value"]) + float(ram2["metric_value"])
        ram3['metric_name'] = "ram_metrics"
        ram3['measured_in'] = "Bytes"
        return ram3

def storage_reduce(s1, s2):
        s3 = {}
        s3["time"] = s1.get("time")
        s3['metric_value'] = float(s1["metric_value"]) + float(s2["metric_value"])
        s3['metric_name'] = "storage_metrics"
        s3['measured_in'] = "Bytes"
        # print s3,"s3333333333333333333333333333333"
        return s3

def reduceByMetric(value, metricName, vm_name):
        metric_dict = {}
        payload = value.get("payload")
        # print payload
        for index, data in enumerate(payload):
            if (str(data.get("metric_name")) == metricName and str(value.get("host_name")) == vm_name):
                metric_dict['time'] = value.get("time")
                metric_dict['host_name'] = value.get("host_name")
                metric_dict['metric_value'] = data.get('metric_value')
                metric_dict['measured_in'] = data.get('measured_in')
                metric_dict.update(data)
                # print metric_dict
                return metric_dict

def reduceByMetricForCluster(value, metric):
        payload = value.get("payload")
        # print payload
        for d in payload:
            if len(d) == 0:
                pass
            else:
                lis = []
                # print d,"ddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
                for val in d:
                    if val["metric_name"] == metric:
                        metric_dict = {}
                        metric_dict['time'] = value.get("time")
                        metric_dict['metric_value'] = val['metric_value']
                        lis.append(metric_dict)
                if lis != []:
                    return lis

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



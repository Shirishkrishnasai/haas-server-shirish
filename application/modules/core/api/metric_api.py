import os
from functools import partial
from itertools import groupby
from operator import is_not
import datetime
import time

import sys

from application.common.loggerfile import my_logger
from azure.mgmt.monitor import MonitorManagementClient
from msrestazure.azure_active_directory import ServicePrincipalCredentials
from application.config.config_file import  secret, client_id, tenant, subscription_id
import pymongo
from application import mongo_conn_string, session_factory
from application.models.models import TblVmCreation
from flask import jsonify, request, Blueprint
from sqlalchemy.orm import scoped_session

metricapi = Blueprint('metricapi', __name__)

@metricapi.route("/api/metrics/<customer_id>/<cluster_id>/<metric>", methods=['GET'])
def metric(customer_id,cluster_id,metric):
    try :
        db_session= scoped_session(session_factory)
        resource_group_name = str(customer_id)
        vm_names= db_session.query(TblVmCreation.var_name).filter(TblVmCreation.uid_customer_id==customer_id,TblVmCreation.uid_cluster_id==cluster_id).all()
        lis = []
        individual_metric=[]
        for names in vm_names:
            vm_names=str(names[0])
            credentials = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant)
            subscription_id
            resource_id = ("subscriptions/"+subscription_id+"/resourceGroups/"+resource_group_name
                           +"/providers/Microsoft.Compute/virtualMachines/"+vm_names)
            client = MonitorManagementClient(credentials, subscription_id)
            metrics_data = client.metrics.list(resource_id,interval="PT1M",metricnames=metric,aggregation='Total')
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
            individual_metric.append(lis[-5:])
        list_network = []
        for vm_list in individual_metric:
            for number_range in range(0,len(vm_list)):
                dic = [vm_list[number_range] for vm_list in individual_metric]
                list_network.append(dic)
            break
        network_metrics=[]
        for element in list_network:
            metric_value_lis = []
            for line in element :
                metric_value = line['metric_value']
                if metric_value != None:
                    metric_value_lis.append(metric_value)
                    metric_sum = sum(metric_value_lis)
            total_metric={}
            total_metric['metric_value'] = metric_sum
            total_metric['time'] = line['time']
            total_metric['measured_in'] = "bytes"
            total_metric['metric_name'] = metric
            network_metrics.append(total_metric)
        return jsonify(network_metrics)

    except Exception as e:
            no_metric=[]
            error_metric={}
            error_metric['metric_value'] = 0
            error_metric['time'] = 0
            error_metric['measured_in'] = "bytes"
            error_metric['metric_name'] = metric
            no_metric.append(error_metric)
            return jsonify(no_metric)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@metricapi.route("/api/metrics/<customer_id>/<cluster_id>/<vm_id>/<metrics>", methods=['GET'])
def metrics_node(customer_id,cluster_id,metrics,vm_id):
    try :
        db_session= scoped_session(session_factory)
        resource_group_name = str(customer_id)
        vmname= db_session.query(TblVmCreation.var_name).filter(TblVmCreation.uid_cluster_id==cluster_id,TblVmCreation.uid_vm_id==vm_id).first()
        network_metric = []
        vm_names=str(vmname[0])
        credentials = ServicePrincipalCredentials(client_id=client_id, secret=secret, tenant=tenant)
        subscription_id
        resource_id = ("subscriptions/"+subscription_id+"/resourceGroups/"+resource_group_name
                           +"/providers/Microsoft.Compute/virtualMachines/"+vm_names)
        client = MonitorManagementClient(credentials, subscription_id)
        metrics_data = client.metrics.list(resource_id,interval="PT1M",metricnames=metrics,aggregation='Total')
        for item in metrics_data.value:
            for timeserie in item.timeseries:
                for metric_list in timeserie.data:
                    node_metric={}
                    timestam = metric_list.time_stamp
                    time_milliseconds = (int(round(time.mktime(timestam.timetuple()))) * 1000)
                    node_metric['vm_name']=vm_names
                    node_metric['data']=metric_list.total
                    node_metric['time']=time_milliseconds
                    node_metric['measured_in'] = "bytes"
                    node_metric['metric_type'] = metrics
                    network_metric.append(node_metric)
        return jsonify(network_metric[-5:])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


    """

  Get cluster Metrics
    """
@metricapi.route('/api/customer/<cusid>/<cluid>/<vm_id>', methods=['GET'])
def clusterNodeLevel(cusid, cluid, vm_id):
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
        if from_time_params and to_time_params:
            from_time_params_str = str(from_time_params)
            to_time_params_str = str(to_time_params)
            req_data = collection.find(
                {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
            minutes = divideMilliSeconds(from_time_params_str, to_time_params_str)
        else:
            date_time = datetime.datetime.now()
            from_time_params = (int(round(time.mktime(date_time.timetuple()))) * 1000) - (5 * 1000 * 60)
            from_time_params_str = str(from_time_params)
            to_time_params_str = str(int(round(time.mktime(date_time.timetuple()))) * 1000)
            req_data = collection.find(
                {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
            minutes = divideMilliSeconds(from_time_params_str, to_time_params_str)
        ram = []
        cpu = []
        storage = []
        for data in req_data:
            if len(data) == 0:
                no_metric = []
                error_metric = {}
                error_metric['metric_value'] = 0
                error_metric['time'] = to_time_params_str
                error_metric['measured_in'] = "bytes"
                error_metric['metric_name'] = metric
                no_metric.append(error_metric)
                return jsonify(no_metric)
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
    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

"""
Get Metrics by node in cluster
"""

@metricapi.route('/api/customer/metrics/<cusid>/<cluid>', methods=['GET'])
def cluster_metrics(cusid, cluid):
    try :
        mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
        database_conn = mongo_db_conn['local']
        collection = database_conn[cusid]
        from_time_params = request.args.get('from')
        to_time_params = request.args.get('to')
        metric = request.args.get('metric')
        if from_time_params and to_time_params:
            from_time_params_str = str(from_time_params)
            to_time_params_str = str(to_time_params)
            req_data = collection.find(
                {"cluster_id": cluid, "time": {"$gte": from_time_params_str, "$lte": to_time_params_str}})
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
        re = list(metrics_data)
        re = [change(v, minutes) for v in re]
        if len(re) == 0:
            no_metric = []
            error_metric = {}
            error_metric['metric_value'] = 0
            error_metric['time'] = to_time_params_str
            error_metric['measured_in'] = "bytes"
            error_metric['metric_name'] = metric
            no_metric.append(error_metric)
            return jsonify(no_metric)
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
            if metric == 'cpu':
                return jsonify(cpumetrics)
            elif metric == 'ram':
                return jsonify(rammetrics)
            elif metric == 'storage':
                return jsonify(storagemetrics)
            else:
                metrics = cpumetrics + rammetrics + storagemetrics
                return jsonify(metrics)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        mongo_db_conn.close()


def cpu_reduce(cpu1, cpu2):
        cpu3 = {}
        cpu3["time"] = cpu1.get("time")
        cpu3['metric_value'] = float(cpu1["metric_value"]) + float(cpu2["metric_value"])
        cpu3['metric_name'] = "cpu_cores"
        return cpu3

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
        return s3

def reduceByMetric(value, metricName, vm_name):
        metric_dict = {}
        payload = value.get("payload")
        for index, data in enumerate(payload):
            if (str(data.get("metric_name")) == metricName and str(value.get("host_name")) == vm_name):
                metric_dict['time'] = value.get("time")
                metric_dict['host_name'] = value.get("host_name")
                metric_dict['metric_value'] = data.get('metric_value')
                metric_dict['measured_in'] = data.get('measured_in')
                metric_dict.update(data)
        return metric_dict

def reduceByMetricForCluster(value, metric):
        payload = value.get("payload")
        for d in payload:
            if len(d) == 0:
                pass
            else:
                lis = []
                for val in d:
                    if val["metric_name"] == metric:
                        metric_dict = {}
                        metric_dict['time'] = value.get("time")
                        metric_dict['metric_value'] = val['metric_value']
                        lis.append(metric_dict)
                if lis != []:
                    return lis

def change(value, minutes):
        v = {}

        for timemetric in minutes:
            if timemetric[0] < int(value.get('time')) <= timemetric[1]:
                v['time'] = timemetric[0]
            else:
                pass

        value.update(v)
        return value

def divideMilliSeconds(fromtime, totime):
        fromtime = int(fromtime)
        totime = int(totime)
        totime = int(totime)
        minutes = []
        from_time = (fromtime / 1000 / 60)
        to_time = (totime / 1000 / 60) + 1
        for i in range(from_time, to_time):
            minutes.append([i * 1000 * 60, (i + 1) * 1000 * 60])
        return minutes

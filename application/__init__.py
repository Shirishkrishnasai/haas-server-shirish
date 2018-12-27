
import pymongo
from flask import Flask, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


from requests.exceptions import HTTPError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['Access-Control-Allow-Origin'] = '*'
conn_string = "host='192.168.100.42' user='postgres' password='password' dbname='haas_demo2'"
postgres_conn = 'postgres://postgres:password@192.168.100.42/haas_demo2'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:password@192.168.100.42/haas_demo2'
mongo_conn_string="mongodb://192.168.100.41:27017"

db = SQLAlchemy(app)
sqlite_string= "/opt/agent/haas"

engine = create_engine("postgres://postgres:password@192.168.100.42/haas_demo2", pool_size=50)
session_factory = sessionmaker(bind=engine)



from application.modules.apis.hg_api import api
from application.modules.daemons.hg_supervisor import hgsuperscheduler,hgsuper
from application.modules.apis.hg_mr_job import mrapi,mrjobstatus
from application.modules.apis.hg_file_browser import filebrowser
from application.modules.daemons.filebrowsestatus import filebrowsestatus
from application.modules.daemons.hg_manager import hgmanagerscheduler,hgmanager
from application.modules.daemons.hg_manager import hgmanagerscheduler,hgmanager
from application.modules.daemons.hive_database_result_consumer import hiveDatabaseResult
from application.modules.apis.az_api import azapi
from application.modules.apis.nifi_connetor import getToken
from application.modules.daemons.job_status_consumer import statusconsumer

from application.common.file_upload import azfile
from application.common.file_download import azfiledownload
#from application.modules.workers.configure_cluster_sprint_2 import configure_cluster
#from application.modules.workers.provision_cluster_sprint2 import installcluster
from application.modules.apis.job_output_api import jobdetails
from application.modules.azure.create_customer_api import customers
from application.modules.apis.hg_mr_job import mrapi
from application.modules.apis.hg_file_browser import filebrowser
from application.modules.daemons.filebrowsestatus import filebrowsestatus
from application.modules.daemons.kafka_job_produce import mrjobproducer
from application.modules.daemons.customer_job_request_consumer import jobinsertion
from application.modules.daemons.job_diagnostic_consumer import diagnosticsconsumer
from application.modules.apis.customeruserlist import customerusers
from application.modules.apis.job_list_api import joblist
from application.modules.apis.get_cluster_size import clustersize
from application.modules.apis.get_cluster_location import clusterlocation#,cloudtype
from application.modules.apis.mapreduceapi import mapreduce
from application.modules.apis.job_diagnostics_api import jobdiagnostics
from application.common.email_generation import emailsender
#from application.modules.apis.hg_api import hiveSelectQueryResult
from multiprocessing import Process

from application.modules.workers.hive_config_worker import configure_hive
from application.modules.workers.edgenode_provision_worker import edgenodeProvision
#arvind
from application.modules.daemons.job_status_consumer import statusconsumer
from application.modules.apis.job_output_api import jobdetails
from application.modules.workers.configure_cluster_sprint_2 import configure_cluster
from application.modules.workers.provision_cluster_sprint2 import installcluster
from application.modules.apis.customeruserlist import customerusers
from application.modules.daemons.kafka_job_produce import mrjobproducer
from application.modules.daemons.customer_job_request_consumer import jobinsertion
from application.modules.apis.job_list_api import joblist
from application.modules.apis.get_cluster_size import clustersize
from application.modules.apis.get_cluster_location import clusterlocation
from application.modules.apis.mapreduceapi import mapreduce
from application.modules.apis.job_diagnostics_api import jobdiagnostics
from application.common.email_generation import emailsender
from application.modules.workers.file_upload_worker import fileuploadworker
from application.common.big_size_file_download import bigsizefiledownload
from application.modules.daemons.hive_status_consumer import kafkaHiveStatusConsumer
from application.modules.daemons.kafka_job_producer import mrjobproducer
from application.modules.daemons.hive_selectquery_url import hgSelectQueryUrlScheduler


app.register_blueprint(azfiledownload,url_prefix='')
app.register_blueprint(mapreduce, url_prefix='')
app.register_blueprint(jobdiagnostics, url_prefix='')
app.register_blueprint(clusterlocation, url_prefix='')
app.register_blueprint(clustersize, url_prefix='')
app.register_blueprint(api, url_prefix='')
app.register_blueprint(azfile,url_prefix='')
app.register_blueprint(azapi,url_prefix='')
app.register_blueprint(mrjobstatus,url_prefix='')
app.register_blueprint(mrapi,url_prefix='')
app.register_blueprint(filebrowser,url_prefix='')
app.register_blueprint(mapreduce, url_prefix='')
app.register_blueprint(jobdiagnostics, url_prefix='')
app.register_blueprint(clusterlocation, url_prefix='')
#app.register_blueprint(cloudtype, url_prefix='')
app.register_blueprint(clustersize, url_prefix='')
app.register_blueprint(customerusers,url_prefix='')
app.register_blueprint(jobdetails, url_prefix='')
app.register_blueprint(joblist, url_prefix='')

app.register_blueprint(customers, url_prefix='')
app.register_blueprint(mrapi,url_prefix='')
app.register_blueprint(filebrowser,url_prefix='')
app.register_blueprint(customerusers,url_prefix='')
app.register_blueprint(jobdetails, url_prefix='')
app.register_blueprint(joblist, url_prefix='')
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)
@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    print (links)


from application.modules.daemons.metrics_consumer import kafkaconsumer
from application.modules.daemons.task_status_consumer import kafkataskconsumer


def runProcess():
    selecturl_process = Process(target = hgSelectQueryUrlScheduler)
    selecturl_process.start()
    hgsuperscheduler_process = Process(target=hgsuperscheduler)
    hgmanagerscheduler_process = Process(target=hgmanagerscheduler)
    kafkataskconsumer_process=Process(target=kafkataskconsumer)
    kafkaconsumer_process=Process(target=kafkaconsumer)
    hgmanager_process=Process(target=hgmanager)
    hgsuper_process=Process(target=hgsuper)

    kafkaHiveStatusConsumer_process = Process(target=kafkaHiveStatusConsumer)
    kafkaHiveStatusConsumer_process.start()

    #hgsuperscheduler_process.start()
    filebrowsestatus_process=Process(target=filebrowsestatus)
    jobDiagnosticConsumer_process = Process(target=diagnosticsconsumer)
    jobDiagnosticConsumer_process.start()
    jobStatusConsumer_process = Process(target=statusconsumer)
    jobStatusConsumer_process.start()
    hiveDatabaseResultConsumer = Process(target=hiveDatabaseResult)
    hiveDatabaseResultConsumer.start()
    hgsuperscheduler_process.start()
    filebrowsestatus_process = Process(target=filebrowsestatus)
    filebrowsestatus_process.start()
    hgmanagerscheduler_process.start()
    kafkataskconsumer_process.start()
    mrjobproducer_process = Process(target=mrjobproducer)
    customerjobreqestconsumer = Process(target=jobinsertion)

    mrjobproducer_process.start()
    customerjobreqestconsumer.start()
    kafkaconsumer_process.start()
    hgmanager_process.start()
    print "Method Ended"


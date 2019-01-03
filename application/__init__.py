from flask import Flask, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application.config.config_file import  *
from logging.config import dictConfig
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['Access-Control-Allow-Origin'] = '*'
conn_string = conn_string
postgres_conn = postgres_conn

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
mongo_conn_string = mongo_conn_string

db = SQLAlchemy(app)
sqlite_string = sqlite_string

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_size=50)
session_factory = sessionmaker(bind=engine)

from db_setup import init_db

init_db()

from application.common.file_upload import azfile
from application.common.file_download import azfiledownload

from application.modules.azure.create_customer_api import customers
from multiprocessing import Process




from application.modules.core.api.hg_api import api
from application.modules.core.api.az_api import azapi
from application.modules.core.api.customeruserlist import customerusers
from application.modules.core.api.get_cluster_size import clustersize
from application.modules.core.api.get_cluster_location import clusterlocation
from application.modules.core.api.hg_file_browser import filebrowser

from application.modules.mapr.api.hg_mr_job import mrapi
from application.modules.mapr.api.hg_mr_job import mrjobstatus
from application.modules.mapr.api.job_output_api import jobdetails
from application.modules.mapr.api.job_list_api import joblist
from application.modules.mapr.api.mapreduceapi import mapreduce
from application.modules.mapr.api.job_diagnostics_api import jobdiagnostics

from application.modules.core.daemons.filebrowsestatus import filebrowsestatus
from application.modules.core.daemons.hg_manager import hgmanagerscheduler, hgmanager
from application.modules.hive.daemons.hive_database_result_consumer import hiveDatabaseResult
from application.modules.core.daemons.hg_supervisor import hgsuperscheduler, hgsuper
from application.modules.mapr.daemons.job_diagnostic_consumer import diagnosticsconsumer
from application.modules.mapr.daemons.job_status_consumer import statusconsumer
from application.modules.mapr.daemons.customer_job_request_consumer import jobinsertion
from application.modules.hive.daemons.hive_status_consumer import kafkaHiveStatusConsumer
from application.modules.core.daemons.kafka_job_producer import mrjobproducer
from application.modules.hive.daemons.hive_selectquery_url import hgSelectQueryUrlScheduler
from application.modules.core.daemons.metrics_consumer import kafkaconsumer
from application.modules.core.daemons.task_status_consumer import kafkataskconsumer


app.register_blueprint(azfiledownload, url_prefix='')
app.register_blueprint(mapreduce, url_prefix='')
app.register_blueprint(jobdiagnostics, url_prefix='')
app.register_blueprint(clusterlocation, url_prefix='')
app.register_blueprint(clustersize, url_prefix='')
app.register_blueprint(api, url_prefix='')
app.register_blueprint(azfile, url_prefix='')
app.register_blueprint(azapi, url_prefix='')
app.register_blueprint(mrjobstatus, url_prefix='')
app.register_blueprint(mrapi, url_prefix='')
app.register_blueprint(filebrowser, url_prefix='')
app.register_blueprint(mapreduce, url_prefix='')
app.register_blueprint(jobdiagnostics, url_prefix='')
app.register_blueprint(clusterlocation, url_prefix='')
# app.register_blueprint(cloudtype, url_prefix='')
app.register_blueprint(clustersize, url_prefix='')
app.register_blueprint(customerusers, url_prefix='')
app.register_blueprint(jobdetails, url_prefix='')
app.register_blueprint(joblist, url_prefix='')

app.register_blueprint(customers, url_prefix='')
app.register_blueprint(mrapi, url_prefix='')
app.register_blueprint(filebrowser, url_prefix='')
app.register_blueprint(customerusers, url_prefix='')
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





def runProcess():
    #selecturl_process = Process(target=hgSelectQueryUrlScheduler)
    #selecturl_process.start()
    #hgsuperscheduler_process = Process(target=hgsuperscheduler)
    #hgmanagerscheduler_process = Process(target=hgmanagerscheduler)
    #kafkataskconsumer_process = Process(target=kafkataskconsumer)
    #kafkaconsumer_process = Process(target=kafkaconsumer)
    hgmanager_process = Process(target=hgmanager)
    #hgsuper_process = Process(target=hgsuper)
    #hgsuper_process.start()

    #kafkaHiveStatusConsumer_process = Process(target=kafkaHiveStatusConsumer)
    #kafkaHiveStatusConsumer_process.start()

    # hgsuperscheduler_process.start()
    #filebrowsestatus_process = Process(target=filebrowsestatus)
    #jobDiagnosticConsumer_process = Process(target=diagnosticsconsumer)
    #jobDiagnosticConsumer_process.start()
    #jobStatusConsumer_process = Process(target=statusconsumer)
    #jobStatusConsumer_process.start()
    #hiveDatabaseResultConsumer = Process(target=hiveDatabaseResult)
    #hiveDatabaseResultConsumer.start()
    #hgsuperscheduler_process.start()
    #filebrowsestatus_process = Process(target=filebrowsestatus)
    #filebrowsestatus_process.start()
    #hgmanagerscheduler_process.start()
    #kafkataskconsumer_process.start()
    #mrjobproducer_process = Process(target=mrjobproducer)
    #customerjobreqestconsumer = Process(target=jobinsertion)

    #mrjobproducer_process.start()
    #customerjobreqestconsumer.start()
    #kafkaconsumer_process.start()
    hgmanager_process.start()
    print "welcome to the club"

    # configure_cluster('722f868d-09b6-11e9-b4fe-000c29da5704')
#from application.modules.hive.workers.hive_config_worker import configure_hive
#configure_hive("d416052b-0e8d-11e9-bb3d-3ca9f49ab2cc")
#from application.modules.cluster.workers.provision_cluster_sprint2 import installcluster
#installcluster('d6954e0a-0e65-11e9-bb3d-3ca9f49ab2cc')
#from application.modules.hive.workers.edgenode_provision_worker import edgenodeProvision
#edgenodeProvision('d416052a-0e8d-11e9-bb3d-3ca9f49ab2cc')
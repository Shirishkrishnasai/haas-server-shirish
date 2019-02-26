import time
import pymongo
import json
from kafka import KafkaProducer
from flask import request,Blueprint,jsonify
from sqlalchemy import exc
from application.models.models import TblAgent,TblNodeInformation
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.config.config_file import kafka_bootstrap_server,kafka_api_version
from application import mongo_conn_string
from application.common.loggerfile import my_logger
filebrowser=Blueprint('filebrowser',__name__)

@filebrowser.route("/api/filebrowser/<customerid>/<clusterid>/<filename>",methods=['GET'])
def filebrowsing(customerid,clusterid,filename):
        try:

                timestamp=str(int(round(time.time() * 1000)))
                my_logger.info(timestamp)
                my_logger.info(filename)
                db_session = scoped_session(session_factory)
                namenode_data = db_session.query(TblAgent.uid_agent_id, TblAgent.private_ips).filter(
                    TblAgent.uid_node_id == TblNodeInformation.uid_node_id) \
                    .filter(TblNodeInformation.char_role == "namenode",TblNodeInformation.uid_cluster_id == clusterid).first()
                private_ip = namenode_data[1]
                agent_id = namenode_data[0]

                my_logger.info(private_ip)
                producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_server)
                kafkatopic = "filebrowsing_" + customerid + "_" + clusterid
                kafkatopic = kafkatopic.decode('utf-8')
                filebrowser_data = {}
                filebrowser_data["customer_id"] = str(customerid)
                filebrowser_data["cluster_id"] = str(clusterid)
                filebrowser_data["agent_id"] = str(agent_id)
                filebrowser_data["filename"] = str(filename)
                filebrowser_data["namenode_ip"] = str(private_ip)
                filebrowser_data["timestamp"] = str(timestamp)
                my_logger.info(filebrowser_data)

                producer.send(kafkatopic, str(filebrowser_data))
                producer.flush()
                my_logger.info('flussshhhh')
                my_logger.info('flush')
                mongo_db_conn = pymongo.MongoClient(mongo_conn_string)
                my_logger.info("mango")
                database_conn = mongo_db_conn['haas']
                db_collection = database_conn['filebrowsingstatus']
                time.sleep(1)
                obj=list(db_collection.find({"timestamp":timestamp,"clusterid":clusterid,"filename":filename}))
                my_logger.info(obj)
                for data in obj:
                        my_logger.info(data)
                        data=data["filesinpath"].replace("'",'"')
                        json_data=json.loads(data)
                        my_logger.info(json_data)
                        my_logger.info(json_data)
                #return jsonify(json_data)
        except exc.SQLAlchemyError as e:
                return jsonify(e.message)
        except pymongo.errors.ConnectionFailure, e:
               my_logger.info(e)
               return jsonify(message='unable to connect mongo')
        except Exception as e:
               return jsonify(e.message)
        finally:
                db_session.close()





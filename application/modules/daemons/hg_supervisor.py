import psycopg2
import datetime,time
import logging

logging.basicConfig()
from apscheduler.schedulers.background import BackgroundScheduler
from application.modules.workers.configure_cluster_sprint_2 import configure_cluster
from application.config.config_file import schema_statement,assigned_status
from application.common.loggerfile import my_logger
from application import app,conn_string
def hgsuper():
	while True:
		my_logger.debug("supervisor:hai")
		try:

			status=assigned_status
			time_updated=datetime.datetime.now()
			conn=psycopg2.connect(conn_string)
			cur=conn.cursor()
			print "hg supervisor connected to database"
			cur.execute(schema_statement)
			select_customer_req_data="select uid_request_id,char_feature_id from tbl_customer_request where bool_assigned='f'"
			cur.execute(select_customer_req_data)
			required_data=cur.fetchall()
			conn.close()
			my_logger.debug("REquied Data")
			my_logger.debug(required_data)
			for row in required_data:
				request_id=row[0]
				print request_id
				# select_worker_path="select txt_worker_path from tbl_feature where char_feature_id='%s'"
				# cur.execute(select_worker_path % feature_id)
				# worker_path=cur.fetchone()
				# subprocess.call(["python",worker_path,req_id],shell=False)

				configure_cluster(request_id)
				#time.sleep(120)
				my_logger.debug("Got Request")
				conn = psycopg2.connect(conn_string)
				cur = conn.cursor()
				cur.execute(schema_statement)
				update_statement="update tbl_customer_request set bool_assigned='t',ts_requested_time='%s' where uid_request_id='%s'"
				my_logger.debug(update_statement)
				cur.execute(update_statement % (time_updated,request_id))
				conn.commit()
				insert_request_status = "insert into tbl_task_request_log (uid_request_id,int_meta_request_status,ts_time_updated)\
							 values('%s',%d,'%s')"
				cur.execute(insert_request_status % (request_id,status,time_updated))
				conn.commit()
				conn.close()
				my_logger.debug("Closing Request")
			print('install_cluster called')
			required_data=[]
		except psycopg2.DatabaseError, e:
			my_logger.debug(e.pgerror)
			#return 'database error'
		except psycopg2.OperationalError, e:
			my_logger.debug(e.pgerror)
			#return 'Operational error'
		except Exception as e:
			my_logger.error(e)
			#return 'not in json format'
		finally:
			#conn.close()
			my_logger.debug("In  Supervisor Finally..")
		time.sleep(15)
		my_logger.debug("running supervisor.. after 15 seconds...")

def hgsuperscheduler():
	#scheduler = BackgroundScheduler()
	#scheduler.add_job(hgsuper,'cron',minute='*/1')
	#scheduler.start()
	#my_logger.debug("in supervisor")
	pass


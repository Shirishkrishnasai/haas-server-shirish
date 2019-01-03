from sqlalchemy.orm import scoped_session
from application import session_factory
import datetime,time
import multiprocessing
import subprocess
import logging
logging.basicConfig()
#from apscheduler.schedulers.background import BackgroundScheduler
#from application.modules.workers.build_cluster_worker_sprint2 import installcluster
from application.models.models import TblCustomerRequest,TblMetaRequestStatus,TblFeature,TblTaskRequestLog
from application.common.loggerfile import my_logger
def hgsuper():
	while True:
			my_logger.debug("supervisor:hai")
		#try:
			db_session = scoped_session(session_factory)
			metatablestatus = db_session.query(TblMetaRequestStatus.var_request_status, TblMetaRequestStatus.srl_id).all()
			request_status_values = dict(metatablestatus)
			completed_request_status_value = request_status_values['COMPLETED']
			update_request_status_value = request_status_values['ASSIGNED']
			time_updated=datetime.datetime.now()
			print "hg supervisor connected to database"
			customer_req_data=db_session.query(TblCustomerRequest.uid_request_id,TblCustomerRequest.char_feature_id,TblCustomerRequest.txt_dependency_request_id)\
				.filter(TblCustomerRequest.bool_assigned=='f').all()
			print customer_req_data

			for row in customer_req_data:
				print 'in customer_req_data'

				request_id=row[0]
				feature_id=row[1]
				dependency_id=row[2]
				select_worker_path = db_session.query(TblFeature.txt_worker_path).filter(
					TblFeature.char_feature_id == feature_id).first()
				print select_worker_path[0]
				worker_path = select_worker_path[0]
				print worker_path
				if dependency_id == None:
					print	"in dependency_id== None"
					worker_call = multiprocessing.Process(target=worker_path, args=([request_id]))
					worker_call.start()
					my_logger.info("this is the following worker...............")
					my_logger.debug(""+worker_path)
					worker_call.join()
					#subprocess.call(["python", worker_path, request_id], shell=False)
					my_logger.debug("Got Request")
					update_object = db_session.query(TblCustomerRequest).filter(
						TblCustomerRequest.uid_request_id == request_id)
					update_statement = update_object.update({"bool_assigned": 1, "ts_requested_time": time_updated})
					my_logger.debug(update_statement)
					insert_request_status = TblTaskRequestLog(uid_request_id=request_id,
															  int_meta_request_status=update_request_status_value,
															  ts_time_updated=time_updated)
					db_session.add(insert_request_status)
					db_session.commit()
					my_logger.debug("Closing Request")

				else:
					print "in dependency"
					list_of_dependency_requests = dependency_id.split(',')

					completedrequests = []


					for each_id in list_of_dependency_requests:
						dependency_request_id = each_id.replace('"', '')
						dependency_request_status = db_session.query(TblCustomerRequest.int_request_status).filter(
							TblCustomerRequest.uid_request_id == dependency_request_id)
						print dependency_request_status,'sssssssssttttattttuss'
						dependency_request_status_value = dependency_request_status[0]
						if dependency_request_status_value[0] == completed_request_status_value:
							completedrequests.append(dependency_request_status)
							print 'done'
					if len(completedrequests) == len(list_of_dependency_requests):
						worker_call = multiprocessing.Process(target=worker_path, args=([request_id, ]))
						worker_call.start()
						my_logger.info("this is the following worker...............")
						my_logger.debug(worker_path)
						worker_call.join()
						#subprocess.call(["python",worker_path,request_id],shell=False)
						#my_logger.debug("Got Request")
						update_object = db_session.query(TblCustomerRequest).filter(
							TblCustomerRequest.uid_request_id == request_id)
						update_statement = update_object.update(
							{"bool_assigned": 1, "ts_requested_time": time_updated})
						my_logger.debug(update_statement)
						insert_request_status = TblTaskRequestLog(uid_request_id=request_id,
																  int_meta_request_status=update_request_status_value,
																  ts_time_updated=time_updated)
						db_session.add(insert_request_status)
						db_session.commit()
						my_logger.debug("Closing Request")
					else:
						pass
				time.sleep(15)


				required_data=[]

		#except Exception as e:
			#my_logger.error(e)
			#return 'not in json format'
		#finally:
			#conn.close()
			#my_logger.debug("In  Supervisor Finally..")
		#time.sleep(15)
		#my_logger.debug("running supervisor.. after 15 seconds...")

def hgsuperscheduler():
	#scheduler = BackgroundScheduler()
	#scheduler.add_job(hgsuper,'cron',minute='*/1')
	#scheduler.start()
	#my_logger.debug("in supervisor")
	pass


from flask import jsonify
from application import db
from application.models.models import TblMetaTaskStatus,TblAgent,TblTask
from application.common.kafka_producer import kafkaproducer
from application.common.loggerfile import my_logger
from apscheduler.schedulers.background import BackgroundScheduler

def hgmanager():
	try:

# Fetching data from meta taskstatus table
		metatablestatus=db.session.query(TblMetaTaskStatus.var_task_status,TblMetaTaskStatus.srl_id).all()
		table_status_values = dict(metatablestatus)
		task_status_value = table_status_values['CREATED']
		update_task_status_value = table_status_values['ASSIGNED']
		completed_task_status_value = table_status_values['COMPLETED']
		agent_verification_result=db.session.query(TblAgent.bool_registered,TblAgent.uid_agent_id)

# Geting agents from database

		for agent_registration in agent_verification_result:
			agent_tasks_data = []
			if agent_registration[0]==True:

# Listing tasks
				created_tasks=db.session.query(TblTask.uid_task_id,TblTask.char_task_type_id,TblTask.txt_dependent_task_id,TblTask.txt_agent_worker_version,TblTask.txt_agent_worker_version_path,TblTask.txt_payload_id,TblTask.int_task_status).filter(TblTask.uid_agent_id==agent_registration[1],TblTask.int_task_status==task_status_value)
				agent_customer_cluster_details=db.session.query(TblAgent.uid_customer_id,TblAgent.uid_cluster_id).filter(TblAgent.uid_agent_id==agent_registration[1])
				for each_tuple in created_tasks:
					dependency_tasks= each_tuple[2]

					if dependency_tasks==None:
						taskdata = {}
						task_id=each_tuple[0]
						
						taskdata['cluster_id']=agent_customer_cluster_details[0][1]
						taskdata['customer_id']=agent_customer_cluster_details[0][0]
						taskdata['agent_worker_path'] = each_tuple[4]
						taskdata['agent_worker_version'] = each_tuple[3]
						taskdata['task_type_id'] = each_tuple[1]
						taskdata['task_id']=task_id
						taskdata['payload_id']=each_tuple[5]
						taskdata['task_status']=each_tuple[6]
						agent_tasks_data.append(taskdata)
						update_taskstatus_statement=db.session.query(TblTask).filter(TblTask.uid_task_id==task_id)
						update_taskstatus_statement.update({"int_task_status":update_task_status_value})
						db.session.commit()
					else:
						list_of_dependency_tasks=dependency_tasks.split(',')
						task_id=each_tuple[0]
						taskdata = {}
						taskdata['cluster_id']=agent_customer_cluster_details[0][1]
						taskdata['customer_id']=agent_customer_cluster_details[0][0]
						taskdata['task_id']=task_id
						taskdata['agent_worker_path']=each_tuple[4]
						taskdata['agent_worker_version']=each_tuple[3]
						taskdata['task_type_id']=each_tuple[1]
						taskdata['payload_id']=each_tuple[5]
						taskdata['task_status'] = each_tuple[6]
						completedtasks=[]

						for each_id in list_of_dependency_tasks:
							dependency_task_id=each_id.replace('"','')
							dependency_task_status=db.session.query(TblTask.int_task_status).filter(TblTask.uid_task_id==dependency_task_id)
							dependency_task_status_value=dependency_task_status[0]
							if dependency_task_status_value==completed_task_status_value:
								completedtasks.append(dependency_task_status)
						if len(completedtasks)==len(list_of_dependency_tasks):
							agent_tasks_data.append(taskdata)
							update_assigned_statement=db.session.query(TblTask).filter(TblTask.uid_task_id==task_id)
							update_assigned_statement.update({"int_task_status":update_task_status_value})
							db.session.commit()
				if agent_tasks_data == []:
					my_logger.debug(nodata)
				else:
					kafkaproducer(message=agent_tasks_data)
					my_logger.debug('message')
			else:
				return jsonify(message="agent is not registered")


	except Exception as e:
		return e.message

def taskpublisherscheduler():
		scheduler = BackgroundScheduler()
		scheduler.add_job(hgmanager,'cron',minute='*/1' )
		scheduler.start()
from sqlalchemy.orm import scoped_session
from application import session_factory
from apscheduler.schedulers.background import BackgroundScheduler
from application import app, conn_string, db
from application.models.models import TblMetaTaskStatus, TblAgent, TblTask
from application.common.kafka_producer import kafkaproducer
from application.common.loggerfile import my_logger

import time,os,sys

def hgmanager():
    while True:
        try:

            # Fetching data from meta taskstatus table
            db_session = scoped_session(session_factory)
            metatablestatus = db_session.query(TblMetaTaskStatus.var_task_status, TblMetaTaskStatus.srl_id).all()
            table_status_values = dict(metatablestatus)
            task_status_value = table_status_values['CREATED']
            update_task_status_value = table_status_values['ASSIGNED']
            completed_task_status_value = table_status_values['COMPLETED']
            agent_verification_result = db_session.query(TblAgent.bool_registered, TblAgent.uid_agent_id)

            # Geting agents from database
            print agent_verification_result
            for agent_registration in agent_verification_result:
                agent_tasks_data = []
                if agent_registration[0] == True:
                    print "agent verification done"
                    #print "true"
                    # Listing tasks
                    #print task_status_value, "task_status"
                    #print agent_registration
                    created_tasks = db_session.query(TblTask.uid_task_id, TblTask.char_task_type_id,
                                                     TblTask.txt_dependent_task_id, TblTask.txt_agent_worker_version,
                                                     TblTask.txt_agent_worker_version_path, TblTask.txt_payload_id,
                                                     TblTask.int_task_status).filter(
                        TblTask.uid_agent_id == agent_registration[1], TblTask.int_task_status == task_status_value).all()
                    agent_customer_cluster_details = db_session.query(TblAgent.uid_customer_id,
                                                                      TblAgent.uid_cluster_id).filter(
                        TblAgent.uid_agent_id == agent_registration[1])
                    print "hg manager fetched tasks and agent information"
                    #print created_tasks, "tasks"
                    for each_tuple in created_tasks:
                        dependency_tasks = each_tuple[2]
                        #      print dependency_tasks
                        if dependency_tasks == None:
                            taskdata = {}
                            task_id = each_tuple[0]
                            payload = each_tuple[5]
                            payload_str = str(payload)
                            taskdata['agent_id'] = agent_registration[1]
                            taskdata['event_type'] = 'tasks'
                            taskdata['cluster_id'] = agent_customer_cluster_details[0][1]
                            taskdata['customer_id'] = agent_customer_cluster_details[0][0]
                            taskdata['worker_path'] = each_tuple[4]
                            taskdata['worker_version'] = each_tuple[3]
                            taskdata['task_type_id'] = each_tuple[1]
                            taskdata['task_id'] = task_id
                            taskdata['payload_id'] = payload_str
                            taskdata['task_status'] = each_tuple[6]
                            agent_tasks_data.append(taskdata)
                            print payload_str
                            # print agent_tasks_data,'no dependencies'
                            update_taskstatus_statement = db_session.query(TblTask).filter(TblTask.uid_task_id == task_id)
                            update_taskstatus_statement.update({"int_task_status": update_task_status_value})
                            db_session.commit()
                        else:
                            list_of_dependency_tasks = dependency_tasks.split(',')
                            task_id = each_tuple[0]
                            taskdata = {}
                            payload = each_tuple[5]
                            payload_str = str(payload)
                            taskdata['agent_id'] = agent_registration[1]
                            taskdata['event_type'] = 'tasks'
                            taskdata['cluster_id'] = agent_customer_cluster_details[0][1]
                            taskdata['customer_id'] = agent_customer_cluster_details[0][0]
                            taskdata['task_id'] = task_id
                            taskdata['worker_path'] = each_tuple[4]
                            taskdata['worker_version'] = each_tuple[3]
                            taskdata['task_type_id'] = each_tuple[1]
                            taskdata['payload_id'] = payload_str
                            taskdata['task_status'] = each_tuple[6]
                            completedtasks = []
                            print payload_str
                            for each_id in list_of_dependency_tasks:
                                dependency_task_id = each_id.replace('"', '')
                                dependency_task_status = db_session.query(TblTask.int_task_status).filter(
                                    TblTask.uid_task_id == dependency_task_id)
                                dependency_task_status_value = dependency_task_status[0]
                                if dependency_task_status_value[0] == completed_task_status_value:
                                    completedtasks.append(dependency_task_status)
                            if len(completedtasks) == len(list_of_dependency_tasks):
                                agent_tasks_data.append(taskdata)

                                print agent_tasks_data, 'dependency', 'last if'
                                update_assigned_statement = db_session.query(TblTask).filter(TblTask.uid_task_id == task_id)
                                update_assigned_statement.update({"int_task_status": update_task_status_value})
                                db_session.commit()
                    #	    print agent_tasks_data
                    if agent_tasks_data == []:
                        print("nodata")
                    else:
                        print agent_tasks_data, "agent data"
                        kafkaproducer(message=agent_tasks_data)
                        print "hgmanager producedddddddddddddddddddd"
                else:
                    print 'hgmanager else'
        #           return jsonify(message="agent is not registered")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

            my_logger.error(exc_type)
            my_logger.error(fname)
            my_logger.error(exc_tb.tb_lineno)
        finally:
            print "HG_MANAGER in Finally"
            db_session.close()
        time.sleep(15)

def hgmanagerscheduler():
    #scheduler = BackgroundScheduler()
    #scheduler.add_job(hgmanager, 'cron', minute='*/1')
    #scheduler.start()
    pass

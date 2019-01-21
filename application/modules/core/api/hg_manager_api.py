from flask import Flask,jsonify
import psycopg2
from application import conn_string
from application import app,db
from flask import Blueprint,render_template,abort
from application.models.models import TblTask,TblAgent,TblMetaTaskStatus


highgearmanager=Blueprint('highgearmanager', __name__)
@highgearmanager.route("/hgmanager/<agent_id>",methods=["GET"])
def hgmanager(agent_id):
    try:
        agent_id=agent_id
        agent_info_query_statement=db.session.query(TblAgent.bool_registered).filter(TblAgent.uid_agent_id==agent_id).all()
        r =agent_info_query_statement[0][0]
        print "hello",agent_info_query_statement,r
        meta_task_status_query=db.session.query(TblMetaTaskStatus.var_task_status).filter(TblMetaTaskStatus.var_task_status=='ASSIGNED').all()
        status_result=meta_task_status_query[0][0]
        print "metastatus",status_result
        list1 = []
        dict = {}
        if r == True:
            print "hii",status_result
            task_info_query_statement=db.session.query(TblTask.uid_task_id,TblTask.char_task_type_id,TblTask.txt_dependent_task_id,
                                                       TblTask.txt_agent_worker_version,TblTask.txt_agent_worker_version_path,
                                                       TblTask.txt_payload_id).filter(TblAgent.uid_agent_id==agent_id,TblTask!=status_result).all()

            print "resultresult",task_info_query_statement
            for res1 in task_info_query_statement:

                  dependency_tasks= res1[2]
                  print "depentask",dependency_tasks
                  if dependency_tasks==None:
                    task_id=res1[0]
                    dict['agent_worker_version_path'] = res1[4]
                    dict['agent_worker_version'] = res1[3]
                    dict['task_type_id'] = res1[1]
                    dict['task_id']=task_id
                    dict['payload_id']=res1[5]
                    list1.append(dict)
                    update_task_status=db.session.query(TblTask).filter(TblTask.uid_task_id==dependency_tasks)
                    # update_statement="update tbl_tasks set var_task_status='a' where uid_task_id='%s'"
                    # update_res=cur.execute(update_statement % task_id)
                    # conn.commit()
                    print "dictdict",dict
                  else:
                    list_of_tasks_list=dependency_tasks.split(',')
                    list_of_tasks=list_of_tasks_list[0][0]
                    print "lists",list_of_tasks
                    task_id=res1[0]
                    dict['task_id']=task_id
                    dict['agent_worker_version_path']=res1[4]
                    dict['agent_worker_version']=res1[3]
                    dict['task_type_id']=res1[1]
                    dict['payload_id']=res1[5]


                   # list1.append(dict)
                    for id in list_of_tasks_list:
                        list = []
                        id = str(id)
                        id1 = id.split('"')
                        id2 = id1[1]
                        print "hellllll",id2

                        # statement2 = "select var_task_status from tbl_tasks where uid_task_id='%s'"
                        # result = cur.execute(statement2 % id2)
                        # result1 = cur.fetchall()
                        # result2 = result1[0][0]
                        # result3 = result2.split('@')
                        statement2=db.session.query(TblTask).filter(TblTask.uid_task_id==dependency_tasks).all()
                        result2 = statement2[0][0]
                        result3 = result2.split('@')
                        print "result3",result3
                        if result3[0] == "completed":
                            list.append(result3)
                    print "hhhhhh",list
                    if len(list) == len(list_of_tasks):
                        list1.append(dict)
                        update_statement=db.session.query(TblTask).filter(TblTask.uid_task_id==dependency_tasks).update(TblTask.uid_task_id==status_result)
                        # update_statement = "update tbl_tasks set var_task_status='a' where uid_task_id='%s'"
                        # update_res = cur.execute(update_statement % task_id)
                        # conn.commit()
            print "resultis",list1
        return jsonify(data=list1)

    except Exception as e:
        return e.message



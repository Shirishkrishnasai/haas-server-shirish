from flask import Flask,jsonify
import psycopg2
from application import app,conn_string
from flask import Blueprint,render_template,abort


highgearmanager=Blueprint('highgearmanager', __name__)
@highgearmanager.route("/hgmanager/<id>",methods=['GET'])
def hgmanager(id):
    conn=psycopg2.connect(conn_string)
    cur=conn.cursor()
    cur.execute("set search_path to highgear;")
    statement="select bool_registered from tbl_agent where uid_agent_id='%s';"
    verification=cur.execute(statement % id)
    ver_res=cur.fetchall()
    print ver_res
    r=ver_res[0][0]
    print r
    resultset=[]

    if r==True:
        print "hii"
        statement1="select uid_task_id,lng_task_type_id,txt_dependent_task_id,txt_agent_worker_version,txt_agent_worker_version_path,txt_payload_id from tbl_tasks where uid_agent_id='%s' and var_task_status='created';"
        res = cur.execute(statement1 % id)
        result = cur.fetchall()
#        print result

        for res1 in result:
#          print "REST",res1
          dependency_tasks= res1[2]

          if dependency_tasks==None:
            task_id=res1[0]
            taskdata = {}
#           print "Adding non dependency tasks"
            taskdata['agent_worker_version_path'] = res1[4]
            taskdata['agent_worker_version'] = res1[3]
            taskdata['task_type_id'] = res1[1]
            taskdata['task_id']=task_id
            taskdata['payload_id']=res1[5]
            resultset.append(taskdata)
            update_statement="update tbl_tasks set var_task_status='a' where uid_task_id='%s'"
            update_res=cur.execute(update_statement % task_id)
            conn.commit()
 #           print "Task data",taskdata
 #           print "All list",resultset
          else:
            list_of_tasks=dependency_tasks.split(',')
 #           print list_of_tasks
            task_id=res1[0]
            taskdata = {}
            taskdata['task_id']=task_id
            taskdata['agent_worker_version_path']=res1[4]
            taskdata['agent_worker_version']=res1[3]
            taskdata['task_type_id']=res1[1]
            taskdata['payload_id']=res1[5]


           # list1.append(dict)
            completedtasks=[]

            for id in list_of_tasks:
                list=[]
                id=str(id)
                id1=id.split('"')
                id2=id1[1]
#                print id2

                statement2="select var_task_status from tbl_tasks where uid_task_id='%s'"
                result=cur.execute(statement2 %id2)
                result1=cur.fetchall()
                result2= result1[0][0]
                result3=result2.split('@')
                if result3[0]=="completed":
                    completedtasks.append(result3)
#            print completedtasks,"hiiiii"
            if len(completedtasks)==len(list_of_tasks):
#                print "Adding dependy... tasks",resultset
                resultset.append(taskdata)
                update_statement = "update tbl_tasks set var_task_status='a' where uid_task_id='%s'"
                update_res = cur.execute(update_statement % task_id)
                conn.commit()
#        print resultset,"hooo"
    return jsonify(data=resultset)



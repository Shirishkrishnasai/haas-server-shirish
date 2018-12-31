from flask import Flask,jsonify,request
import psycopg2
import datetime
from application import app,conn_string
from flask import Blueprint,render_template,abort
highgearmonitor=Blueprint('highgearmonitor', __name__)
@highgearmonitor.route("/hgmonitor",methods=['POST'])
def monitor():
    print 'hahahahahahahahahahaha'
    data=request.json
    print data
    status=data['status']
    date=datetime.datetime.now()
    print date
    task_id=data['task_id']
    print status,task_id
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    schema_connection = cur.execute("set search_path to highgear")
    statement = "update tbl_tasks set var_task_status='"+str(status)+"@"+str(date)+"' where uid_task_id="+"'"+task_id+"'"
    database_insertion=cur.execute(statement)
    conn.commit()
    statement1="select uid_request_id from tbl_tasks where uid_task_id="+"'"+task_id+"'"
    get_request_id=cur.execute(statement1)
    request_id=cur.fetchall()
    req_request_id=request_id[0][0]
    print req_request_id
    statement2="select uid_task_id,var_task_status from tbl_tasks where uid_request_id="+"'"+req_request_id+"'"
    get_tasks=cur.execute(statement2)
    tasks=cur.fetchall()
    list1=[]
    list2=[]
    for task in tasks:
        list1.append(task[0])
 #       print [1]
        status=task[1].split("@")
        if status[0]=="completed":
            list2.append(status[0])
  #  print list1
  #  print list2
    if len(list1)==len(list2):
        statement3="update tbl_customer_request set var_request_status='completed' where uid_request_id="+"'"+req_request_id+"'"
        cur.execute(statement3)
        conn.commit()
    else:
        statement4="update tbl_customer_request set var_request_status='pending' where uid_request_id="+"'"+req_request_id+"'"
        cur.execute(statement4)
        conn.commit()




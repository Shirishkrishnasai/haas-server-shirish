
import requests
from flask import Flask,jsonify,request,Request
import json
from flask import Blueprint,render_template,abort
from uuid import getnode as get_mac
import psycopg2
import urllib2
import urllib
import psycopg2.extras
import sys
from application import app,conn_string
from flask import Blueprint,render_template,abort

agent=Blueprint('agent', __name__)




@agent.route('/register',methods=['POST'])
def register():
   try:
	print 'helooooooooooooooooooooooooooooo'
	content=request.json
	print content
	print type(content)
	agent_id=str(content['agent_id'])
	print agent_id,type(agent_id)
	customer_id=int(content['customer_id'])
	print customer_id,type(customer_id)
	cluster_id=str(content['cluster_id'])
	print cluster_id,type(cluster_id)
	agent_version=str(content['agent_version'])
	print agent_version,type(agent_version)
	#conn = psycopg2.connect(host="192.168.100.108", user="postgres", password="password", dbname="haas")
	conn=psycopg2.connect(conn_string)
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	statement =  "select uid_agent_id,lng_customer_id,uid_cluster_id,str_agent_version from highgear.tbl_agent where uid_agent_id='%s' and lng_customer_id='%d' and uid_cluster_id='%s' and str_agent_version='%s'"
	cur.execute(statement % (agent_id,customer_id,cluster_id,agent_version))
	res=cur.fetchone()
	print 'jjjjjjjjjjjjjjjjjjj',res
	if(res):
		print 'yyyyaaaaaaaaaaaaayyyyyyyyyy'
		update_statement = "update highgear.tbl_agent set bool_registered='t' where uid_agent_id='%s' and uid_cluster_id='%s'"
		cur.execute(update_statement % (agent_id,cluster_id))
		conn.commit()
		print 'done-done-london2'
		return jsonify(message="agent registered successfully")
	else:
		return jsonify(message="incorrect agent details")
   except Exception as e:
        print e.message
	return  jsonify(message="something went wrong")



	#update_statement="


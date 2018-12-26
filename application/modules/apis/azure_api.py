import ldap as pyldap
from flask import Flask,jsonify,request,Blueprint
import datetime
#from application import app,conn_string
#from application.common.loggerfile import my_logger
azapi=Blueprint('azapi', __name__)




@azapi.route("/azapi/customer/users", methods=['GET'])

def getCustomerUsers():
		

		ldap_conn = pyldap.initialize('ldap://192.168.100.145:389')
                ldap_conn.simple_bind_s("cn=ldapadm,dc=kwartile,dc=local", "ldppassword")
		ldap_search_result = ldap_conn.search_s("ou=marvel,dc=kwartile,dc=local", ldap.SCOPE_SUBTREE)
		print ldap_search_result

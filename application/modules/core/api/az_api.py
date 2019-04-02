import datetime
import random
import jwt
import ldap
import os,sys
from application import  session_factory
from application.config.config_file import ldap_connection, ldap_connection_dn, ldap_connection_password
from application.models.models import TblUsers, TblNodeInformation, TblCustomer, TblAzureFileStorageCredentials
from flask import jsonify, request, Blueprint
from sqlalchemy.orm import scoped_session
from application.common.loggerfile import my_logger
azapi = Blueprint('azapi', __name__)

"""
Getting list of customers from LDAP
"""
@azapi.route("/api/customer/<customer_id>", methods=['GET'])
def getCustomerUsers(customer_id):
    try:
        db_session = scoped_session(session_factory)
        my_logger.info("azapi.route('/api/customer/<customer_id>', methods=['GET']) is get list of users in customer ")
        select_customer_dn = db_session.query(TblCustomer.txt_customer_dn).filter(
            TblCustomer.uid_customer_id == customer_id).all()
        customer_dn = select_customer_dn[0][0]
        if customer_dn != None :
            ldap_conn = ldap.initialize(ldap_connection)
            ldap_conn.simple_bind_s(ldap_connection_dn, ldap_connection_password)
            ldap_search_result = ldap_conn.search_s(customer_dn, ldap.SCOPE_SUBTREE)
            users_count = len(ldap_search_result) - 2
            users_list = []
            for each_user in range(users_count):
                users_dict = {}
                user_name = ldap_search_result[each_user + 2][1]['uid']
                users_dict['user_name'] = user_name[0]
                users_dict['active'] = "true"
                users_list.append(users_dict)
            return jsonify(users_list)
        else :
            return jsonify("no customer " + customer_id)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

"""
Create Customer user in LDAP
"""

@azapi.route('/api/customer/user/ldap', methods=['POST'])
def createUserLdap():
    try:
        db_session = scoped_session(session_factory)
        my_logger.info("@azapi.route('/api/customer/user/ldap', methods=['POST']) is used for creating customer information in ldap")
        content = request.json
        display_name = content['first_name'] + content['second_name']
        sn = content['second_name']
        password = content['password']
        uid = content['email']
        customer_id = content['customer_id']
        cn = content['first_name'] + content['second_name']
        connect = ldap.initialize(ldap_connection)
        connect.simple_bind_s(ldap_connection_dn, ldap_connection_password)
        select_customer_dn = db_session.query(TblCustomer.txt_customer_dn).filter(
            TblCustomer.uid_customer_id == customer_id).all()
        customer_dn = select_customer_dn[0][0]
        customer_gid_query = db_session.query(TblCustomer.int_gid_id).filter(
            TblCustomer.uid_customer_id == customer_id).all()
        customer_gid_id = customer_gid_query[0][0]
        dn = "cn=" + cn + "," + customer_dn
        modlist = {
            "objectClass": ["inetOrgPerson", "posixAccount"],
            "uid": [str(uid)],
            "sn": [str(sn)],
            "displayName": [str(display_name)],
            "userPassword": [str(password)],
            "uidNumber": ["1021"],
            "gidNumber": [str(customer_gid_id)],
            "loginShell": ["/bin/bash"],
            "homeDirectory": ["/home/users/"]
        }
        # addModList transforms your dictionary into a list that is conform to ldap input.
        addinguser = connect.add_s(dn, ldap.modlist.addModlist(modlist))
        if addinguser:
            data = TblUsers(uid_customer_id=customer_id,
                            var_user_name=uid,
                            txt_dn=dn,
                            bool_active=1,
                            ts_created_time=datetime.datetime.now(),
                            var_created_by='system')
            db_session.add(data)
            db_session.commit()

            select_user_dn = db_session.query(TblUsers).filter(TblUsers.var_user_name == uid).order_by(
                TblUsers.srl_id.desc()).all()

            get_data = [rows.to_json() for rows in select_user_dn]
            connect.unbind_s()
            return jsonify(message="user is added", userdata=get_data)
        else:
            connect.unbind_s()
            return jsonify(message="user is not added")

    except ldap.INVALID_CREDENTIALS:
        return jsonify(message="Your username or password is incorrect.")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()



"""
Authenticating user
"""


@azapi.route('/api/customer/user/auth', methods=['POST'])
def userAuthenticate():
    try:
        db_session=scoped_session(session_factory)
        connect = ldap.initialize(ldap_connection)
        my_logger.info("@azapi.route('/api/customer/user/auth', methods=['POST']) is used to check authentication of user")
        content = request.json
        mail = content['email']
        password = content['password']
        select_user_dn = db_session.query(TblUsers.uid_customer_id).filter(TblUsers.var_user_name == mail).all()
        customer_id = select_user_dn[0][0]
        payload = {'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
                   'uid': mail,
                   'customerid': customer_id}
        algorithm = 'HS256'
        secret_key = "qwartile"
        # connect = ldap.initialize(ldap_connection)
        select_user_dn = db_session.query(TblUsers.txt_dn).filter(TblUsers.var_user_name == mail).all()
        dn = select_user_dn[0][0]
        connect.bind_s(dn, password)
        token = jwt.encode(payload, secret_key, algorithm)
        data = {}
        data['user_name'] = mail
        data['token'] = token
        data['customer_id'] = customer_id
        connect.unbind_s()
        return jsonify(data=data)

    except ldap.INVALID_CREDENTIALS:
        return jsonify(message="Your username or password is incorrect.")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


"""
Deleting user
"""

@azapi.route('/api/customer/user/del', methods=['POST'])
def removeUser():
    try:
        db_session = scoped_session(session_factory)

        my_logger.info("@azapi.route('/api/customer/user/del', methods=['POST']) is used to delete the user")
        content = request.json
        uid = content['user_name']
        select_user_dn = db_session.query(TblUsers.txt_dn).filter(TblUsers.var_user_name == uid).all()
        dn = select_user_dn[0][0]
        connect = ldap.initialize(ldap_connection)
        connect.simple_bind_s(ldap_connection_dn, ldap_connection_password)
        del_user = connect.delete_s(dn)
        connect.unbind_s()
        if del_user:
            object = db_session.query(TblUsers).filter(TblUsers.var_user_name == uid)
            object.update({"bool_active": 0})
            db_session.commit()
            return jsonify(message="user deleted")
        else:
            return jsonify(message="user deletion is un successful")
    except ldap.INVALID_CREDENTIALS:
        return "Your username or password is incorrect."
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


@azapi.route("/api/cluster_members/<customer_id>/<cluster_id>", methods=['GET'])
def clustermembers(customer_id, cluster_id):
    try:
        db_session = scoped_session(session_factory)
        my_logger.info("@azapi.route('/api/cluster_members/<customer_id>/<cluster_id>', methods=['GET']) is used to get node information of cluster")
        customer_id = customer_id
        cluster_id = cluster_id
        # Query cluster members from tbl_node_information
        cluster_info_query_statement = db_session.query(TblNodeInformation.char_role,TblNodeInformation.uid_node_id,TblNodeInformation.uid_vm_id). \
            filter(TblNodeInformation.uid_customer_id == customer_id,
                   TblNodeInformation.uid_cluster_id == cluster_id).all()
        clust_members=[]
        for clust in cluster_info_query_statement:
            node_info={}
            node_info["role"]=clust[0]
            node_info["node_id"]=clust[1]
            node_info["vm_id"]=clust[2]
            clust_members.append(node_info)
        return jsonify(cluster_members=clust_members)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()

@azapi.route("/api/azure_credentials/<customer_id>", methods=['GET'])
def azureFileStorageCredentials(customer_id):
    try:
        db_session = scoped_session(session_factory)
        azure_file_storage_credentials_statement = db_session.query(TblAzureFileStorageCredentials).all()
        keys_list = []
        for val in azure_file_storage_credentials_statement:
            values_dict = dict(val)
            azure_account_name = values_dict['account_name']
            keys_list.append(values_dict['account_primary_key'])
            keys_list.append(values_dict['account_secondary_key'])
        return jsonify(account_name=azure_account_name, key=str(random.choice(keys_list)))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        db_session.close()


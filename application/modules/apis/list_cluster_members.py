from flask import Blueprint,request,jsonify
import json
from application import app,db
from application.models.models import TblNodeInformation

cluster_members=Blueprint('cluster_members', __name__)
@cluster_members.route("/api/cluster_members/<customer_id>/<cluster_id>",methods=['GET'])

def clustermemers(customer_id,cluster_id):
    #customer_request=request.json
    try:
        customer_id=customer_id
        cluster_id=cluster_id

    #Query cluster members from tbl_node_information


        cluster_info_query_statement=db.session.query(TblNodeInformation).filter(TblNodeInformation.uid_cluster_id==cluster_id,TblNodeInformation.uid_customer_id==customer_id).all()
        list_cluster_info=[i.to_json() for i in cluster_info_query_statement]
        cluster_roles=[]
        for dict_cluster_info in list_cluster_info:
            json_cluster_info=json.loads(dict_cluster_info)
            cluster_roles.append({"role":json_cluster_info['char_role'],"node_id":json_cluster_info['uid_node_id']})
        return jsonify(cluster_members=cluster_roles)
    except Exception as e:
        return e.message

from flask import Blueprint,jsonify
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.models.models import TblCustomer,TblCluster,TblPlanClusterSize,TblSize

clustersize = Blueprint('clustersize',__name__)
@clustersize.route("/clustersize/<customer_id>/<clusterid>",methods=['GET'])

def customerclustersize(customer_id,clusterid):
    session = scoped_session(session_factory)
    customer_query=session.query(TblCustomer.int_plan_id).filter(TblCustomer.uid_customer_id==customer_id).all()
    cluster_query=session.query(TblCluster.int_size_id).filter(TblCluster.uid_customer_id==customer_id,TblCluster.uid_cluster_id==clusterid).all()
    clustersize_query=session.query(TblPlanClusterSize.int_nodes).filter(TblPlanClusterSize.int_size_id==cluster_query[0][0],TblPlanClusterSize.int_plan_id==customer_query[0][0]).all()
    size_table_query=session.query(TblSize.var_size_type).filter(TblSize.int_size_id==cluster_query[0][0]).all()
    cluster_size_info={}
    cluster_size_info['cluster_size']=size_table_query[0][0]
    cluster_size_info['number 0f nodes']=clustersize_query[0][0]
    return jsonify(cluster_size_info)




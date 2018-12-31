from application import session_factory
from application.models.models import TblMetaCloudLocation
from flask import Blueprint, jsonify
from sqlalchemy.orm import scoped_session

clusterlocation = Blueprint('clusterlocation', __name__)


@clusterlocation.route("/clusterlocation/cloudtype", methods=['GET'])
def clusterLocation():
    session = scoped_session(session_factory)
    # meta_cluster_location_query=session.query(TblMetaCloudLocation.var_cloud_type,TblMetaCloudLocation.var_location).filter(TblMetaCloudLocation.var_cloud_type==cloudtype).all()
    meta_cluster_location_query = session.query(TblMetaCloudLocation.var_cloud_type,
                                                TblMetaCloudLocation.var_location).all()
    dict_location = {}
    list_location = []
    for cluster_location in meta_cluster_location_query:
        # print cluster_location
        cloud_type = cluster_location[0]
        if cloud_type in dict_location:
            # print cluster_location,"inside"

            dict_location[cloud_type].append(cluster_location[1])
        else:
            dict_location[cloud_type] = [cluster_location[1]]
            # print dict_location,"else"
    print dict_location, "dciciciic"
    result_dict = {}
    end_list = []
    locations_dict = {}

    # print result_dict,"starting"
    for keys, values in dict_location.items():
        # print keys,"keyssssssss"
        # print values,"valuessssssssss"
        result_dict["cloud_type"] = keys
        locations_list = []
        for vals in values:
            # print values,"lueeeeeeeeeeeeeeeeeeeeee"
            # print vals,"vallllllllllllllllllllllllllll"
            locations_dict["key"] = vals
            locations_dict["value"] = vals
            locations_list.append(locations_dict.copy())
        result_dict["location"] = locations_list
        end_list.append(result_dict.copy())
        locations_list = []
        print locations_list, "locaaaaaaaaaaaaaaaaaa"
        # print result_dict,"before append"

    print end_list, "after apendddd"
    return jsonify(end_list)

# cloudtype=Blueprint('cloudtype',__name__)
# @cloudtype.route("/cloudtype/<cloudtype>",methods=['GET'])
# def cloudType(cloudtype):
#    session = scoped_session(session_factory)
#    meta_cloud_type_query=session.query(TblMetaCloudType.float_ram,TblMetaCloudType.float_disk_size,TblMetaCloudType.float_cpu,TblMetaCloudType.var_vm_type,TblMetaCloudType.var_cloud_type).\
#        filter(TblMetaCloudType.var_cloud_type==cloudtype).all()
#    dict_type={}
#    list_type = []
#    for cloud_type in meta_cloud_type_query:
#        print cloud_type
#        list_type.append(cloud_type)
#    dict_type[cloudtype]=list_type
#    return jsonify(dict_type)

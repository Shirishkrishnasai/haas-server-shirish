from flask import Blueprint,jsonify
from application.models.models import TblMetaCloudLocation, TblMetaCloudType,TblClusterType
from sqlalchemy.orm import scoped_session
from application import session_factory

clusterlocation=Blueprint('clusterlocation',__name__)
@clusterlocation.route("/clusterlocation/cloudtype",methods=['GET'])
def clusterLocation():
    session = scoped_session(session_factory)
    #meta_cluster_location_query=session.query(TblMetaCloudLocation.var_cloud_type,TblMetaCloudLocation.var_location).filter(TblMetaCloudLocation.var_cloud_type==cloudtype).all()
    meta_cluster_location_query = session.query(TblMetaCloudLocation.var_cloud_type,TblMetaCloudLocation.var_location,TblMetaCloudLocation.srl_id,TblClusterType.uid_cluster_type_id)\
        .filter(TblMetaCloudLocation.var_cloud_type==TblClusterType.char_name).all()
    dict_location={}
    list_location = []
    location_id_list = []
    cloud_type_id_list = []
    #print meta_cluster_location_query,'meeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    for cluster_location in meta_cluster_location_query:
        #print cluster_location
        location_id_dict = {}
        cloud_type_id_dict = {}
        cloud_type = cluster_location[0]
        cloud_location = cluster_location[1]
        location_id = cluster_location[2]
        location_id_dict[str(cloud_location)] = location_id
        location_id_dict[str(cloud_type)] = cluster_location[3]
        location_id_list.append(location_id_dict)

        #cloud_type_id_dict[str(cloud_type)] = cluster_location[3]
        #cloud_type_id_list.append(cloud_type_id_dict)
        #print location_id,'lplplplp'
        #location_id_dict[str(cloud_location)].append(location_id)
        if cloud_type in dict_location:
            #print cluster_location,"inside"

            dict_location[cloud_type].append(cluster_location[1])
        else:
            dict_location[cloud_type] = [cluster_location[1]]
            #print dict_location,"else"
    #print location_id_list,'loooooooooooooooooooooollllllllllllllll'
    #print cloud_type_id_list, 'ccccccccccccloooooooooooooooooooooollllllllllllllll'
    #print dict_location, "dciciciic"
    result_dict = {}
    end_list = []
    locations_dict = {}

    #print result_dict,"starting"
    for keys,values in dict_location.items():
        #print keys,"keyssssssss"
        #print values,"valuessssssssss"
        result_dict["cloud_type"] = keys

        #print keys,'keeeeeeeeyyyyyyyy'
        locations_list = []
        for vals in values:

            #print values,"lueeeeeeeeeeeeeeeeeeeeee"
            #print vals,"vallllllllllllllllllllllllllll"
            for dicts in location_id_list:
                #print dicts,'sssssssssssddddddddddddddddddddddiiiii'
                for key,value in dicts.items():
                    #if dicts.has_key(keys):
                    if dicts.has_key(keys):
                        #print value,'valolollol'
                        result_dict['id'] = dicts[keys]
                        #print result_dict['id'],'ressssssssssssssssss'
                    if vals == key and dicts.has_key(keys):

                        locations_dict["key"] = value
                        locations_dict["value"] = vals
                        locations_list.append(locations_dict.copy())

        result_dict["location"] = locations_list

        end_list.append(result_dict.copy())

    #print end_list, "after apendddd"
    return jsonify(end_list)

#cloudtype=Blueprint('cloudtype',__name__)
#@cloudtype.route("/cloudtype/<cloudtype>",methods=['GET'])
#def cloudType(cloudtype):
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
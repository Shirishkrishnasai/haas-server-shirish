from flask import Blueprint,jsonify
from application.models.models import TblMetaCloudLocation, TblMetaCloudType,TblClusterType
from sqlalchemy.orm import scoped_session
from application import session_factory

clusterlocation=Blueprint('clusterlocation',__name__)
@clusterlocation.route("/clusterlocation/cloudtype",methods=['GET'])
def clusterLocation():
    try :
        session = scoped_session(session_factory)
        meta_cluster_location_query = session.query(TblMetaCloudLocation.var_cloud_type,TblMetaCloudLocation.var_location,TblMetaCloudLocation.srl_id,TblClusterType.uid_cluster_type_id)\
            .filter(TblMetaCloudLocation.var_cloud_type==TblClusterType.char_name).all()
        dict_location={}
        location_id_list = []
        for cluster_location in meta_cluster_location_query:
            location_id_dict = {}
            cloud_type = cluster_location[0]
            cloud_location = cluster_location[1]
            location_id = cluster_location[2]
            location_id_dict[str(cloud_location)] = location_id
            location_id_dict[str(cloud_type)] = cluster_location[3]
            location_id_list.append(location_id_dict)


            if cloud_type in dict_location:
                dict_location[cloud_type].append(cluster_location[1])
            else:
                dict_location[cloud_type] = [cluster_location[1]]

        result_dict = {}
        end_list = []
        locations_dict = {}

        for keys,values in dict_location.items():
            result_dict["cloud_type"] = keys
            locations_list = []
            for vals in values:
                for dicts in location_id_list:
                    for key,value in dicts.items():
                        if dicts.has_key(keys):
                            result_dict['id'] = dicts[keys]
                        if vals == key and dicts.has_key(keys):

                            locations_dict["key"] = value
                            locations_dict["value"] = vals
                            locations_list.append(locations_dict.copy())

            result_dict["location"] = locations_list

            end_list.append(result_dict.copy())

        return jsonify(end_list)
    except Exception as e:
        return e.message
    finally:
        session.close()


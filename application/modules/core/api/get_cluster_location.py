from flask import Blueprint,jsonify
from application.models.models import TblMetaCloudLocation, TblClusterType
from sqlalchemy.orm import scoped_session
from application import session_factory
from application.common.loggerfile import my_logger
import os,sys

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
        for type_cloud, location_cloud in dict_location.items():
            result_dict["cloud_type"] = type_cloud
            locations_list = []
            for location_list in location_cloud:
                for location_values in location_id_list:
                    for cloud_key,cloud_value in location_values.items():
                        if location_values.has_key(type_cloud):
                            result_dict['id'] = location_values[type_cloud]
                        if location_list == cloud_key and location_values.has_key(type_cloud):
                            locations_dict["key"] = cloud_value
                            locations_dict["value"] = location_list
                            locations_list.append(locations_dict.copy())
            result_dict["location"] = locations_list
            end_list.append(result_dict.copy())
        return jsonify(end_list)
    except Exception  as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
    finally:
        session.close()


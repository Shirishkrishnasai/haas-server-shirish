from application.config.config_file import postgres_conn
from application.models.models import TblFeature, TblTaskType,TblCustomerAzureResourceGroup, \
    TblMetaRequestStatus, TblFeatureType, TblMetaNodeRoles, TblMetaTaskStatus, \
    TblMetaFeatureStatus, TblMetaMrRequestStatus, TblImage, TblMetaCloudType, \
    TblPlan, TblSize, TblPlanClusterSize, TblPlanClusterSizeConfig, TblMetaVmSize, \
    TblMetaFileUpload, TblHiveMetaStatus, TblMetaCloudLocation, TblEdgenode, TblClusterType, TblCluster, \
    TblAzureAppGateway, TblVmCreation, TblCustomer, TblVmInformation, TblAzureFileStorageCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
#lol
engine = create_engine(postgres_conn, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Uid_customer_id = 'aa182743-0aa7-11e9-ba4c-3ca9f49ab2cc'
Uid_cluster_id = 'ae945516-09bc-11e9-b4fe-000c29da5704'

cluster_feature_provision = TblFeature(char_feature_id='9',
                                       txt_worker_path='/home/database/haas-server/application/modules/cluster/workers/provision_cluster_sprint2.py')
cluster_feature_configuration = TblFeature(char_feature_id='10',
                                           txt_dependency_feature_id='9',
                                           txt_worker_path='/home/database/haas-server/application/modules/cluster/workers/configure_cluster.py')
hive_feature_provision = TblFeature(char_feature_id='11',
                                    txt_worker_path='/home/database/haas-server/application/modules/hive/workers/edgenode_provision_worker.py')

hive_feature_configuration = TblFeature(char_feature_id='12',
                                        txt_dependency_feature_id='11',
                                        txt_worker_path='/home/database/haas-server/application/modules/hive/workers/hive_config_worker.py')

# cluster related
tbl_feature_type_tbl_task_typeid_1 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T1')
tbl_feature_type_tbl_task_typeid_2 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T2')
tbl_feature_type_tbl_task_typeid_3 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T3')

tbl_feature_type_tbl_task_typeid_4 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T4')
tbl_feature_type_tbl_task_typeid_5 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T5')
tbl_feature_type_tbl_task_typeid_6 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T6')
tbl_feature_type_tbl_task_typeid_7 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T7')
tbl_feature_type_tbl_task_typeid_8 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T8')
tbl_feature_type_tbl_task_typeid_9 = TblFeatureType(char_feature_id='10',
                                                    char_task_type_id='F1_T9')
tbl_feature_type_tbl_task_typeid_10 = TblFeatureType(char_feature_id='10',
                                                     char_task_type_id='F1_T10')
tbl_feature_type_tbl_task_typeid_11 = TblFeatureType(char_feature_id='10',
                                                     char_task_type_id='F1_T11')
# hive related

tbl_feature_type_hive_typeid_1 = TblFeatureType(char_feature_id='12',
                                                char_task_type_id='F12_T1')
tbl_feature_type_hive_typeid_2 = TblFeatureType(char_feature_id='12',
                                                char_task_type_id='F12_T2')
tbl_feature_type_hive_typeid_3 = TblFeatureType(char_feature_id='12',
                                                char_task_type_id='F12_T3')
tbl_feature_type_hive_typeid_4 = TblFeatureType(char_feature_id='12',
                                                char_task_type_id='F12_T4')
tbl_feature_type_hive_typeid_5 = TblFeatureType(char_feature_id='12',
                                                char_task_type_id='F12_T5')

# meta node roles

node_role_1 = TblMetaNodeRoles(srl_id=1,
                               vm_roles='namenode')
node_role_2 = TblMetaNodeRoles(srl_id=2,
                               vm_roles='datanode')
node_role_3 = TblMetaNodeRoles(srl_id=3,
                               vm_roles='hive')
node_role_4 = TblMetaNodeRoles(srl_id=4,
                               vm_roles='spark')

meta_request_status_1 = TblMetaRequestStatus(srl_id=1,
                                             var_request_status='CREATED')
meta_request_status_2 = TblMetaRequestStatus(srl_id=2,
                                             var_request_status='ASSIGNED')
meta_request_status_3 = TblMetaRequestStatus(srl_id=3,
                                             var_request_status='RUNNING')
meta_request_status_4 = TblMetaRequestStatus(srl_id=4,
                                             var_request_status='COMPLETED')
meta_request_status_5 = TblMetaRequestStatus(srl_id=5,
                                             var_request_status='FAILED')

meta_task_status_1 = TblMetaTaskStatus(var_task_status='CREATED')
meta_task_status_2 = TblMetaTaskStatus(var_task_status='ASSIGNED')
meta_task_status_3 = TblMetaTaskStatus(var_task_status='RUNNING')
meta_task_status_4 = TblMetaTaskStatus(var_task_status='COMPLETED')
meta_task_status_5 = TblMetaTaskStatus(var_task_status='FAILED')

meta_feature_status_1 = TblMetaFeatureStatus(var_feature_status='CREATED')
meta_feature_status_2 = TblMetaFeatureStatus(var_feature_status='ASSIGNED')
meta_feature_status_3 = TblMetaFeatureStatus(var_feature_status='RUNNING')
meta_feature_status_4 = TblMetaFeatureStatus(var_feature_status='COMPLETED')
meta_feature_status_5 = TblMetaFeatureStatus(var_feature_status='FAILED')

meta_mr_request_status_1 = TblMetaMrRequestStatus(var_mr_request_status='SUBMITTED')
meta_mr_request_status_2 = TblMetaMrRequestStatus(var_mr_request_status='ACCEPTED')
meta_mr_request_status_3 = TblMetaMrRequestStatus(var_mr_request_status='RUNNING')
meta_mr_request_status_4 = TblMetaMrRequestStatus(var_mr_request_status='FINISHED')
meta_mr_request_status_5 = TblMetaMrRequestStatus(var_mr_request_status='FAILED')
meta_mr_request_status_6 = TblMetaMrRequestStatus(var_mr_request_status='KILLED')
meta_mr_request_status_7 = TblMetaMrRequestStatus(var_mr_request_status='CREATED')


# tasktypes

cluster_task_type_1 = TblTaskType(char_task_type_id='F1_T1',
                                  txt_description='copy host text file',
                                  txt_agent_worker_version_path='/opt/agent/application/modules/workers/hostdns.py',
                                  txt_agent_worker_version='1.0',
                                  int_vm_roles=1
                                  )
cluster_task_type_2 = TblTaskType(char_task_type_id='F1_T2',
                                  txt_description='copy host text file',
                                  txt_agent_worker_version_path='/opt/agent/application/modules/workers/hostdns.py',
                                  txt_agent_worker_version='1.0',
                                  int_vm_roles=2
                                  )
cluster_task_type_3 = TblTaskType(char_task_type_id='F1_T3',
                                  txt_description='slaves file',
                                  txt_agent_worker_version_path='/opt/agent/application/modules/workers/slaves.py',
                                  txt_agent_worker_version='1.0',
                                  int_vm_roles=1
                                  )
cluster_task_type_4 = TblTaskType(char_task_type_id='F1_T4',
                                  txt_description='workerconfiguration',
                                  txt_agent_worker_version_path='/opt/agent/application/modules/workers/workerconfiguration.py',
                                  txt_agent_worker_version='1.0',
                                  int_vm_roles=1
                                  )
cluster_task_type_5 = TblTaskType(char_task_type_id='F1_T5',
                                  txt_description='workerconfiguration',
                                  txt_agent_worker_version_path='/opt/agent/application/modules/workers/workerconfiguration.py',
                                  txt_agent_worker_version='1.0',
                                  int_vm_roles=2
                                  )
cluster_task_type_6 = TblTaskType(char_task_type_id='F1_T6',
                                  txt_description='ssh key scan',
                                  txt_agent_worker_version_path='/opt/scripts/sshkeyscan.ksh',
                                  txt_agent_worker_version='1.0',
                                  txt_dependency_task_id='F1_T1,F1_T3',
                                  int_vm_roles=1
                                  )
cluster_task_type_7 = TblTaskType(char_task_type_id='F1_T7',
                                  txt_description='ssh key generation',
                                  txt_agent_worker_version_path='/opt/scripts/ssh-keygen.sh',
                                  txt_agent_worker_version='1.0',
                                  int_vm_roles=1
                                  )
cluster_task_type_8 = TblTaskType(char_task_type_id='F1_T8',
                                  txt_description='ssh key copyid',
                                  txt_agent_worker_version_path='/opt/scripts/ssh-copyid.sh',
                                  txt_agent_worker_version='1.0',
                                  txt_dependency_task_id='F1_T7',
                                  int_vm_roles=1
                                  )
cluster_task_type_9 = TblTaskType(char_task_type_id='F1_T9',
                                  txt_description='hdfs format',
                                  txt_agent_worker_version_path='/opt/scripts/hdfs-format.sh',
                                  txt_agent_worker_version='1.0',
                                  txt_dependency_task_id='F1_T2,F1_T4,F1_T5,F1_T8,F1_T1',
                                  int_vm_roles=1
                                  )
cluster_task_type_10 = TblTaskType(char_task_type_id='F1_T10',
                                   txt_description='hdfs start daemon',
                                   txt_agent_worker_version_path='/opt/scripts/hdfs-daemons-start.sh',
                                   txt_agent_worker_version='1.0',
                                   txt_dependency_task_id='F1_T9',
                                   int_vm_roles=1
                                   )
cluster_task_type_11 = TblTaskType(char_task_type_id='F1_T11',
                                   txt_description='yarn daemon',
                                   txt_agent_worker_version_path='/opt/scripts/yarn-daemons-start.sh',
                                   txt_agent_worker_version='1.0',
                                   txt_dependency_task_id='F1_T10',
                                   int_vm_roles=1
                                   )
hive_task_type_1 = TblTaskType(char_task_type_id='F12_T1',
                               txt_description='hadoop-hive-integration',
                               txt_agent_worker_version_path='/opt/agent/application/modules/workers/hadoop-hive-config.py',
                               txt_agent_worker_version='1.0',
                               int_vm_roles=3
                               )
hive_task_type_2 = TblTaskType(char_task_type_id='F12_T2',
                               txt_description='hive-configuration',
                               txt_agent_worker_version_path='/opt/scripts/hive.sh',
                               txt_agent_worker_version='1.0',
                               txt_dependency_task_id='F12_T1',
                               int_vm_roles=3
                               )
hive_task_type_3 = TblTaskType(char_task_type_id='F12_T3',
                               txt_description='mysql-installation',
                               txt_agent_worker_version_path='/opt/scripts/mysql.sh',
                               txt_agent_worker_version='1.0',
                               txt_dependency_task_id='F12_T2',
                               int_vm_roles=3
                               )
hive_task_type_4 = TblTaskType(char_task_type_id='F12_T4',
                               txt_description='start-hiveServer2',
                               txt_agent_worker_version_path='/opt/scripts/start-hiveserver2.sh',
                               txt_agent_worker_version='1.0',
                               txt_dependency_task_id='F12_T3',
                               int_vm_roles=3
                               )
hive_task_type_5 = TblTaskType(char_task_type_id='F12_T5',
                               txt_description='hosts file',
                               txt_agent_worker_version_path='/opt/agent/application/modules/workers/hivehostdns.py',
                               txt_agent_worker_version='1.0',
                               int_vm_roles=3
                               )
hive_task_type_6 = TblTaskType(char_task_type_id='F12_T6',
                               txt_description='copy hiveip to namenode hosts',
                               txt_agent_worker_version_path='/opt/agent/application/modules/workers/hostdns.py',
                               txt_agent_worker_version='1.0',
                               int_vm_roles=1
                               )
hive_task_type_7 = TblTaskType(char_task_type_id='F12_T7',
                               txt_description='copy hiveip to datanode hosts',
                               txt_agent_worker_version_path='/opt/agent/application/modules/workers/hostdns.py',
                               txt_agent_worker_version='1.0',
                               int_vm_roles=2
                               )

cluster_type_1 = TblClusterType(uid_cluster_type_id='f5826f72-d135-11e8-84db-3ca9f49ab2cc',
                                char_name='azure')

tbl_image_1 = TblImage(txt_image_desc='hadoop_image',
                       var_service_name='namenode',
                       txt_image_id='/subscriptions/cfed96cf-1241-4c76-827e-785b6d5cff7c/resourceGroups/haas/providers/Microsoft.Compute/images/hadoop')

tbl_image_2 = TblImage(txt_image_desc='hadoop_image',
                       var_service_name='secondarynamenode',
                       txt_image_id='/subscriptions/cfed96cf-1241-4c76-827e-785b6d5cff7c/resourceGroups/haas/providers/Microsoft.Compute/images/hadoop')

tbl_image_3 = TblImage(txt_image_desc='hadoop_image',
                       var_service_name='datanode',
                       txt_image_id='/subscriptions/cfed96cf-1241-4c76-827e-785b6d5cff7c/resourceGroups/haas/providers/Microsoft.Compute/images/hadoop')

tbl_image_4 = TblImage(txt_image_desc='hadoop_image',
                       var_service_name='hive',
                       txt_image_id='/subscriptions/cfed96cf-1241-4c76-827e-785b6d5cff7c/resourceGroups/haas/providers/Microsoft.Compute/images/hadoop')

tbl_meta_cloud_type_1 = TblMetaCloudType(var_vm_type='Standard_B1ms',
                                         float_cpu=1,
                                         float_ram=2,
                                         float_disk_size=4,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_2 = TblMetaCloudType(var_vm_type='Standard_B1s',
                                         float_cpu=1,
                                         float_ram=1,
                                         float_disk_size=4,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_3 = TblMetaCloudType(var_vm_type='Standard_B2ms',
                                         float_cpu=2,
                                         float_ram=8,
                                         float_disk_size=16,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_4 = TblMetaCloudType(var_vm_type='Standard_B2s',
                                         float_cpu=2,
                                         float_ram=4,
                                         float_disk_size=8,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_5 = TblMetaCloudType(var_vm_type='Standard_B4ms',
                                         float_cpu=4,
                                         float_ram=16,
                                         float_disk_size=32,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_6 = TblMetaCloudType(var_vm_type='Standard_D2s_v3',
                                         float_cpu=2,
                                         float_ram=8,
                                         float_disk_size=16,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_7 = TblMetaCloudType(var_vm_type='Standard_D4s_v3',
                                         float_cpu=4,
                                         float_ram=16,
                                         float_disk_size=32,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_8 = TblMetaCloudType(var_vm_type='Standard_DS1_v2',
                                         float_cpu=1,
                                         float_ram=3.5,
                                         float_disk_size=7,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_9 = TblMetaCloudType(var_vm_type='Standard_DS2_v2',
                                         float_cpu=2,
                                         float_ram=7,
                                         float_disk_size=14,
                                         var_cloud_type='azure')

tbl_meta_cloud_type_10 = TblMetaCloudType(var_vm_type='Standard_DS3_v2',
                                          float_cpu=4,
                                          float_ram=14,
                                          float_disk_size=28,
                                          var_cloud_type='azure')

tbl_meta_cloud_type_11 = TblMetaCloudType(var_vm_type='Promo_DS2_v2',
                                          float_cpu=2,
                                          float_ram=7,
                                          float_disk_size=14,
                                          var_cloud_type='azure')

tbl_meta_cloud_type_12 = TblMetaCloudType(var_vm_type='Promo_DS3_v2',
                                          float_cpu=4,
                                          float_ram=14,
                                          float_disk_size=28,
                                          var_cloud_type='azure')

tbl_plan_1 = TblPlan(int_plan_id=1,
                     var_plan_type='silver')
tbl_plan_2 = TblPlan(int_plan_id=2,
                     var_plan_type='gold')
tbl_plan_3 = TblPlan(int_plan_id=3,
                     var_plan_type='platinum')

tbl_size_1 = TblSize(int_size_id=1,
                     var_size_type='small')
tbl_size_2 = TblSize(int_size_id=2,
                     var_size_type='medium')
tbl_size_3 = TblSize(int_size_id=3,
                     var_size_type='large')

tbl_plan_cluster_size_1 = TblPlanClusterSize(int_plan_id=1,
                                             int_size_id=1,
                                             int_nodes=2)
tbl_plan_cluster_size_2 = TblPlanClusterSize(int_plan_id=1,
                                             int_size_id=2,
                                             int_nodes=3)
tbl_plan_cluster_size_3 = TblPlanClusterSize(int_plan_id=1,
                                             int_size_id=3,
                                             int_nodes=4)
tbl_plan_cluster_size_4 = TblPlanClusterSize(int_plan_id=2,
                                             int_size_id=1,
                                             int_nodes=5)
tbl_plan_cluster_size_5 = TblPlanClusterSize(int_plan_id=2,
                                             int_size_id=2,
                                             int_nodes=6)
tbl_plan_cluster_size_6 = TblPlanClusterSize(int_plan_id=2,
                                             int_size_id=3,
                                             int_nodes=7)
tbl_plan_cluster_size_7 = TblPlanClusterSize(int_plan_id=3,
                                             int_size_id=1,
                                             int_nodes=8)
tbl_plan_cluster_size_8 = TblPlanClusterSize(int_plan_id=3,
                                             int_size_id=2,
                                             int_nodes=9)
tbl_plan_cluster_size_9 = TblPlanClusterSize(int_plan_id=3,
                                             int_size_id=3,
                                             int_nodes=10)

tbl_plan_cluster_size_config_1 = TblPlanClusterSizeConfig(int_plan_id=1,
                                                          int_size_id=1,
                                                          var_role='namenode',
                                                          int_role_count=1)

tbl_plan_cluster_size_config_2 = TblPlanClusterSizeConfig(int_plan_id=1,
                                                          int_size_id=1,
                                                          var_role='datanode',
                                                          int_role_count=3)
tbl_plan_cluster_size_config_3 = TblPlanClusterSizeConfig(int_plan_id=1,
                                                          int_size_id=2,
                                                          var_role='namenode',
                                                          int_role_count=1)
tbl_plan_cluster_size_config_4 = TblPlanClusterSizeConfig(int_plan_id=1,
                                                          int_size_id=2,
                                                          var_role='datanode',
                                                          int_role_count=3)
tbl_plan_cluster_size_config_5 = TblPlanClusterSizeConfig(int_plan_id=1,
                                                          int_size_id=3,
                                                          var_role='namenode',
                                                          int_role_count=1)
tbl_plan_cluster_size_config_6 = TblPlanClusterSizeConfig(int_plan_id=1,
                                                          int_size_id=3,
                                                          var_role='datanode',
                                                          int_role_count=3)
tbl_plan_cluster_size_config_7 = TblPlanClusterSizeConfig(int_plan_id=2,
                                                          int_size_id=1,
                                                          var_role='namenode',
                                                          int_role_count=1)
tbl_plan_cluster_size_config_8 = TblPlanClusterSizeConfig(int_plan_id=2,
                                                          int_size_id=1,
                                                          var_role='datanode',
                                                          int_role_count=4)
tbl_plan_cluster_size_config_9 = TblPlanClusterSizeConfig(int_plan_id=2,
                                                          int_size_id=2,
                                                          var_role='namenode',
                                                          int_role_count=1)
tbl_plan_cluster_size_config_10 = TblPlanClusterSizeConfig(int_plan_id=2,
                                                           int_size_id=2,
                                                           var_role='datanode',
                                                           int_role_count=5)
tbl_plan_cluster_size_config_11 = TblPlanClusterSizeConfig(int_plan_id=2,
                                                           int_size_id=3,
                                                           var_role='namenode',
                                                           int_role_count=1)
tbl_plan_cluster_size_config_12 = TblPlanClusterSizeConfig(int_plan_id=2,
                                                           int_size_id=3,
                                                           var_role='datanode',
                                                           int_role_count=6)
tbl_plan_cluster_size_config_13 = TblPlanClusterSizeConfig(int_plan_id=3,
                                                           int_size_id=1,
                                                           var_role='namenode',
                                                           int_role_count=1)
tbl_plan_cluster_size_config_14 = TblPlanClusterSizeConfig(int_plan_id=3,
                                                           int_size_id=1,
                                                           var_role='datanode',
                                                           int_role_count=7)

tbl_plan_cluster_size_config_15 = TblPlanClusterSizeConfig(int_plan_id=3,
                                                           int_size_id=2,
                                                           var_role='namenode',
                                                           int_role_count=1)

tbl_plan_cluster_size_config_16 = TblPlanClusterSizeConfig(int_plan_id=3,
                                                           int_size_id=2,
                                                           var_role='datanode',
                                                           int_role_count=8)

tbl_plan_cluster_size_config_17 = TblPlanClusterSizeConfig(int_plan_id=3,
                                                           int_size_id=3,
                                                           var_role='namenode',
                                                           int_role_count=1)

tbl_plan_cluster_size_config_18 = TblPlanClusterSizeConfig(int_plan_id=3,
                                                           int_size_id=3,
                                                           var_role='datanode',
                                                           int_role_count=9)
tbl_meta_vm_size_1 = TblMetaVmSize(int_plan_id=1,
                                   int_size_id=1,
                                   var_role='namenode',
                                   var_vm_type='Standard_DS1_v2')
tbl_meta_vm_size_2 = TblMetaVmSize(int_plan_id=1,
                                   int_size_id=1,
                                   var_role='datanode',
                                   var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_3 = TblMetaVmSize(int_plan_id=1,
                                   int_size_id=2,
                                   var_role='namenode',
                                   var_vm_type='Standard_DS1_v2')
tbl_meta_vm_size_4 = TblMetaVmSize(int_plan_id=1,
                                   int_size_id=2,
                                   var_role='datanode',
                                   var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_5 = TblMetaVmSize(int_plan_id=1,
                                   int_size_id=3,
                                   var_role='namenode',
                                   var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_6 = TblMetaVmSize(int_plan_id=1,
                                   int_size_id=3,
                                   var_role='datanode',
                                   var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_7 = TblMetaVmSize(int_plan_id=2,
                                   int_size_id=1,
                                   var_role='namenode',
                                   var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_8 = TblMetaVmSize(int_plan_id=2,
                                   int_size_id=1,
                                   var_role='datanode',
                                   var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_9 = TblMetaVmSize(int_plan_id=2,
                                   int_size_id=2,
                                   var_role='namenode',
                                   var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_10 = TblMetaVmSize(int_plan_id=2,
                                    int_size_id=2,
                                    var_role='datanode',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_11 = TblMetaVmSize(int_plan_id=2,
                                    int_size_id=3,
                                    var_role='namenode',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_12 = TblMetaVmSize(int_plan_id=2,
                                    int_size_id=3,
                                    var_role='datanode',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_13 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=1,
                                    var_role='namenode',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_14 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=1,
                                    var_role='datanode',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_15 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=2,
                                    var_role='namenode',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_16 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=2,
                                    var_role='datanode',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_17 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=3,
                                    var_role='namenode',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_18 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=3,
                                    var_role='datanode',
                                    var_vm_type='Standard_DS1_v2')
tbl_meta_vm_size_19 = TblMetaVmSize(int_plan_id=1,
                                    int_size_id=1,
                                    var_role='hive',
                                    var_vm_type='Standard_DS1_v2')

tbl_meta_vm_size_20 = TblMetaVmSize(int_plan_id=1,
                                    int_size_id=2,
                                    var_role='hive',
                                    var_vm_type='Standard_B2ms')
tbl_meta_vm_size_21 = TblMetaVmSize(int_plan_id=1,
                                    int_size_id=3,
                                    var_role='hive',
                                    var_vm_type='Standard_B2ms')
tbl_meta_vm_size_22 = TblMetaVmSize(int_plan_id=2,
                                    int_size_id=1,
                                    var_role='hive',
                                    var_vm_type='Standard_B2ms')
tbl_meta_vm_size_23 = TblMetaVmSize(int_plan_id=2,
                                    int_size_id=2,
                                    var_role='hive',
                                    var_vm_type='Standard_B2ms')
tbl_meta_vm_size_24 = TblMetaVmSize(int_plan_id=2,
                                    int_size_id=3,
                                    var_role='hive',
                                    var_vm_type='Standard_B2ms')
tbl_meta_vm_size_25 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=1,
                                    var_role='hive',
                                    var_vm_type='Standard_B2ms')
tbl_meta_vm_size_26 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=2,
                                    var_role='hive',
                                    var_vm_type='Standard_B2ms')
tbl_meta_vm_size_27 = TblMetaVmSize(int_plan_id=3,
                                    int_size_id=3,
                                    var_role='hive',
                                    var_vm_type='Standard_B2ms')

tbl_meta_file_upload_1 = TblMetaFileUpload(uid_customer_id=Uid_customer_id,
                                           var_share_name='haasfiles',
                                           var_directory_name='sampledir')

tbl_hive_meta_status_1 = TblHiveMetaStatus(srl_id=0,
                                           var_status='INITIALIZED')
tbl_hive_meta_status_2 = TblHiveMetaStatus(srl_id=1,
                                           var_status='RUNNING')
tbl_hive_meta_status_3 = TblHiveMetaStatus(srl_id=2,
                                           var_status='FINISHED')
tbl_hive_meta_status_4 = TblHiveMetaStatus(srl_id=3,
                                           var_status='CANCELED')
tbl_hive_meta_status_5 = TblHiveMetaStatus(srl_id=4,
                                           var_status='CLOSED')
tbl_hive_meta_status_6 = TblHiveMetaStatus(srl_id=5,
                                           var_status='ERROR')
tbl_hive_meta_status_7 = TblHiveMetaStatus(srl_id=6,
                                           var_status='UNKNOWN')
tbl_hive_meta_status_8 = TblHiveMetaStatus(srl_id=7,
                                           var_status='PENDING')
tbl_hive_meta_status_9 = TblHiveMetaStatus(srl_id=8,
                                           var_status='TIMEDOUT')

tbl_meta_cloud_location_1 = TblMetaCloudLocation(var_cloud_type='azure',
                                                  var_location='Central India')
tbl_meta_cloud_location_2 = TblMetaCloudLocation(var_cloud_type='azure',
                                                  var_location='South India')
tbl_meta_cloud_location_3 = TblMetaCloudLocation(var_cloud_type='azure',
                                                  var_location='West India')

# tbl_meta_cloud_location_1 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='Australia East')
#
# tbl_meta_cloud_location_2 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='Australia Southeast')
# tbl_meta_cloud_location_3 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='Brazil South')
# tbl_meta_cloud_location_4 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='Canada Central')
# tbl_meta_cloud_location_5 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='Canada East')
# tbl_meta_cloud_location_6 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='Central India')
# tbl_meta_cloud_location_7 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='Central US')
# tbl_meta_cloud_location_8 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='East Asia')
# tbl_meta_cloud_location_9 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='East US')
# tbl_meta_cloud_location_10 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='East US 2')
# tbl_meta_cloud_location_11 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='France Central')
# tbl_meta_cloud_location_12 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='Japan East')
# tbl_meta_cloud_location_13 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='Japan West')
# tbl_meta_cloud_location_14 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='Korea Central')
# tbl_meta_cloud_location_15 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='Korea South')
# tbl_meta_cloud_location_16 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='North Central US')
# tbl_meta_cloud_location_17 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='North Europe')
# tbl_meta_cloud_location_18 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='South Central US')
# tbl_meta_cloud_location_19 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='South India')
# tbl_meta_cloud_location_20 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='Southeast Asia')
# tbl_meta_cloud_location_21 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='UK South')
# tbl_meta_cloud_location_22 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='UK West')
# tbl_meta_cloud_location_23 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='West Central US')
# tbl_meta_cloud_location_24 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='West Europe')
# tbl_meta_cloud_location_25 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='West India')
# tbl_meta_cloud_location_26 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                   var_location='West US')
# tbl_meta_cloud_location_27 = TblMetaCloudLocation(var_cloud_type='azure',
#                                                  var_location='West US 2')
tbl_edgenode_1 = TblEdgenode(int_plan_id=1,
                             int_size_id=1,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)
tbl_edgenode_2 = TblEdgenode(int_plan_id=1,
                             int_size_id=2,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)
tbl_edgenode_3 = TblEdgenode(int_plan_id=1,
                             int_size_id=3,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)
tbl_edgenode_4 = TblEdgenode(int_plan_id=2,
                             int_size_id=1,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)
tbl_edgenode_5 = TblEdgenode(int_plan_id=2,
                             int_size_id=2,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)
tbl_edgenode_6 = TblEdgenode(int_plan_id=2,
                             int_size_id=3,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)
tbl_edgenode_7 = TblEdgenode(int_plan_id=3,
                             int_size_id=1,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)
tbl_edgenode_8 = TblEdgenode(int_plan_id=3,
                             int_size_id=2,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)
tbl_edgenode_9 = TblEdgenode(int_plan_id=3,
                             int_size_id=3,
                             char_feature_id=11,
                             var_role='hive',
                             int_role_count=1)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

tbl_app_gateway = TblAzureAppGateway(srl_id=1000000,
                                     uid_gateway_id="aa182744-0aa7-11e9-ba4c-3ca9f49ab2cc",
                                     var_resource_group_name="aa182742-0aa7-11e9-ba4c-3ca9f49ab2cc",

                                     txt_client_secret="iQGyjnaRDvfzGQi7z+1bZXvhRwFTDLwmNq+zX9rW3JY=",
                                     txt_app_id="5ad67325-9d85-4664-be5d-34d117f52436",
                                     txt_subscription_id="cfed96cf-1241-4c76-827e-785b6d5cff7c",
                                     txt_tenant_id="07272dbe-1df8-41bd-b29c-ae16bb7b9b83",
                                     bool_active=True,
                                     )
db_session.add(tbl_app_gateway)
tbl_cluster_1 = TblCluster(uid_cluster_id=Uid_cluster_id,
                           uid_customer_id=Uid_customer_id,
                           uid_cluster_type_id='f5826f72-d135-11e8-84db-3ca9f49ab2cc',
                           int_size_id=1,
                           char_cluster_region='South India'
                           )

tbl_vm_creation_1 = TblVmCreation(uid_cluster_id=Uid_cluster_id,
                                  uid_customer_id=Uid_customer_id,
                                  uid_agent_id='5e00f01a-0cf4-11e9-8adb-3ca9f49ab2cc',
                                  uid_vm_id='777a536a-0cf4-11e9-8adb-3ca9f49ab2cc',
                                  var_ip='192.168.100.45',
                                  bool_edge=False,
                                  )
tbl_vm_creation_2 = TblVmCreation(uid_cluster_id=Uid_cluster_id,
                                  uid_customer_id=Uid_customer_id,
                                  uid_agent_id='a9ad9568-0cf4-11e9-8adb-3ca9f49ab2cc',
                                  uid_vm_id='b50d33b4-0cf4-11e9-8adb-3ca9f49ab2cc',
                                  var_ip='192.168.100.46',
                                  bool_edge=False,
                                  )
tbl_vm_creation_3 = TblVmCreation(uid_cluster_id=Uid_cluster_id,
                                  uid_customer_id=Uid_customer_id,
                                  uid_agent_id='c7ca3772-0cf4-11e9-8adb-3ca9f49ab2cc',
                                  uid_vm_id='cdf3a62e-0cf4-11e9-8adb-3ca9f49ab2cc',
                                  var_ip='192.168.100.49',
                                  bool_edge=True,
                                  )

tbl_customer = TblCustomer(srl_id=1000000,
                           uid_customer_id=Uid_customer_id,
                           uid_gateway_id='aa182744-0aa7-11e9-ba4c-3ca9f49ab2cc',
                           txt_customer_dn='cn=customer1,ou=aa182743-0aa7-11e9-ba4c-3ca9f49ab2cc,dc=kwartile,dc=local',
                           int_plan_id=1,
                           var_name='Demo Customer',
                           int_gid_id='529'
                           )
tbl_azure_resource_group=TblCustomerAzureResourceGroup(
    uid_customer_id = Uid_customer_id,
    txt_resource_group_id = 'resource1',
    var_resource_group_name = 'resource1',
    var_created_by = 'Demouser',
    var_modified_by = 'Demouser'
)


tbl_vm_info_1 = TblVmInformation(uid_vm_id='777a536a-0cf4-11e9-8adb-3ca9f49ab2cc',
                                 macad_mac_id='FF:AE:48:E1:D5:60',
                                 uid_customer_id=Uid_customer_id,
                                 var_resource_group_name='resource1',
                                 var_virtual_network_name=None,
                                 txt_subnet_id='subnetid',
                                 txt_ip='192.168.100.45',
                                 txt_nic_name='nic1',
                                 var_user_name='sampleuser',
                                 txt_password='password')

tbl_vm_info_2 = TblVmInformation(uid_vm_id='b50d33b4-0cf4-11e9-8adb-3ca9f49ab2cc',
                                 macad_mac_id='FF:AE:48:E1:D5:60',
                                 uid_customer_id=Uid_customer_id,
                                 var_resource_group_name='resource1',
                                 var_virtual_network_name=None,
                                 txt_subnet_id='subnetid',
                                 txt_nic_name='nic1',
                                 var_user_name='sampleuser',
                                 txt_password='password',
                                 txt_ip='192.168.100.46'

                                 )
tbl_vm_info_3 = TblVmInformation(uid_vm_id='cdf3a62e-0cf4-11e9-8adb-3ca9f49ab2cc',
                                 macad_mac_id='FF:AE:48:E1:D5:60',
                                 uid_customer_id=Uid_customer_id,
                                 var_resource_group_name='resource1',
                                 var_virtual_network_name=None,
                                 txt_subnet_id='subnetid',

                                 txt_nic_name='nic1',
                                 var_user_name='sampleuser',
                                 txt_password='password',
                                 txt_ip='192.168.100.49'

                                 )


tbl_azure_credentials = TblAzureFileStorageCredentials(account_name='sbvsolutions',
                                                       account_primary_key='HLkFq07o9m9Nr/IJWXgKMiS1j5O65p1ojrpWydYEtbD7xzBBbQ95LFYoeQHOhLupzJCTUunayaIoUqiAYWv4XQ==',
                                                       account_secondary_key='9fASv4JGbIhzM03rGFb84TuYtHVVNjfIE35N54IL4rFBOlrnqGnQTUpLPRvPHWURGqmo0QyalFtrY8fBc5JBvw=='
                                                       )

#db_session.add(tbl_vm_info_1)
#db_session.add(tbl_vm_info_2)
#db_session.add(tbl_vm_info_2)
db_session.add(tbl_azure_resource_group)
db_session.add(tbl_azure_credentials)
db_session.add(tbl_customer)

#db_session.add(tbl_vm_info_1)
#db_session.add(tbl_vm_info_2)
#db_session.add(tbl_vm_info_2)

db_session.add(cluster_feature_provision)
db_session.add(cluster_feature_configuration)
db_session.add(hive_feature_provision)
db_session.add(hive_feature_configuration)
db_session.add(tbl_feature_type_tbl_task_typeid_1)
db_session.add(tbl_feature_type_tbl_task_typeid_2)
db_session.add(tbl_feature_type_tbl_task_typeid_3)
db_session.add(tbl_feature_type_tbl_task_typeid_4)
db_session.add(tbl_feature_type_tbl_task_typeid_5)
db_session.add(tbl_feature_type_tbl_task_typeid_6)
db_session.add(tbl_feature_type_tbl_task_typeid_7)
db_session.add(tbl_feature_type_tbl_task_typeid_8)
db_session.add(tbl_feature_type_tbl_task_typeid_9)
db_session.add(tbl_feature_type_tbl_task_typeid_10)
db_session.add(tbl_feature_type_tbl_task_typeid_11)
db_session.add(tbl_feature_type_hive_typeid_1)
db_session.add(tbl_feature_type_hive_typeid_2)
db_session.add(tbl_feature_type_hive_typeid_3)
db_session.add(tbl_feature_type_hive_typeid_4)
db_session.add(tbl_feature_type_hive_typeid_5)
db_session.add(node_role_1)
db_session.add(node_role_2)
db_session.add(node_role_3)
db_session.add(node_role_4)
db_session.add(meta_request_status_1)
db_session.add(meta_request_status_2)
db_session.add(meta_request_status_3)
db_session.add(meta_request_status_4)
db_session.add(meta_request_status_5)
db_session.add(meta_task_status_1)
db_session.add(meta_task_status_2)
db_session.add(meta_task_status_3)
db_session.add(meta_task_status_4)
db_session.add(meta_task_status_5)
db_session.add(meta_feature_status_1)
db_session.add(meta_feature_status_2)
db_session.add(meta_feature_status_3)
db_session.add(meta_feature_status_4)
db_session.add(meta_feature_status_5)
db_session.add(meta_mr_request_status_7)
db_session.add(meta_mr_request_status_1)
db_session.add(meta_mr_request_status_2)
db_session.add(meta_mr_request_status_3)
db_session.add(meta_mr_request_status_4)
db_session.add(meta_mr_request_status_5)
db_session.add(meta_mr_request_status_6)
db_session.add(cluster_task_type_1)
db_session.add(cluster_task_type_2)
db_session.add(cluster_task_type_3)
db_session.add(cluster_task_type_4)
db_session.add(cluster_task_type_5)
db_session.add(cluster_task_type_6)
db_session.add(cluster_task_type_7)
db_session.add(cluster_task_type_8)
db_session.add(cluster_task_type_9)
db_session.add(cluster_task_type_10)
db_session.add(cluster_task_type_11)
db_session.add(hive_task_type_1)
db_session.add(hive_task_type_2)
db_session.add(hive_task_type_3)
db_session.add(hive_task_type_4)
db_session.add(hive_task_type_5)
db_session.add(hive_task_type_6)
db_session.add(hive_task_type_7)
db_session.add(cluster_type_1)
db_session.add(tbl_image_1)
db_session.add(tbl_image_2)
db_session.add(tbl_image_3)
db_session.add(tbl_image_4)
db_session.add(tbl_meta_cloud_type_1)
db_session.add(tbl_meta_cloud_type_2)
db_session.add(tbl_meta_cloud_type_3)
db_session.add(tbl_meta_cloud_type_4)
db_session.add(tbl_meta_cloud_type_5)
db_session.add(tbl_meta_cloud_type_6)
db_session.add(tbl_meta_cloud_type_7)
db_session.add(tbl_meta_cloud_type_8)
db_session.add(tbl_meta_cloud_type_9)
db_session.add(tbl_meta_cloud_type_10)
db_session.add(tbl_meta_cloud_type_11)
db_session.add(tbl_meta_cloud_type_12)
db_session.add(tbl_plan_1)
db_session.add(tbl_plan_2)
db_session.add(tbl_plan_3)
db_session.add(tbl_size_1)
db_session.add(tbl_size_2)
db_session.add(tbl_size_3)
db_session.add(tbl_plan_cluster_size_1)
db_session.add(tbl_plan_cluster_size_2)
db_session.add(tbl_plan_cluster_size_3)
db_session.add(tbl_plan_cluster_size_4)
db_session.add(tbl_plan_cluster_size_5)
db_session.add(tbl_plan_cluster_size_6)
db_session.add(tbl_plan_cluster_size_7)
db_session.add(tbl_plan_cluster_size_8)
db_session.add(tbl_plan_cluster_size_9)
db_session.add(tbl_plan_cluster_size_config_1)
db_session.add(tbl_plan_cluster_size_config_2)
db_session.add(tbl_plan_cluster_size_config_3)
db_session.add(tbl_plan_cluster_size_config_4)
db_session.add(tbl_plan_cluster_size_config_5)
db_session.add(tbl_plan_cluster_size_config_6)
db_session.add(tbl_plan_cluster_size_config_7)
db_session.add(tbl_plan_cluster_size_config_8)
db_session.add(tbl_plan_cluster_size_config_9)
db_session.add(tbl_plan_cluster_size_config_10)
db_session.add(tbl_plan_cluster_size_config_11)
db_session.add(tbl_plan_cluster_size_config_12)
db_session.add(tbl_plan_cluster_size_config_13)
db_session.add(tbl_plan_cluster_size_config_14)
db_session.add(tbl_plan_cluster_size_config_15)
db_session.add(tbl_plan_cluster_size_config_16)
db_session.add(tbl_plan_cluster_size_config_17)
db_session.add(tbl_plan_cluster_size_config_18)
db_session.add(tbl_meta_vm_size_1)
db_session.add(tbl_meta_vm_size_2)
db_session.add(tbl_meta_vm_size_3)
db_session.add(tbl_meta_vm_size_4)
db_session.add(tbl_meta_vm_size_5)
db_session.add(tbl_meta_vm_size_6)
db_session.add(tbl_meta_vm_size_7)
db_session.add(tbl_meta_vm_size_8)
db_session.add(tbl_meta_vm_size_9)
db_session.add(tbl_meta_vm_size_10)
db_session.add(tbl_meta_vm_size_11)
db_session.add(tbl_meta_vm_size_12)
db_session.add(tbl_meta_vm_size_13)
db_session.add(tbl_meta_vm_size_14)
db_session.add(tbl_meta_vm_size_15)
db_session.add(tbl_meta_vm_size_16)
db_session.add(tbl_meta_vm_size_17)
db_session.add(tbl_meta_vm_size_18)
db_session.add(tbl_meta_vm_size_19)
db_session.add(tbl_meta_vm_size_20)
db_session.add(tbl_meta_vm_size_21)
db_session.add(tbl_meta_vm_size_22)
db_session.add(tbl_meta_vm_size_23)
db_session.add(tbl_meta_vm_size_24)
db_session.add(tbl_meta_vm_size_25)
db_session.add(tbl_meta_vm_size_26)
db_session.add(tbl_meta_vm_size_27)

db_session.add(tbl_meta_file_upload_1)
db_session.add(tbl_hive_meta_status_1)
db_session.add(tbl_hive_meta_status_2)
db_session.add(tbl_hive_meta_status_3)
db_session.add(tbl_hive_meta_status_4)
db_session.add(tbl_hive_meta_status_5)
db_session.add(tbl_hive_meta_status_6)
db_session.add(tbl_hive_meta_status_7)
db_session.add(tbl_hive_meta_status_8)
db_session.add(tbl_hive_meta_status_9)
db_session.add(tbl_meta_cloud_location_1)
db_session.add(tbl_meta_cloud_location_2)
db_session.add(tbl_meta_cloud_location_3)
# db_session.add(tbl_meta_cloud_location_4)
# db_session.add(tbl_meta_cloud_location_5)
# db_session.add(tbl_meta_cloud_location_6)
# db_session.add(tbl_meta_cloud_location_7)
# db_session.add(tbl_meta_cloud_location_8)
# db_session.add(tbl_meta_cloud_location_9)
# db_session.add(tbl_meta_cloud_location_10)
# db_session.add(tbl_meta_cloud_location_11)
# db_session.add(tbl_meta_cloud_location_12)
# db_session.add(tbl_meta_cloud_location_13)
# db_session.add(tbl_meta_cloud_location_14)
# db_session.add(tbl_meta_cloud_location_15)
# db_session.add(tbl_meta_cloud_location_16)
# db_session.add(tbl_meta_cloud_location_17)
# db_session.add(tbl_meta_cloud_location_18)
# db_session.add(tbl_meta_cloud_location_19)
# db_session.add(tbl_meta_cloud_location_20)
# db_session.add(tbl_meta_cloud_location_21)
# db_session.add(tbl_meta_cloud_location_22)
# db_session.add(tbl_meta_cloud_location_23)
# db_session.add(tbl_meta_cloud_location_24)
# db_session.add(tbl_meta_cloud_location_25)
# db_session.add(tbl_meta_cloud_location_26)
# db_session.add(tbl_meta_cloud_location_27)
db_session.add(tbl_edgenode_1)
db_session.add(tbl_edgenode_2)
db_session.add(tbl_edgenode_3)
db_session.add(tbl_edgenode_4)
db_session.add(tbl_edgenode_5)
db_session.add(tbl_edgenode_6)
db_session.add(tbl_edgenode_7)
db_session.add(tbl_edgenode_8)
db_session.add(tbl_edgenode_9)


db_session.add(tbl_cluster_1)
db_session.add(tbl_vm_creation_1)
db_session.add(tbl_vm_creation_2)
db_session.add(tbl_vm_creation_3)

db_session.flush();
db_session.commit();

import requests
import json

headers = {'Content-Type': 'application/json'}
# application.app.logger("Creating cutomer...")
url = "http://localhost:5000"


def login(username, password):
    LoginCrednetials = requests.post(url + "/api/customer/user/auth",
                                     data=json.dumps({"email": username, "password": password}),
                                     headers=headers)
    return LoginCrednetials.content


def createCustomer():
    cutomerCreation = requests.post(url + "/api/customer/register",
                                    data=json.dumps(
                                        {"first_name": "navya", "second_name": "v", "email": "navya@gmail.com",
                                         "password": "password",
                                         "location": "southindia"}), headers=headers
                                    )
    return cutomerCreation.content


def addCluster(customerId):
    data = {
        "customer_id": customerId,
        "features": [
            {"feature_id": "9", "payload": {
                "cloud_type": "1", "cluster_location": "20", "cluster_name": "Demo Cluster ForDevlopment",
                "size_id": "2"
            }}, {"feature_id": "10"}
        ]
    }
    clusterAdd = requests.post(url + "/api/addcluster", data=json.dumps(data), headers=headers)
    response = clusterAdd.content
    return response;


#customer_response = json.loads(login("navya@gmail.com", "password"))
#customer_id = customer_response['data']['customer_id']
# .data['customer_id']
#print addCluster(customer_id)

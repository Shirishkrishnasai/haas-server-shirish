import json
from sqlalchemy import BigInteger, Boolean, CHAR, Column, DateTime, ForeignKey,Float,Integer, String, Table, Text, text,create_engine,inspect,Sequence
from sqlalchemy.dialects.postgresql import INET, MACADDR, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime




db_url = 'postgres://postgres:password@192.168.100.81/haas_demo2'

engine = create_engine(db_url)

Base = declarative_base()
metadata = Base.metadata


class TblClusterType(Base):
    __tablename__ = 'tbl_cluster_type'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_cluster_type_id = Column(UUID, nullable=False, unique=True)
    char_name = Column(CHAR(20), unique=True)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)


class TblCustomer(Base):
    __tablename__ = 'tbl_customer'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(UUID, nullable=False, unique=True)
    uid_gateway_id = Column(ForeignKey(u'highgear.tbl_azure_app_gateway.uid_gateway_id'))
    txt_customer_dn = Column(Text)
    int_plan_id = Column(ForeignKey(u'highgear.tbl_plan.int_plan_id'))
    var_name = Column(String(60))
    int_gid_id = Column(Integer)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_azure_app_gateway = relationship(u'TblAzureAppGateway')
    tbl_plan=relationship(u'TblPlan')


class TblAddress(Base):
    __tablename__ = 'tbl_address'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    int_address_type_id = Column(Integer)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_address_line1 = Column(String(60))
    var_address_line2 = Column(String(60))
    var_city = Column(String(20))
    var_state = Column(String(20))
    var_country = Column(String(20))

    tbl_customer = relationship(u'TblCustomer')


class TblAddressTypes(Base):
    __tablename__ = 'tbl_address_types'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_address_type = Column(String(30))
    var_description = Column(String(30))


class TblFeature(Base):
    __tablename__ = 'tbl_feature'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    char_feature_id = Column(String(100), unique=True)
    txt_worker_path = Column(Text)
    txt_feature_version = Column(Text)
    txt_dependency_feature_id = Column(Text)

    int_feature_status = Column(Integer)
    var_provisioning_type=Column(String(5))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)


class TblKafkaTopicPurposeType(Base):
    __tablename__ = 'tbl_kafka_topic_purpose_types'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_purpose_type_id = Column(UUID, nullable=False, unique=True)
    purpose = Column(String(20))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)


class TblServerSideVersion(Base):
    __tablename__ = 'tbl_server_side_version'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    component = Column(Text)
    txt_version = Column(Text)
    txt_latest_path = Column(Text)
    ts_updated_datetime = Column(DateTime)
    bool_restart_needed = Column(Boolean)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)


class TblServerWorkersMapping(Base):
    __tablename__ = 'tbl_server_workers_mapping'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    char_feature_id = Column(CHAR(5))
    txt_description = Column(Text)
    txt_server_worker_version = Column(Text)
    var_server_worker_file_name = Column(String(25))
    txt_path = Column(Text)
    ts_version_updated_datetime = Column(DateTime)
    bool_restart_needed_on_upgrade = Column(Boolean)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)


class TblTaskType(Base):
    __tablename__ = 'tbl_task_types'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    char_task_type_id = Column(String(20), unique=True)
    int_vm_roles = Column(ForeignKey(u'highgear.tbl_meta_node_roles.srl_id'))
    txt_description = Column(Text)
    txt_agent_worker_version_path = Column(Text)
    txt_agent_worker_version = Column(Text)
    txt_dependency_task_id = Column(Text)
    arr_parameters = Column(Text)
    bool_require_payload = Column(Boolean)
    char_self_dependent_task = Column(String(100))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_meta_node_roles = relationship(u'TblMetaNodeRoles')


class TblCluster(Base):
    __tablename__ = 'tbl_cluster'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_cluster_id = Column(UUID, nullable=False, unique=True)
    txt_fqdn = Column(Text)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_cluster_type_id = Column(ForeignKey(u'highgear.tbl_cluster_type.uid_cluster_type_id'))
    var_cluster_name = Column(String(15))
    char_cluster_region = Column(CHAR(20))
    int_size_id = Column(ForeignKey(u'highgear.tbl_size.int_size_id'))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_cluster_type = relationship(u'TblClusterType')
    tbl_customer = relationship(u'TblCustomer')
    tbl_size = relationship(u'TblSize')


class TblCustomerAzureResourceGroup(Base):
    __tablename__ = 'tbl_customer_azure_resource_group'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    txt_resource_group_id = Column(Text, nullable=False)
    var_resource_group_name = Column(String(60), nullable=False, unique=True)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')


class TblFeatureType(Base):
    __tablename__ = 'tbl_feature_type'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    char_feature_id = Column(ForeignKey(u'highgear.tbl_feature.char_feature_id'))
    char_task_type_id = Column(ForeignKey(u'highgear.tbl_task_types.char_task_type_id'))
    txt_feature_type_desc = Column(Text)
    txt_role = Column(Text)
    dependent_tasks = Column(Text)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_task_types = relationship('TblTaskType')
    tbl_feature = relationship('TblFeature')


class TblKafkaConsumerGroup(Base):
    __tablename__ = 'tbl_kafka_consumer_group'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_consumer_group_id = Column(UUID, nullable=False, unique=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_consumer_group_name = Column(String(100))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')


class TblVmCreation(Base):
    __tablename__ = 'tbl_vm_creation'
    __table_args__ = {u'schema': 'highgear'}
    srl_id=Column(Integer,primary_key=True)
    uid_customer_id = Column(UUID)
    uid_cluster_id = Column(UUID)
    uid_vm_id = Column(UUID)
    uid_agent_id=Column(UUID)
    var_role = Column(String(60))
    var_ip = Column(String(100))
    var_name = Column(String(100))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

class TblCustomerRequest(Base):
    __tablename__ = 'tbl_customer_request'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_request_id = Column(UUID, nullable=False, unique=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    txt_payload_id = Column(Text)
    char_feature_id = Column(ForeignKey(u'highgear.tbl_feature.char_feature_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    ts_requested_time = Column(DateTime)
    var_request_status = Column(String(25))
    txt_dependency_request_id = Column(Text)
    var_provisioning_type=Column(String(5))
    ts_completed_time = Column(DateTime)
    txt_message = Column(Text)
    bool_assigned = Column(Boolean, default=False)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_feature = relationship(u'TblFeature')
    tbl_cluster = relationship(u'TblCluster')


class TblKafkaTopic(Base):
    __tablename__ = 'tbl_kafka_topic'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_topic_id = Column(UUID, nullable=False, unique=True)
    uid_consumer_group_id = Column(ForeignKey(u'highgear.tbl_kafka_consumer_group.uid_consumer_group_id'))
    var_topic_name = Column(String(100))
    var_topic_type = Column(String(25))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_kafka_consumer_group = relationship(u'TblKafkaConsumerGroup')


class TblVirtualNetwork(Base):
    __tablename__ = 'tbl_virtual_network'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_virtual_network_name = Column(String(100), nullable=False, unique=True)
    var_resource_group_name = Column(ForeignKey(u'highgear.tbl_customer_azure_resource_group.var_resource_group_name'))
    inet_ip_range = Column(INET)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_customer_azure_resource_group = relationship(u'TblCustomerAzureResourceGroup')


class TblKafkaPublisher(Base):
    __tablename__ = 'tbl_kafka_publishers'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    uid_topic_id = Column(ForeignKey(u'highgear.tbl_kafka_topic.uid_topic_id'))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_kafka_topic = relationship(u'TblKafkaTopic')
    tbl_agent = relationship(u'TblAgent')
    tbl_customer = relationship(u'TblCustomer')
    tbl_cluster = relationship(u'TblCluster')


class TblSubnet(Base):
    __tablename__ = 'tbl_subnet'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    txt_subnet_id = Column(Text, unique=True)
    var_virtual_network_name = Column(ForeignKey(u'highgear.tbl_virtual_network.var_virtual_network_name'))
    var_resource_group_name = Column(ForeignKey(u'highgear.tbl_customer_azure_resource_group.var_resource_group_name'))
    inet_subnet_ip_range = Column(INET)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_cluster = relationship(u'TblCluster')
    tbl_customer_azure_resource_group = relationship(u'TblCustomerAzureResourceGroup')
    tbl_virtual_network = relationship(u'TblVirtualNetwork')


class TblVmInformation(Base):
    __tablename__ = 'tbl_vm_information'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_vm_id = Column(UUID, unique=True)
    macad_mac_id = Column(MACADDR, unique=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_resource_group_name = Column(ForeignKey(u'highgear.tbl_customer_azure_resource_group.var_resource_group_name'))
    var_virtual_network_name = Column(ForeignKey(u'highgear.tbl_virtual_network.var_virtual_network_name'))
    txt_subnet_id = Column(Text)
    txt_ip = Column(Text)
    txt_nic_name = Column(Text)
    var_user_name = Column(String(100))
    txt_password = Column(Text)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_customer_azure_resource_group = relationship(u'TblCustomerAzureResourceGroup')
    tbl_virtual_network = relationship(u'TblVirtualNetwork')


class TblNodeInformation(Base):
    __tablename__ = 'tbl_node_information'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_node_id = Column(UUID, unique=True)
    uid_vm_id = Column(ForeignKey(u'highgear.tbl_vm_information.uid_vm_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    txt_fqdn = Column(Text)
    inet_dns1 = Column(INET)
    inet_dns2 = Column(INET)
    char_role = Column(String(20))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_cluster = relationship(u'TblCluster')
    tbl_vm_information = relationship(u'TblVmInformation')


class TblService(Base):
    __tablename__ = 'tbl_services'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_service_id = Column(UUID)
    char_service_name = Column(String(20))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_vm_id = Column(ForeignKey(u'highgear.tbl_vm_information.uid_vm_id'))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_vm_information = relationship(u'TblVmInformation')
    tbl_cluster = relationship(u'TblCluster')


class TblStorage(Base):
    __tablename__ = 'tbl_storage'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_vm_id = Column(ForeignKey(u'highgear.tbl_vm_information.uid_vm_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    char_storage_type = Column(String(20))
    var_capacity = Column(String(15))
    uid_disk_name = Column(UUID)
    azure_disk_type = Column(Text)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_vm_information = relationship(u'TblVmInformation')


class TblAgent(Base):
    __tablename__ = 'tbl_agent'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_agent_id = Column(UUID, unique=True)
    txt_agent_desc = Column(Text)
    uid_node_id = Column(ForeignKey(u'highgear.tbl_node_information.uid_node_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    str_agent_version = Column(String(75))
    public_ips = Column(Text)
    private_ips = Column(Text)
    bool_registered = Column(Boolean, default=False)
    ts_registered_datetime = Column(DateTime)
    ts_unregistered_datetime = Column(DateTime)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_node_information = relationship(u'TblNodeInformation')

    tbl_cluster = relationship(u'TblCluster')


class TblAgentTopicTable(Base):
    __tablename__ = 'tbl_agent_topic_table'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
    var_topic_name = Column(String(25))
    uid_purpose_type_id = Column(ForeignKey(u'highgear.tbl_kafka_topic_purpose_types.uid_purpose_type_id'))
    char_pubsub = Column(CHAR(1))
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

    tbl_agent = relationship(u'TblAgent')
    tbl_purpose_types = relationship('TblKafkaTopicPurposeType')


class TblTask(Base):
    __tablename__ = 'tbl_tasks'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_task_id = Column(UUID, unique=True)
    char_task_type_id = Column(ForeignKey(u'highgear.tbl_task_types.char_task_type_id'))
    uid_request_id = Column(UUID)
    char_feature_id = Column(ForeignKey(u'highgear.tbl_feature.char_feature_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    txt_dependent_task_id = Column(Text)
    txt_payload_id = Column(Text)
    int_task_status = Column(ForeignKey(u'highgear.tbl_meta_task_status.srl_id'))
    txt_message = Column(Text)
    txt_agent_worker_version = Column(Text)
    txt_agent_worker_version_path = Column(Text)
    var_created_by = Column(String(20))
    var_modified_by = Column(String(20))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))

    tbl_customer = relationship(u'TblCustomer')
    tbl_task_types = relationship('TblTaskType')
    tbl_agent = relationship(u'TblAgent')


class TblImage(Base):
    __tablename__ = 'tbl_image'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    txt_image_desc = Column(Text)
    var_service_name = Column(String(30))
    var_application_version = Column(String(60)),
    txt_image_id = Column(Text)
    var_linux_flavour = Column(String(60))


class TblAzureAppGateway(Base):
    __tablename__ = 'tbl_azure_app_gateway'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_gateway_id = Column(UUID, unique=True)
    var_resource_group_name = Column(ForeignKey(u'highgear.tbl_customer_azure_resource_group.var_resource_group_name'))

    txt_client_secret = Column(Text)
    txt_app_id = Column(Text)
    txt_subscription_id = Column(Text)
    txt_tenant_id = Column(Text)
    bool_active = Column(Boolean)
    ts_created_time = Column(DateTime)
    ts_updated_time = Column(DateTime)

    tbl_customer_azure_resource_group = relationship(u'TblCustomerAzureResourceGroup')



class TblUsers(Base):
    __tablename__ = 'tbl_users'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)

    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_user_name = Column(String(60),unique=True)
    txt_dn = Column(Text)
    bool_active = Column(Boolean)
    ts_created_time = Column(DateTime)
    var_created_by = Column(String(30))

    tbl_customer = relationship(u'TblCustomer')


class TblAgentStatus(Base):

     __tablename__ = 'tbl_agent_status'
     __table_args__ = {u'schema': 'highgear'}
     srl_id = Column(Integer, primary_key=True)
     uid_agent_id =  Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
     ts_heart_beat_time = Column(DateTime)
     var_created_by = Column(String(20))
     var_modified_by = Column(String(20))
     ts_created_datetime = Column(DateTime)
     ts_modified_datetime = Column(DateTime)

    tbl_agent = relationship(u'TblAgent')


class TblMetaTaskStatus(Base):
    __tablename__ = 'tbl_meta_task_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_task_status = Column(String(15))


class TblTaskStatusLog(Base):
    __tablename__ = 'tbl_task_status_log'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_task_id = Column(ForeignKey(u'highgear.tbl_tasks.uid_task_id'))
    int_meta_task_status = Column(ForeignKey(u'highgear.tbl_meta_task_status.srl_id'))
    ts_time_updated = Column(DateTime)

    tbl_tasks = relationship(u'TblTask')
    tbl_meta_task_status = relationship(u'TblMetaTaskStatus')


class TblMetaRequestStatus(Base):
    __tablename__ = 'tbl_meta_request_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_request_status = Column(String(20))


class TblMetaFeatureStatus(Base):
    __tablename__ = 'tbl_meta_feature_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_feature_status = Column(String(20))

class TblTaskRequestLog(Base):
    __tablename__ = 'tbl_task_request_log'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_request_id = Column(ForeignKey(u'highgear.tbl_customer_request.uid_request_id'))
    int_meta_request_status = Column(ForeignKey(u'highgear.tbl_meta_request_status.srl_id'))
    ts_time_updated = Column(DateTime)

    tbl_meta_request_status = relationship(u'TblMetaRequestStatus')

class TblAgentConfig(Base):
    __tablename__ = 'tbl_agent_config'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    config_entity_name = Column(String(100))
    config_entity_value = Column(String(100))
    var_created_by = Column(String(60))
    var_modified_by = Column(String(60))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

class TblMetaCloudType(Base):
    __tablename__ = 'tbl_meta_cloud_type'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    float_ram = Column(Float)
    float_disk_size = Column(Float)
    float_cpu = Column(Float)
    txt_vm_type = Column(Text)
    txt_cloud_type = Column(Text)

    tbl_customer = relationship(u'TblCustomer')
    tbl_vm_information = relationship(u'TblVmInformation')

class TblAgentConfig(Base):
    __tablename__ = 'tbl_agent_config'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    config_entity_name = Column(String(100))
    config_entity_value = Column(String(100))
    var_created_by = Column(String(60))
    var_modified_by = Column(String(60))
    ts_created_datetime = Column(DateTime)
    ts_modified_datetime = Column(DateTime)

class TblMetaNodeRoles(Base):
    __tablename__ = 'tbl_meta_node_roles'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    vm_roles = Column(String(30),unique=True)
    txt_description = Column(Text)

class TblPlan(Base):
    __tablename__ = 'tbl_plan'
    __table_args__ = {u'schema': 'highgear'}
    srl_id=Column(Integer, primary_key=True)
    int_plan_id=Column(Integer ,nullable=False,unique=True)
    var_plan_type=Column(String(50),unique=True)

class TblSize(Base):
    __tablename__ = 'tbl_size'
    __table_args__ = {u'schema': 'highgear'}
    srl_id=Column(Integer, primary_key=True)
    int_size_id=Column(Integer,unique=True)
    var_size_type=Column(String(50),unique=True)

class TblPlanClusterSize(Base):
    __tablename__ = 'tbl_plan_cluster_size'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    int_size_id=Column(ForeignKey(u'highgear.tbl_size.int_size_id'))
    int_plan_id = Column(ForeignKey(u'highgear.tbl_plan.int_plan_id'))
    int_nodes =Column(Integer)

    tbl_plan = relationship(u'TblPlan')
    tbl_size = relationship(u'TblSize')

class TblPlanClusterSizeConfig(Base):
    __tablename__ = 'tbl_plan_cluster_size_config'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    int_size_id = Column(ForeignKey(u'highgear.tbl_size.int_size_id'))
    int_plan_id = Column(ForeignKey(u'highgear.tbl_plan.int_plan_id'))
    var_role = Column(String(100))
    int_role_count= Column(Integer)

    tbl_size = relationship(u'TblSize')
    tbl_plan = relationship(u'TblPlan')

class TblMetaCloudType(Base):
    __tablename__ = 'tbl_meta_cloud_type'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    float_ram = Column(Float)
    float_disk_size = Column(Float)
    float_cpu = Column(Float)
    var_vm_type = Column(String(100),unique=True)
    var_cloud_type = Column(String(100))

    tbl_size = relationship(u'TblSize')
    tbl_plan = relationship(u'TblPlan')


class TblMetaVmSize(Base):
    __tablename__ = 'tbl_meta_vm_size'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)

    int_size_id = Column(ForeignKey(u'highgear.tbl_size.int_size_id'))
    int_plan_id = Column(ForeignKey(u'highgear.tbl_plan.int_plan_id'))
    var_role = Column(ForeignKey(u'highgear.tbl_meta_node_roles.vm_roles'))
    var_vm_type = Column(ForeignKey(u'highgear.tbl_meta_cloud_type.var_vm_type'))

    tbl_size = relationship(u'TblSize')
    tbl_plan = relationship(u'TblPlan')
    tbl_meta_node_roles = relationship(u'TblMetaNodeRoles')
    tbl_meta_cloud_type= relationship(u'TblMetaCloudType')

class TblMetaFileUpload(Base):
    __tablename__ = 'tbl_meta_file_upload'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_share_name = Column(String(60))
    var_directory_name = Column(String(60))

    tbl_customer = relationship(u'TblCustomer')

class TblFileUpload(Base):
    __tablename__ = 'tbl_file_upload'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_upload_id = Column(UUID)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
    var_share_name = Column(String(60))
    var_directory_name = Column(String(60))
    var_file_name = Column(String(60))
    var_username = Column(ForeignKey(u'highgear.tbl_users.var_user_name'))
    ts_uploaded_time = Column(DateTime)

    tbl_customer = relationship(u'TblCustomer')
    tbl_users = relationship(u'TblUsers')
    tbl_agent = relationship(u'TblAgent')



class TblFileDownload(Base):
    __tablename__ = 'tbl_file_download'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
    uid_upload_id = Column(ForeignKey(u'highgear.tbl_file_upload.uid_upload_id'))
    var_file_name = Column(String(60))
    var_username = Column(ForeignKey(u'highgear.tbl_users.var_user_name'))
    txt_file_url = Column(Text)
    ts_file_expiry_time = Column(DateTime)
    ts_requested_time = Column(DateTime)

    tbl_agent = relationship(u'TblAgent')
    tbl_users = relationship(u'TblUsers')
    tbl_file_upload = relationship(u'TblFileUpload')

class TblHiveMetaStatus(Base):
    __tablename__ = 'tbl_hive_meta_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_status = Column(String(60))



class TblHiveRequest(Base):
    __tablename__ = 'tbl_hive_request'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_hive_request_id = Column(UUID)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    var_user_name = Column(ForeignKey(u'highgear.tbl_users.var_user_name'))
    ts_requested_time = Column(DateTime)
    txt_query_string = Column(Text)
    txt_output_path = Column(Text)
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
    int_query_status = Column(ForeignKey(u'highgear.tbl_hive_meta_status.srl_id'))
    ts_status_time = Column(DateTime)
    bool_select_query = Column(Boolean)
    txt_url_value = Column(Text)
    bool_url_created = Column(Boolean)

    tbl_customer = relationship(u'TblCustomer')
    tbl_cluster = relationship(u'TblCluster')
    tbl_users = relationship(u'TblUsers')
    tbl_agent = relationship(u'TblAgent')
    tbl_hive_meta_status = relationship(u'TblHiveMetaStatus')

class TblEdgenode(Base):
    __tablename__ = 'tbl_edgenode'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    int_plan_id = Column(ForeignKey(u'highgear.tbl_plan.int_plan_id'))
    int_size_id = Column(ForeignKey(u'highgear.tbl_size.int_size_id'))
    char_feature_id = Column(ForeignKey(u'highgear.tbl_feature.char_feature_id'))
    var_role = Column(String(60))
    int_role_count = Column(Integer)



    tbl_size = relationship(u'TblSize')
    tbl_plan = relationship(u'TblPlan')
    tbl_feature = relationship(u'TblFeature')

class TblAzureFileStorageCredentials(Base):
    __tablename__ = 'tbl_azure_file_storage_credentials'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    account_name = Column(String(100))
    account_primary_key = Column(Text)
    account_secondary_key = Column(Text)







Base.metadata.create_all(bind = engine)
ins = inspect(engine)
for _t in ins.get_table_names():
    print(_t)
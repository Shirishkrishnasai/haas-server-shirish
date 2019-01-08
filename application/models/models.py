import json
from sqlalchemy.sql import func
from sqlalchemy import BigInteger, Boolean, CHAR, Column, DateTime, ForeignKey, Integer, String, Table, Text, text, create_engine, inspect, Sequence,Float
from sqlalchemy.dialects.postgresql import INET, MACADDR, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime


Base = declarative_base()

metadata = Base.metadata
class ItemBase(Base):
    __abstract__ = True
    def _ensure_defaults(self):
        for column in self.__table__.c:
            if getattr(self, column.name) is None and column.default is not None and column.default.is_scalar:
                setattr(self, column.name, column.default.arg)
                
class OutputMixin(object):
    RELATIONSHIPS_TO_DICT = False


    def __iter__(self):
        return self.to_dict().iteritems()

    def to_dict(self, rel=None, backref=None):
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        res = {column.key: getattr(self, attr)
               for attr, column in self.__mapper__.c.items()}
        if rel:
            for attr, relation in self.__mapper__.relationships.items():
                # Avoid recursive loop between to tables.
                if backref == relation.table:
                    continue
                value = getattr(self, attr)
                if value is None:
                    res[relation.key] = None
                elif isinstance(value.__class__, DeclarativeMeta):
                    res[relation.key] = value.to_dict(backref=self.__table__)
                else:
                    res[relation.key] = [i.to_dict(backref=self.__table__)
                                         for i in value]
        return res

    def to_json(self, rel=None):
        def extended_encoder(x):
            if isinstance(x, datetime):
                return x.isoformat()
            if isinstance(x, UUID):
                return str(x)

        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        return json.dumps(self.to_dict(rel), server_default=extended_encoder)


class TblClusterType(ItemBase, OutputMixin):
    __tablename__ = 'tbl_cluster_type'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_cluster_type_id = Column(UUID, nullable=False, unique=True)
    char_name = Column(CHAR(20), unique=True)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True),onupdate=func.now())


class TblCustomer(ItemBase, OutputMixin):
    __tablename__ = 'tbl_customer'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(UUID, nullable=False, unique=True)
    uid_gateway_id = Column(ForeignKey(u'highgear.tbl_azure_app_gateway.uid_gateway_id'))
    txt_customer_dn = Column(Text)
    int_plan_id = Column(ForeignKey(u'highgear.tbl_plan.int_plan_id'))
    var_name = Column(String(60))
    int_gid_id = Column(Integer)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_azure_app_gateway = relationship(u'TblAzureAppGateway')

    tbl_plan=relationship(u'TblPlan')


class TblAddress(ItemBase, OutputMixin):
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


class TblAddressTypes(ItemBase, OutputMixin):
    __tablename__ = 'tbl_address_types'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_address_type = Column(String(30))
    var_description = Column(String(30))


class TblFeature(ItemBase, OutputMixin):
    __tablename__ = 'tbl_feature'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    char_feature_id = Column(String(100), unique=True)
    txt_worker_path = Column(Text)
    txt_feature_version = Column(Text)
    txt_dependency_feature_id = Column(Text)

    int_feature_status = Column(Integer)
    var_provisioning_type=Column(String(5))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())


class TblKafkaTopicPurposeType(ItemBase, OutputMixin):
    __tablename__ = 'tbl_kafka_topic_purpose_types'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_purpose_type_id = Column(UUID, nullable=False, unique=True)
    purpose = Column(String(20))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())


class TblServerSideVersion(ItemBase, OutputMixin):
    __tablename__ = 'tbl_server_side_version'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    component = Column(Text)
    txt_version = Column(Text)
    txt_latest_path = Column(Text)
    ts_updated_datetime = Column(DateTime)
    bool_restart_needed = Column(Boolean)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())


class TblServerWorkersMapping(ItemBase, OutputMixin):
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
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())


class TblTaskType(ItemBase, OutputMixin):
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
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_meta_node_roles = relationship(u'TblMetaNodeRoles')


class TblCluster(ItemBase, OutputMixin):
    __tablename__ = 'tbl_cluster'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_cluster_id = Column(UUID, nullable=False, unique=True)
    txt_fqdn = Column(Text)
    int_size_id = Column(ForeignKey(u'highgear.tbl_size.srl_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_cluster_type_id = Column(ForeignKey(u'highgear.tbl_cluster_type.uid_cluster_type_id'))
    var_cluster_name = Column(String(15))
    char_cluster_region = Column(CHAR(20))
    int_size_id = Column(ForeignKey(u'highgear.tbl_size.int_size_id'))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    valid_cluster = Column(Boolean)


    tbl_cluster_type = relationship(u'TblClusterType')
    tbl_customer = relationship(u'TblCustomer')
    tbl_size = relationship(u'TblSize')

class TblCustomerAzureResourceGroup(ItemBase, OutputMixin):
    __tablename__ = 'tbl_customer_azure_resource_group'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    txt_resource_group_id = Column(Text, nullable=False)
    var_resource_group_name = Column(String(60), nullable=False, unique=True)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')


class TblFeatureType(ItemBase, OutputMixin):
    __tablename__ = 'tbl_feature_type'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    char_feature_id = Column(ForeignKey(u'highgear.tbl_feature.char_feature_id'))
    char_task_type_id = Column(ForeignKey(u'highgear.tbl_task_types.char_task_type_id'))
    txt_feature_type_desc = Column(Text)
    txt_role = Column(Text)
    dependent_tasks = Column(Text)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_task_types = relationship('TblTaskType')
    tbl_feature = relationship('TblFeature')

class TblMetaFileUpload(ItemBase,OutputMixin):
    __tablename__ = 'tbl_meta_file_upload'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_share_name = Column(String(60))
    var_directory_name = Column(String(60))

    tbl_customer = relationship(u'TblCustomer')

class TblKafkaConsumerGroup(ItemBase, OutputMixin):
    __tablename__ = 'tbl_kafka_consumer_group'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_consumer_group_id = Column(UUID, nullable=False, unique=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_consumer_group_name = Column(String(100))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')


class TblVmCreation(ItemBase,OutputMixin):
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
    bool_edge = Column(Boolean)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())


class TblMetaHdfsUpload(ItemBase,OutputMixin):
    __tablename__ = 'tbl_meta_hdfs_upload'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_upload_id = Column(String(50))
    txt_hdfs_file_path = Column(Text)
    uid_request_id = Column(ForeignKey(u'highgear.tbl_customer_request.uid_request_id'))

class TblFileDownload(ItemBase,OutputMixin):
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



class TblCustomerRequest(ItemBase,OutputMixin):
    __tablename__ = 'tbl_customer_request'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_request_id = Column(UUID, nullable=False, unique=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    txt_payload_id = Column(Text)
    char_feature_id = Column(ForeignKey(u'highgear.tbl_feature.char_feature_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    ts_requested_time = Column(DateTime)
    int_request_status = Column(ForeignKey(u'highgear.tbl_meta_request_status.srl_id'))
    txt_dependency_request_id = Column(Text)
    var_provisioning_type = Column(String(5))
    ts_completed_time = Column(DateTime)
    txt_message = Column(Text)
    bool_assigned = Column(Boolean, default=False)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_feature = relationship(u'TblFeature')
    tbl_cluster = relationship(u'TblCluster')
    tbl_meta_request_status = relationship(U'TblMetaRequestStatus')

class TblKafkaTopic(ItemBase, OutputMixin):
    __tablename__ = 'tbl_kafka_topic'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_topic_id = Column(UUID, nullable=False, unique=True)
    uid_consumer_group_id = Column(ForeignKey(u'highgear.tbl_kafka_consumer_group.uid_consumer_group_id'))
    var_topic_name = Column(String(100))
    var_topic_type = Column(String(25))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_kafka_consumer_group = relationship(u'TblKafkaConsumerGroup')


class TblVirtualNetwork(ItemBase, OutputMixin):
    __tablename__ = 'tbl_virtual_network'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_virtual_network_name = Column(String(100), nullable=False, unique=True)
    var_resource_group_name = Column(ForeignKey(u'highgear.tbl_customer_azure_resource_group.var_resource_group_name'))
    inet_ip_range = Column(INET)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_customer_azure_resource_group = relationship(u'TblCustomerAzureResourceGroup')


class TblKafkaPublisher(ItemBase, OutputMixin):
    __tablename__ = 'tbl_kafka_publishers'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    uid_topic_id = Column(ForeignKey(u'highgear.tbl_kafka_topic.uid_topic_id'))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_kafka_topic = relationship(u'TblKafkaTopic')
    tbl_agent = relationship(u'TblAgent')
    tbl_customer = relationship(u'TblCustomer')
    tbl_cluster = relationship(u'TblCluster')


class TblSubnet(ItemBase, OutputMixin):
    __tablename__ = 'tbl_subnet'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    txt_subnet_id = Column(Text, unique=True)
    var_virtual_network_name = Column(ForeignKey(u'highgear.tbl_virtual_network.var_virtual_network_name'))
    var_resource_group_name = Column(ForeignKey(u'highgear.tbl_customer_azure_resource_group.var_resource_group_name'))
    inet_subnet_ip_range = Column(INET)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_cluster = relationship(u'TblCluster')
    tbl_customer_azure_resource_group = relationship(u'TblCustomerAzureResourceGroup')
    tbl_virtual_network = relationship(u'TblVirtualNetwork')


class TblVmInformation(ItemBase, OutputMixin):
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
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_customer_azure_resource_group = relationship(u'TblCustomerAzureResourceGroup')
    tbl_virtual_network = relationship(u'TblVirtualNetwork')


class TblNodeInformation(ItemBase, OutputMixin):
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
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_cluster = relationship(u'TblCluster')
    tbl_vm_information = relationship(u'TblVmInformation')

class TblPlanClusterSize(ItemBase,OutputMixin):
    __tablename__ = 'tbl_plan_cluster_size'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    int_size_id=Column(ForeignKey(u'highgear.tbl_size.int_size_id'))
    int_plan_id = Column(ForeignKey(u'highgear.tbl_plan.int_plan_id'))
    int_nodes =Column(Integer)

    tbl_plan = relationship(u'TblPlan')
    tbl_size = relationship(u'TblSize')

class TblService(ItemBase, OutputMixin):
    __tablename__ = 'tbl_services'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_service_id = Column(UUID)
    char_service_name = Column(String(20))
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_vm_id = Column(ForeignKey(u'highgear.tbl_vm_information.uid_vm_id'))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_vm_information = relationship(u'TblVmInformation')
    tbl_cluster = relationship(u'TblCluster')


class TblStorage(ItemBase, OutputMixin):
    __tablename__ = 'tbl_storage'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_vm_id = Column(ForeignKey(u'highgear.tbl_vm_information.uid_vm_id'))
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    char_storage_type = Column(String(20))
    var_capacity = Column(String(15))
    uid_disk_name = Column(UUID)
    azure_disk_type = Column(Text)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_vm_information = relationship(u'TblVmInformation')


class TblAgent(ItemBase, OutputMixin):
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
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_node_information = relationship(u'TblNodeInformation')

    tbl_cluster = relationship(u'TblCluster')


class TblAgentTopicTable(ItemBase, OutputMixin):
    __tablename__ = 'tbl_agent_topic_table'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
    var_topic_name = Column(String(25))
    uid_purpose_type_id = Column(ForeignKey(u'highgear.tbl_kafka_topic_purpose_types.uid_purpose_type_id'))
    char_pubsub = Column(CHAR(1))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_agent = relationship(u'TblAgent')
    tbl_purpose_types = relationship('TblKafkaTopicPurposeType')


class TblTask(ItemBase, OutputMixin):
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
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))

    tbl_customer = relationship(u'TblCustomer')
    tbl_task_types = relationship('TblTaskType')
    tbl_agent = relationship(u'TblAgent')

class TblFileUploadTasks(ItemBase,OutputMixin):
    __tablename__ = 'tbl_file_upload_tasks'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    uid_agent_id = Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
    uid_task_id = Column(UUID)
    uid_upload_id = Column

class TblImage(ItemBase, OutputMixin):
    __tablename__ = 'tbl_image'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    txt_image_desc = Column(Text)
    var_service_name = Column(String(30))
    var_application_version = Column(String(60)),
    txt_image_id = Column(Text)
    var_linux_flavour = Column(String(60))

class TblAzureAppGateway(ItemBase, OutputMixin):
    __tablename__ = 'tbl_azure_app_gateway'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_gateway_id = Column(UUID, unique=True)
    var_resource_group_name = Column(Text)

    txt_client_secret = Column(Text)
    txt_app_id = Column(Text)
    txt_subscription_id = Column(Text)
    txt_tenant_id = Column(Text)
    bool_active = Column(Boolean)
    ts_created_time = Column(DateTime)
    ts_updated_time = Column(DateTime)




class TblMetaNodeRoles(ItemBase, OutputMixin):
    __tablename__ = 'tbl_meta_node_roles'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    vm_roles = Column(String(30),unique=True)
    txt_description = Column(Text)


class TblUsers(ItemBase, OutputMixin):
    __tablename__ = 'tbl_users'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)

    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_user_name = Column(String(60),unique=True)
    txt_dn = Column(Text)
    bool_active = Column(Boolean)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

    tbl_customer = relationship(u'TblCustomer')

class TblTaskStatusLog(ItemBase, OutputMixin):
    __tablename__ = 'tbl_task_status_log'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_task_id = Column(ForeignKey(u'highgear.tbl_tasks.uid_task_id'))
    int_meta_task_status = Column(ForeignKey(u'highgear.tbl_meta_task_status.srl_id'))
    ts_time_updated = Column(DateTime)

    tbl_tasks = relationship(u'TblTask')
    tbl_meta_task_status = relationship(u'TblMetaTaskStatus')

class TblAgentStatus(ItemBase,OutputMixin):
     __tablename__ = 'tbl_agent_status'
     __table_args__ = {u'schema': 'highgear'}
     srl_id = Column(Integer, primary_key=True)
     uid_agent_id =  Column(ForeignKey(u'highgear.tbl_agent.uid_agent_id'))
     ts_heart_beat_time = Column(DateTime)
     var_created_by = Column(String(20), server_default="system")
     var_modified_by = Column(String(20), server_default="system")
     ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
     ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())

     tbl_agent = relationship(u'TblAgent')


class TblMetaTaskStatus(ItemBase, OutputMixin):
    __tablename__ = 'tbl_meta_task_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_task_status = Column(String(15))



class TblMetaRequestStatus(ItemBase, OutputMixin):
    __tablename__ = 'tbl_meta_request_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_request_status = Column(String(20))


class TblTaskRequestLog(ItemBase, OutputMixin):
    __tablename__ = 'tbl_task_request_log'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_request_id = Column(ForeignKey(u'highgear.tbl_customer_request.uid_request_id'))
    int_meta_request_status = Column(ForeignKey(u'highgear.tbl_meta_request_status.srl_id'))
    ts_time_updated = Column(DateTime)

    tbl_meta_request_status = relationship(u'TblMetaRequestStatus')
    tbl_customer_request = relationship(u'TblCustomerRequest')

class TblMetaFeatureStatus(Base):
    __tablename__ = 'tbl_meta_feature_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_feature_status = Column(String(20))


class TblAgentConfig(Base):
    __tablename__ = 'tbl_agent_config'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    config_entity_name = Column(String(100))
    config_entity_value = Column(String(100))
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())


class TblPlan(Base):
    __tablename__ = 'tbl_plan'
    __table_args__ = {u'schema': 'highgear'}
    srl_id=Column(Integer, primary_key=True)
    int_plan_id=Column(Integer ,nullable=False,unique=True)
    var_plan_type=Column(String(50),unique=True)

class TblSize(ItemBase,OutputMixin):
    __tablename__ = 'tbl_size'
    __table_args__ = {u'schema': 'highgear'}
    srl_id=Column(Integer, primary_key=True)
    int_size_id=Column(Integer,unique=True)
    var_size_type=Column(String(50),unique=True)

class TblMetaCloudType(ItemBase,OutputMixin):
    __tablename__ = 'tbl_meta_cloud_type'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    float_ram = Column(Float)
    float_disk_size = Column(Float)
    float_cpu = Column(Float)
    var_vm_type = Column(String(100),unique=True)
    var_cloud_type = Column(String(100))



class TblMetaVmSize(ItemBase,OutputMixin):
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

class TblCustomerJobRequest(ItemBase,OutputMixin):
    __tablename__ = 'tbl_customer_job_request'
    __table_args__ = {u'schema': 'highgear'}

    srl_id = Column(Integer, primary_key=True)
    uid_request_id = Column(UUID, nullable=False, unique=True)
    uid_customer_id = Column(ForeignKey(u'highgear.tbl_customer.uid_customer_id'))
    var_user_name = Column(ForeignKey(u'highgear.tbl_users.var_user_name'))
    txt_payload_id = Column(Text)
    uid_cluster_id = Column(ForeignKey(u'highgear.tbl_cluster.uid_cluster_id'))
    uid_conf_upload_id = Column(UUID)
    uid_jar_upload_id = Column(UUID)
    var_job_name = Column(String(100))
    txt_job_description = Column(Text)
    var_input_file_path = Column(String(200))
    var_output_file_path = Column(String(200))
    ts_requested_time = Column(DateTime)
    int_request_status = Column(Integer,default=7)
    var_application_id=Column(String(100))
    var_job_diagnostics=Column(Text)
    conf_mapred_job_tracker=Column(String(50))
    conf_mapreduce_framework_name = Column(String(50))
    conf_mapreduce_task_io_sort_mb = Column(Integer)
    conf_mapreduce_task_io_sort_factor= Column(Integer)
    conf_mapreduce_map_sort_spill_percent = Column(Float)
    conf_mapreduce_job_maps = Column(Integer)
    conf_mapreduce_job_reduces = Column(Integer)
    conf_output_compress = Column(Boolean)
    ts_completed_time = Column(DateTime)
    txt_message = Column(Text)
    bool_assigned = Column(Boolean, default=False)
    var_created_by = Column(String(20), server_default="system")
    var_modified_by = Column(String(20), server_default="system")
    ts_created_datetime = Column(DateTime(timezone=True), server_default=func.now())
    ts_modified_datetime = Column(DateTime(timezone=True), server_onupdate=func.now())

    tbl_customer = relationship(u'TblCustomer')
    tbl_cluster = relationship(u'TblCluster')
    tbl_users = relationship(u'TblUsers')


class TblHiveRequest(ItemBase,OutputMixin):
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

class TblHiveMetaStatus(ItemBase,OutputMixin):
    __tablename__ = 'tbl_hive_meta_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_status = Column(String(60))

class TblAzureFileStorageCredentials(ItemBase,OutputMixin):
    __tablename__ = 'tbl_azure_file_storage_credentials'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    account_name = Column(String(100))
    account_primary_key = Column(Text)
    account_secondary_key = Column(Text)

class TblEdgenode(ItemBase,OutputMixin):
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


class TblFileUpload(ItemBase,OutputMixin):
    __tablename__ = 'tbl_file_upload'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    uid_upload_id = Column(UUID,unique=True)
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


class TblMetaMrRequestStatus(ItemBase,OutputMixin):
    __tablename__ = 'tbl_meta_mr_request_status'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_mr_request_status = Column(String(15))

class TblMetaCloudLocation(ItemBase,OutputMixin):
    __tablename__ = 'tbl_meta_cloud_location'
    __table_args__ = {u'schema': 'highgear'}
    srl_id = Column(Integer, primary_key=True)
    var_cloud_type = Column(String(40))
    var_location = Column(Text)


#Drop table tbl_feature_status meta table
import uuid
import time
from sqlalchemy import func
from flask import request,jsonify,Blueprint
from azure.mgmt.network import NetworkManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from application.config.config_file import application_id,customer_client_id,secret_code,tenant_id,subscription_id,resource
from application.modules.azure.create_ldap_customer import azureldapcustomer
from azure.mgmt.resource import ResourceManagementClient
from application.models.models import TblCustomer,TblCustomerAzureResourceGroup,TblVirtualNetwork,TblAzureAppGateway,TblSubnet,TblClusterType
from application import db
from application.common.loggerfile import my_logger
from azure.mgmt.network.models import NetworkSecurityGroup
from azure.mgmt.network.models import SecurityRule,SecurityRuleProtocol,SecurityRuleAccess,SecurityRuleDirection
customers=Blueprint('customers', __name__)
@customers.route("/api/customer/register",methods=['POST'])
def customercreation():

    #Gathering information of customer and retriving configuration data of azure
#    try:
    customer_content=request.json
    #print customer_content
    display_name = customer_content['first_name']
    #print display_name

    user_principal_name = customer_content['first_name'] + '@bhaskarhighgear.onmicrosoft.com'
    password = customer_content['password']
    mail_nickname = customer_content['second_name']
    customer_content = request.json
    LOCATION = customer_content['location']
    GROUP_NAME=str(uuid.uuid1())
    customer_id=str(uuid.uuid1())
    customer_email=customer_content['email']
    #Connection to postgres and inserting customer details to database


    gateway_id=str(uuid.uuid1())
    resourcegroup_id=uuid.uuid1()

    insert_customer_details_first = TblCustomer(uid_customer_id=customer_id)
    db.session.add(insert_customer_details_first)
    db.session.commit()

    insert_into_app_gateway_first = TblAzureAppGateway(uid_gateway_id=gateway_id)
    db.session.add(insert_into_app_gateway_first)
    db.session.commit()

    insert_resource_group = TblCustomerAzureResourceGroup(uid_customer_id=customer_id,
                                                          var_resource_group_name=GROUP_NAME,
                                                          txt_resource_group_id=resourcegroup_id)
    db.session.add(insert_resource_group)
    db.session.commit()

    #insert_resource_group_first = TblCustomerAzureResourceGroup(var_resource_group_name=GROUP_NAME)
    #db.session.add(insert_resource_group_first)
    #db.session.commit()

    #insert_customer_details = TblCustomer(uid_customer_id=customer_id, uid_gateway_id=gateway_id)
    #db.session.add(insert_customer_details)
    #db.session.commit()

    db.session.query(TblCustomer).filter(TblCustomer.uid_customer_id==customer_id).update({"uid_gateway_id":gateway_id})

    #db.session.add(insert_customer_details)
    db.session.commit()

    #insert_resource_group = TblCustomerAzureResourceGroup(uid_customer_id=customer_id, var_resource_group_name=GROUP_NAME,txt_resource_group_id=resourcegroup_id)
    #db.session.add(insert_resource_group)
    #db.session.commit()


#    insert_into_app_gateway = TblAzureAppGateway(txt_app_id=application_id, txt_subscription_id=subscription_id,var_resource_group_name=GROUP_NAME, txt_tenant_id=tenant_id,txt_client_secret=secret_code, uid_gateway_id=gateway_id)
#    db.session.add(insert_into_app_gateway)
#    db.session.commit()

    db.session.query(TblAzureAppGateway).filter(TblAzureAppGateway.uid_gateway_id==gateway_id).update({"txt_app_id":application_id, "txt_subscription_id":subscription_id,
                                                 "var_resource_group_name":GROUP_NAME, "txt_tenant_id":tenant_id,
                                                 "txt_client_secret":secret_code})
    #db.session.add(insert_into_app_gateway)
    db.session.commit()

    customer_gid_query=db.session.query(func.max(TblCustomer.int_gid_id))
    customer_gid_id=customer_gid_query[0][0]
    #Adding customer to ldap
    azureldapcustomer(customer_id,display_name,customer_gid_id,user_principal_name,mail_nickname,customer_email,password)
    #Resource group creation


    my_logger.debug('Create Resource Group')
    credentials = ServicePrincipalCredentials(
       client_id=customer_client_id,
       secret=secret_code,
       tenant=tenant_id)

    client_login = ResourceManagementClient(credentials, subscription_id)
    resource_group_creation=client_login.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})
    #Virtual Network creation


    virtual_network_id_query=db.session.query(func.max(TblVirtualNetwork.srl_id)).all()
    virtual_network_ip_info=db.session.query(TblVirtualNetwork.inet_ip_range).filter(TblVirtualNetwork.srl_id==virtual_network_id_query[0][0]).all()
    print virtual_network_ip_info[0][0],"info"
    if virtual_network_ip_info[0][0] == None:
        print "into if"
        vn_ip = "10.0.0.0/24"
    else:
        ip_of_previous_cluster = virtual_network_ip_info[0][0]
        print ip_of_previous_cluster
        splitting_vn_ip = ip_of_previous_cluster.split('.')
        splitting_vn_ip_range=splitting_vn_ip[2]
        ip_value = int(splitting_vn_ip_range) + 1
        vn_ip = "10.0." + str(ip_value)+".0/24"

    VNET_NAME=str(uuid.uuid1())
    network_client = NetworkManagementClient(credentials, subscription_id)
    vnet_creation = network_client.virtual_networks.create_or_update(GROUP_NAME,VNET_NAME,{'location': LOCATION,'address_space': {'address_prefixes': [vn_ip]}})
    vnet_creation.wait()
    insert_virtual_network=TblVirtualNetwork(uid_customer_id=customer_id,var_virtual_network_name=VNET_NAME,var_resource_group_name=GROUP_NAME,inet_ip_range=vn_ip)
    db.session.add(insert_virtual_network)
    db.session.commit()

    #Creating subnet
    NSG_NAME = 'nsg' + str(int(round(time.time() * 1000)))
    security_rule = SecurityRule(protocol=SecurityRuleProtocol.tcp, source_address_prefix='*',
                         description='Test security rule', name="Security" + NSG_NAME,
                         source_port_range='*', destination_port_range="50070", priority=200,
                         destination_address_prefix='*', access=SecurityRuleAccess.allow,
                         direction=SecurityRuleDirection.inbound)


    security_rule1 = SecurityRule(protocol=SecurityRuleProtocol.tcp, source_address_prefix='*',
                         description='Test security rule', name="Security1" + NSG_NAME,
                         source_port_range='*', destination_port_range="22", priority=199,
                         destination_address_prefix='*', access=SecurityRuleAccess.allow,
                         direction=SecurityRuleDirection.inbound)

    NSG = network_client.network_security_groups.create_or_update(GROUP_NAME,
                                                          NSG_NAME,
                                                          NetworkSecurityGroup(location=LOCATION,
                                                                               security_rules=[security_rule,security_rule1]))
    NSG.wait()
    nsg_result = NSG.result()
    print "NSG", nsg_result
    subnet_ip=vn_ip
    SUBNET_NAME = 'snet'+str(int(round(time.time() * 1000)))
    my_logger.debug('\nCreate Subnet')
    subnet_creation = network_client.subnets.create_or_update(GROUP_NAME,VNET_NAME,SUBNET_NAME,{'address_prefix': subnet_ip, 'network_security_group':nsg_result})
    subnet_info = subnet_creation.result()
    subnet_id=subnet_info.id
    print subnet_id
    insert_subnet=TblSubnet(uid_customer_id=customer_id,txt_subnet_id=subnet_id,inet_subnet_ip_range=subnet_ip,var_resource_group_name=GROUP_NAME,var_virtual_network_name=VNET_NAME)
    db.session.add(insert_subnet)
    db.session.commit()


    return jsonify(customer_first_name=display_name,customer_last_name=mail_nickname,customer_password=password,customer_id=customer_id)
    #    except Exception as e:
    #        return e.message

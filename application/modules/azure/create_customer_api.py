import uuid
import time
from xml.etree.ElementTree import ParseError

from application import session_factory
from msrestazure.azure_exceptions import CloudError
from sqlalchemy import func
from flask import request, jsonify, Blueprint
from azure.mgmt.network import NetworkManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from application.config.config_file import application_id, customer_client_id, secret_code, tenant_id, subscription_id,
from application.modules.azure.create_ldap_customer import azureldapcustomer
from azure.mgmt.resource import ResourceManagementClient
from application.models.models import TblCustomer, TblCustomerAzureResourceGroup, TblVirtualNetwork, TblAzureAppGateway, \
    TblSubnet, TblClusterType,TblMetaCloudLocation, TblUsers
from application.common.loggerfile import my_logger
from azure.mgmt.network.models import NetworkSecurityGroup
from azure.mgmt.network.models import SecurityRule, SecurityRuleProtocol, SecurityRuleAccess, SecurityRuleDirection
from sqlalchemy.orm import scoped_session

customers = Blueprint('customers', __name__)
@customers.route("/api/customer/register", methods=['POST'])
def customercreation():
    # Gathering information of customer and retriving configuration data of azure
    try:
        db_session = scoped_session(session_factory)
        customer_content = request.json
        display_name = customer_content['first_name']
        plan_id = customer_content['cluster_plan']
        user_principal_name = customer_content['first_name'] + '@bhaskarhighgear.onmicrosoft.com'
        password = customer_content['password']
        mail_nickname = customer_content['second_name']
        customer_content = request.json
        locate = customer_content['location']
        print customer_content
        location = db_session.query(TblMetaCloudLocation.var_location).filter(TblMetaCloudLocation.srl_id == locate).all()
        location = location[0][0]
        GROUP_NAME = str(uuid.uuid1())
        customer_id = GROUP_NAME
        customer_email = customer_content['email']
        user_name = db_session.query(TblUsers.var_user_name).filter(TblUsers.var_user_name==customer_email).all()
        # print user_name[0]
        print user_name
        if user_name != []:
            return jsonify(message="Mail id already exist")
        else :
            # Connection to postgres and inserting customer details to database
            gateway_id = str(uuid.uuid1())
            resourcegroup_id = GROUP_NAME
            #inserting plan id and customer id into customer table and committing into customer table

            insert_customer_details_first = TblCustomer(uid_customer_id=customer_id,
                                                        int_plan_id = plan_id)
            db_session.add(insert_customer_details_first)
            db_session.commit()

            insert_into_app_gateway_first = TblAzureAppGateway(uid_gateway_id=gateway_id)
            db_session.add(insert_into_app_gateway_first)
            db_session.commit()

            insert_resource_group = TblCustomerAzureResourceGroup(uid_customer_id=customer_id,
                                                                  var_resource_group_name=GROUP_NAME,
                                                                  txt_resource_group_id=resourcegroup_id)
            db_session.add(insert_resource_group)
            db_session.commit()

            # insert_resource_group_first = TblCustomerAzureResourceGroup(var_resource_group_name=GROUP_NAME)
            # db.session.add(insert_resource_group_first)
            # db.session.commit()

            # insert_customer_details = TblCustomer(uid_customer_id=customer_id, uid_gateway_id=gateway_id)
            # db.session.add(insert_customer_details)
            # db.session.commit()

            db_session.query(TblCustomer).filter(TblCustomer.uid_customer_id == customer_id).update(
                {"uid_gateway_id": gateway_id})

            # db.session.add(insert_customer_details)
            db_session.commit()

            # insert_resource_group = TblCustomerAzureResourceGroup(uid_customer_id=customer_id, var_resource_group_name=GROUP_NAME,txt_resource_group_id=resourcegroup_id)
            # db.session.add(insert_resource_group)
            # db.session.commit()

            #    insert_into_app_gateway = TblAzureAppGateway(txt_app_id=application_id, txt_subscription_id=subscription_id,var_resource_group_name=GROUP_NAME, txt_tenant_id=tenant_id,txt_client_secret=secret_code, uid_gateway_id=gateway_id)
            #    db.session.add(insert_into_app_gateway)
            #    db.session.commit()

            db_session.query(TblAzureAppGateway).filter(TblAzureAppGateway.uid_gateway_id == gateway_id).update(
                {"txt_app_id": application_id, "txt_subscription_id": subscription_id,
                 "var_resource_group_name": GROUP_NAME, "txt_tenant_id": tenant_id,
                 "txt_client_secret": secret_code})
            # db.session.add(insert_into_app_gateway)
            db_session.commit()

            customer_gid_query = db_session.query(func.max(TblCustomer.int_gid_id))
            customer_gid_id = customer_gid_query[0][0]
            # Adding customer to ldap
            azureldapcustomer(customer_id, display_name, customer_gid_id, user_principal_name, mail_nickname, customer_email,
                              password)
            # Resource group creation

            my_logger.debug('Create Resource Group')
            credentials = ServicePrincipalCredentials(
                client_id=customer_client_id,
                secret=secret_code,
                tenant=tenant_id)

            client_login = ResourceManagementClient(credentials, subscription_id)
            resource_group_creation = client_login.resource_groups.create_or_update(GROUP_NAME, {'location': location})
            # Virtual Network creation

            virtual_network_id_query = db_session.query(func.max(TblVirtualNetwork.srl_id)).all()
            virtual_network_ip_info = db_session.query(TblVirtualNetwork.inet_ip_range).filter(
                TblVirtualNetwork.srl_id == virtual_network_id_query[0][0]).all()
            if len(virtual_network_ip_info) == 0:
                # if virtual_network_ip_info[0][0] == None:
                vn_ip = "10.0.0.0/24"
            else:
                ip_of_previous_cluster = virtual_network_ip_info[0][0]
                my_logger.debug(ip_of_previous_cluster)
                splitting_vn_ip = ip_of_previous_cluster.split('.')
                splitting_vn_ip_range = splitting_vn_ip[2]
                ip_value = int(splitting_vn_ip_range) + 1
                vn_ip = "10.0." + str(ip_value) + ".0/24"

            VNET_NAME = str(uuid.uuid1())
            network_client = NetworkManagementClient(credentials, subscription_id)
            vnet_creation = network_client.virtual_networks.create_or_update(GROUP_NAME, VNET_NAME, {'location': location,
                                                                                                     'address_space': {
                                                                                                         'address_prefixes': [
                                                                                                             vn_ip]}})
            vnet_creation.wait()
            insert_virtual_network = TblVirtualNetwork(uid_customer_id=customer_id, var_virtual_network_name=VNET_NAME,
                                                       var_resource_group_name=GROUP_NAME, inet_ip_range=vn_ip)
            db_session.add(insert_virtual_network)
            db_session.commit()

            # Creating subnet
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

            security_rule2 = SecurityRule(protocol=SecurityRuleProtocol.tcp, source_address_prefix='*',
                                          description='Test security rule', name="Security2" + NSG_NAME,
                                          source_port_range='*', destination_port_range="445", priority=198,
                                          destination_address_prefix='*', access=SecurityRuleAccess.allow,
                                          direction=SecurityRuleDirection.inbound)

            NSG = network_client.network_security_groups.create_or_update(GROUP_NAME,
                                                                          NSG_NAME,
                                                                          NetworkSecurityGroup(location=location,
                                                                                               security_rules=[security_rule,
                                                                                                               security_rule1,security_rule2]))
            NSG.wait()
            nsg_result = NSG.result()
            my_logger.debug(nsg_result)
            subnet_ip = vn_ip
            SUBNET_NAME = 'snet' + str(int(round(time.time() * 1000)))
            my_logger.debug('\nCreate Subnet')
            subnet_creation = network_client.subnets.create_or_update(GROUP_NAME, VNET_NAME, SUBNET_NAME,
                                                                      {'address_prefix': subnet_ip,
                                                                       'network_security_group': nsg_result})
            subnet_info = subnet_creation.result()
            subnet_id = subnet_info.id
            my_logger.debug(subnet_id)
            insert_subnet = TblSubnet(uid_customer_id=customer_id, txt_subnet_id=subnet_id, inet_subnet_ip_range=subnet_ip,
                                      var_resource_group_name=GROUP_NAME, var_virtual_network_name=VNET_NAME)
            db_session.add(insert_subnet)
            db_session.commit()

            return jsonify(customer_first_name=display_name, customer_last_name=mail_nickname, customer_password=password,
                           customer_id=customer_id,successmessage="Successfully registered")
    except ParseError as e:
        my_logger.debug(e)
        return jsonify(message=e,err_code=500)
    # except psycopg2.DatabaseError as e:
    #     my_logger.error(e.pgerror)
    #     return jsonify(message=e,err_code=500)
    # except psycopg2.OperationalError as e:
    #     my_logger.error(e.pgerror)
    #     return jsonify(message=e,err_code=500)
    except CloudError as e:
        my_logger.error(e.clouderror)
        return jsonify(message=e,err_code=500)
    except Exception as e:
        my_logger.error(e)
        return jsonify(message=e,err_code=500)
    finally:
        db_session.close()


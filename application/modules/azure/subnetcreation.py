import time
import uuid

import psycopg2
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from flask import Flask
from flask import request
from application.common.loggerfile import my_logger

app = Flask(__name__)
@app.route('/res',methods=['POST'])
def resource():
   content = request.json
   my_logger.info(content)
   # LOCATION = 'centralindia'
   LOCATION = content['LOCATION']
   # Resource Group
   GROUP_NAME = content['COMPANY_NAME']

   VNET_NAME=content['COMPANY_NAME']
   tenant_id='07272dbe-1df8-41bd-b29c-ae16bb7b9b83'
   id=uuid.uuid1()
   customer_id=str(id)
   application_id='5ad67325-9d85-4664-be5d-34d117f52436'
   subscription_id='cfed96cf-1241-4c76-827e-785b6d5cff7c'
   haas_plan_id=content['plan_id']
   customer_name=content['customername']
   srl_id='3'
   conn = psycopg2.connect(host="192.168.100.108", user="postgres", password="password", dbname="haas")
   cur = conn.cursor()
   statement = "insert into tbl_customer (srl_id,var_str_azure_tenant_id,uid_customer_id,var_application_id,var_azure_subscription_id,lng_haas_plan_id,var_name,var_group_name) values('%s','%s','%s','%s','%s','%s','%s','%s')"
   query = cur.execute("set search_path to highgear;")
   query1 = cur.execute(statement % (str(srl_id),tenant_id,customer_id,application_id,subscription_id,haas_plan_id,customer_name,GROUP_NAME))




   subscription_id = 'cfed96cf-1241-4c76-827e-785b6d5cff7c'
   credentials = ServicePrincipalCredentials(
   client_id = '5ad67325-9d85-4664-be5d-34d117f52436',
   secret = 'iQGyjnaRDvfzGQi7z+1bZXvhRwFTDLwmNq+zX9rW3JY=',
   tenant = '07272dbe-1df8-41bd-b29c-ae16bb7b9b83')


   resource_client = ResourceManagementClient(credentials, subscription_id)


   my_logger.info('Create Resource Group')
   resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})

   #create nic(GROUP_NAME,VNET_NAME,LOCATION)




def create_nic():

          #LOCATION = 'centralindia

   subscription_id = 'cfed96cf-1241-4c76-827e-785b6d5cff7c'
   credentials = ServicePrincipalCredentials(
        client_id = '5ad67325-9d85-4664-be5d-34d117f52436',
        secret = 'iQGyjnaRDvfzGQi7z+1bZXvhRwFTDLwmNq+zX9rW3JY=',
        tenant = '07272dbe-1df8-41bd-b29c-ae16bb7b9b83')
   network_client = NetworkManagementClient(credentials, subscription_id)
    # Create VNet
   my_logger.info('Create Vnet')
   ip='10.0.0.0/16'
   async_vnet_creation = network_client.virtual_networks.create_or_update(
      GROUP_NAME,
           VNET_NAME,
           {
               'location': LOCATION,
               'address_space': {
                   'address_prefixes': [ip]
                }
            }
        )
   async_vnet_creation.wait()








def create_subnet(customer_id):
   cluster_id='56dcb242-ac28-11e8-b56b-3ca9f49ab2cc'

   #content = request.json
   #my_logger.info(content)

     #   GROUP_NAME = content['GROUP_NAME']

        # Network
      #  VNET_NAME = content['VNET_NAME']
   GROUP_NAME='haas'
   VNET_NAME='haas'
   conn = psycopg2.connect(host="192.168.100.108", user="postgres", password="password", dbname="haas")
   cur = conn.cursor()
   statement = "select max(srl_id) from tbl_subnet where uid_cluster_id='%s';"
   query=cur.execute("set search_path to highgear;")

   query2=cur.execute(statement % cluster_id)
   result=cur.fetchall()
   srl_id=result[0][0]
   statement1="select inet_subnet_ip_range from tbl_subnet where srl_id='%d';"
   query3=cur.execute(statement1 % srl_id)
   result1=cur.fetchall()
   ip_of_previous_cluster=result1[0][0]
   splitting=ip_of_previous_cluster.split('.')
   value=int(splitting[2])
   value=value+1
   ip="10.3."+str(value)+".0/24"
   my_logger.info(ip)


   SUBNET_NAME = 'snet'+str(int(round(time.time() * 1000)))
   LOCATION = 'centralindia'
        #LOCATION = content['LOCATION']

   subscription_id = 'cfed96cf-1241-4c76-827e-785b6d5cff7c'
   credentials = ServicePrincipalCredentials(
        client_id = '5ad67325-9d85-4664-be5d-34d117f52436',
        secret = 'iQGyjnaRDvfzGQi7z+1bZXvhRwFTDLwmNq+zX9rW3JY=',
        tenant = '07272dbe-1df8-41bd-b29c-ae16bb7b9b83')
   network_client = NetworkManagementClient(credentials, subscription_id)


   # Create Subnet
   my_logger.info('Create Subnet')
   async_subnet_creation = network_client.subnets.create_or_update(
      GROUP_NAME,
              VNET_NAME,
              SUBNET_NAME,
              {'address_prefix': ip}
       )
   subnet_info = async_subnet_creation.result()
   subnet_id=subnet_info.id
   my_logger.info(subnet_id)
#   srl_id=int(srl_id)+1
   my_logger.info(type(SUBNET_NAME))
   my_logger.info(type(ip))
   cur.execute("set search_path to highgear;")
   statement2 = "insert into tbl_subnet (lng_customer_id,uid_cluster_id,inet_subnet_ip_range,txt_subnet_name,txt_subnet_id) values('%d','%s','%s','%s','%s')"
   my_logger.info("statement")
   cur.execute(statement2 % (customer_id,cluster_id,ip,SUBNET_NAME,subnet_id))
   my_logger.info("execution")
   conn.commit()
   return subnet_id


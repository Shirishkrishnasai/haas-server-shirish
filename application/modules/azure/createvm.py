import time
import datetime
import uuid
import base64
from sqlalchemy import and_
from sqlalchemy.orm import scoped_session
from application import session_factory
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from msrestazure.azure_exceptions import CloudError
from application.models.models import TblSubnet,TblVmInformation,TblVmCreation,TblImage,TblCustomer,TblPlanClusterSizeConfig,TblMetaVmSize
from application.config.config_file import application_id, customer_client_id, secret_code, tenant_id

USERNAME = 'sample-user'
PASSWORD = 'Sample@123'


def get_credentials():
    subscription_id='cfed96cf-1241-4c76-827e-785b6d5cff7c'
    credentials = ServicePrincipalCredentials(
        client_id=customer_client_id,
        secret=secret_code,
        tenant=tenant_id)

    return credentials, subscription_id


def vmcreation(required_data_list):
    failed_data_list=[]

    print "CAlling VmCreation"
    db_session = scoped_session(session_factory)
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)

    print len(required_data_list)


    for data in required_data_list:
        try:

            IP_NAME = 'pip' + str(int(round(time.time() * 1000)))
            VM_NAME = 'vm-' + str(int(round(time.time() * 1000)))
            NIC_NAME = 'nic' + str(int(round(time.time() * 1000)))
            IP_CONFIG_NAME = 'ip-config' + str(int(round(time.time() * 1000)))
            OS_DISK_NAME = 'osdisk' + str(int(round(time.time() * 1000)))
            date_time = datetime.datetime.now()
            created_by = "system"
            modified_by = "system"
            clusterid=data[0]
            customerid=data[1]

            agentid = data[2]
            role=data[3]
            LOCATION = data[4]
            size_id=data[5]
            plan_id = data[6]
            print customerid,role,'i am role',"-----------"



            print plan_id
            print size_id


            subnet_info = db_session.query(TblSubnet.txt_subnet_id , TblSubnet.var_virtual_network_name, \
                                      TblSubnet.var_resource_group_name).filter(TblSubnet.uid_customer_id == customerid).all()

            subnet_id = subnet_info[0][0]
            GROUP_NAME = subnet_info[0][2]
            vnet_name = subnet_info[0][1]
            print subnet_id,'i am subnet'

            image_info = db_session.query(TblImage.txt_image_id).filter(TblImage.var_service_name == role).all()
            print "heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",role

            print image_info
            image_id=image_info[0][0]
            print image_id



            vm_size_info=db_session.query(TblMetaVmSize.var_vm_type).filter(and_(TblMetaVmSize.int_plan_id == plan_id,
                                                                                 TblMetaVmSize.int_size_id == size_id,
                                                                                 TblMetaVmSize.var_role==role)).all()


            vm_size_info=db_session.query(TblMetaVmSize.var_vm_type).filter(and_(TblMetaVmSize.int_plan_id == plan_id ,TblMetaVmSize.int_size_id == size_id ,TblMetaVmSize.var_role==role))
            print vm_size_info
            vm_size=vm_size_info[0][0]
            print vm_size

            vm_information = {}
            vm_information['name'] = 'vm-' + str(int(round(time.time() * 1000)))
            vm_information['vm_id'] = uuid.uuid1()
            vm_information['vm_ip'] = "10.0.0.3"
            vm_information['role'] = role
            if True:
                return vm_information
#            subnet_id = '/subscriptions/cfed96cf-1241-4c76-827e-785b6d5cff7c/resourceGroups/haas/providers/Microsoft.Network/virtualNetworks/haas/subnets/SUB1539665969989'
            tobestring = """#cloud-config
    write_files:
    -   content: |        
            {{"customer_id":"{customerid}","cluster_id":"{clusterid}","role":"{role}","agent_id":"{agentid}","agent_version":"1.0"}}
        owner: hadoop:hadoop
        path: /opt/agent/agent_info.txt""".format(customerid=customerid, clusterid=clusterid, role=role, agentid=agentid)
            encoded = base64.b64encode(tobestring)

            # create NIC
            if role == "namenode":
                nic = create_nic_namenode(network_client, subnet_id, GROUP_NAME, IP_NAME, LOCATION, IP_CONFIG_NAME,
                                          NIC_NAME)
            else:
                nic = create_nic(network_client, subnet_id, GROUP_NAME, NIC_NAME, LOCATION, IP_CONFIG_NAME)

            # Create Linux VM
            print('\nCreating Linux Virtual Machine')
            vm_parameters = create_vm_parameters(encoded, nic.id, OS_DISK_NAME, LOCATION,image_id,vm_size)
            async_vm_creation = compute_client.virtual_machines.create_or_update(
                GROUP_NAME, VM_NAME, vm_parameters)

            vm_result = async_vm_creation.wait(0)

            print vm_result,async_vm_creation
            time.sleep(5)


            # Get the virtual machine by name
            print('\nGet Virtual Machine by Name')
            virtual_machine = compute_client.virtual_machines.get(
                GROUP_NAME,
                VM_NAME

            )
            print virtual_machine
            print virtual_machine.os_profile,'os_profffffffffffffffilllle'

            time.sleep(5)
            private_ip = network_client.network_interfaces.get(GROUP_NAME, NIC_NAME).ip_configurations[0].private_ip_address
            print private_ip
            time.sleep(5)
            vm_information['vm_ip'] = private_ip
            vm_information['name'] = virtual_machine.name
            vm_information['vm_id'] = virtual_machine.vm_id
            vm_information['role'] = role
            print vm_information,'hiii'

            vm_information_insert=TblVmInformation(uid_vm_id = virtual_machine.vm_id,
                                                    uid_customer_id =customerid,
                                                    var_resource_group_name = GROUP_NAME,
                                                    var_virtual_network_name =vnet_name,
                                                    txt_subnet_id = subnet_id,
                                                    txt_ip =private_ip,
                                                    txt_nic_name = NIC_NAME,
                                                    var_user_name = USERNAME,
                                                    txt_password = PASSWORD,
                                                    var_created_by =created_by,
                                                    var_modified_by = modified_by,
                                                    ts_created_datetime =date_time,
                                                    ts_modified_datetime =date_time )
            db_session.add(vm_information_insert)

            db_session.commit()

            if role == 'namenode' or role == 'datanode' or role == 'resourcemanager':
                edge = 'f'
            else:
                edge = 't'

            vm_creation_insert=TblVmCreation(uid_customer_id =customerid,
                                uid_cluster_id = clusterid,
                                uid_agent_id=agentid,
                                var_role =role,
                                var_name =virtual_machine.name,
                                uid_vm_id=virtual_machine.vm_id,
                                var_ip = private_ip,
                                bool_edge = edge,
                                var_created_by = created_by,
                                var_modified_by = modified_by,
                                ts_created_datetime =date_time,
                                ts_modified_datetime = date_time)
            db_session.add(vm_creation_insert)
            db_session.commit()

        #return "success"

        except CloudError as ce:
            failed_data_list.append(data)
            print('A VM operation failed:')
            print(ce.__str__())
        except Exception as e:

            print e.__str__()

        else:
            print('All example operations completed successfully!')

        finally:
            if len(failed_data_list)>=1:
                vmcreation(failed_data_list)
            print('\nfinal')







def create_nic_namenode(network_client, subnet_id, GROUP_NAME, IP_NAME, LOCATION, IP_CONFIG_NAME, NIC_NAME):
    """Create a Network Interface for a VM
    """
    async_public_ip_creation = network_client.public_ip_addresses.create_or_update(
        GROUP_NAME,
        IP_NAME,
        {
            'location': LOCATION,
            'public_ip_allocation_method': 'Dynamic',
            'idle_timeout_in_minutes': 4,
        }
    )
    public_ip = async_public_ip_creation.result()
    public_ip_id = public_ip.id
    print
    public_ip

    # Create NIC
    print('\nCreate NIC with ')
    print(
        "Nic Name:", NIC_NAME, "Location:", LOCATION, "ipconfigName:", IP_CONFIG_NAME, "SubnetId", subnet_id,
        "publc ipid",
        public_ip_id)

    async_nic_creation = network_client.network_interfaces.create_or_update(
        GROUP_NAME,
        NIC_NAME,
        {'name': NIC_NAME,
         'location': LOCATION,
         'ip_configurations': [
             {
                 'name': IP_CONFIG_NAME,
                 'subnet': {
                     'id': subnet_id
                 },

                 'public_ip_address': {
                     'id': public_ip_id}

             }
         ]
         }
    )
    print  async_nic_creation
    return async_nic_creation.result()


def create_nic(network_client, subnet_id, GROUP_NAME, NIC_NAME, LOCATION, IP_CONFIG_NAME):
    print('\nCreate NIC',GROUP_NAME,NIC_NAME,LOCATION,IP_CONFIG_NAME)
    async_nic_creation = network_client.network_interfaces.create_or_update(
        GROUP_NAME,
        NIC_NAME,
        {'name': NIC_NAME,
         'location': LOCATION,
         'ip_configurations': [
             {
                 'name': IP_CONFIG_NAME,
                 'subnet': {
                     'id': subnet_id
                 },

             }
         ]
         }
    )
    print async_nic_creation
    return async_nic_creation.result(0)
   # return async_nic_creation.result()


def create_vm_parameters(encoded, nic_id, OS_DISK_NAME, LOCATION,image_id,vm_size):

    print image_id,'in  parameters'
    return {
        'location': LOCATION,
        'os_profile': {
            'computer_name': 'vm-' + str(int(round(time.time() * 1000))),
            'admin_username': USERNAME,
            'admin_password': PASSWORD,
            'custom_data': encoded
        },
        'hardware_profile': {
            'vm_size': vm_size
        },
        'storage_profile': {
            'image_reference': {
                "id": image_id
                 },
            'osDisk': {
                'caching': 'ReadWrite',
                'managedDisk': {
                    'storageAccountType': 'Standard_LRS'
                },
                'name': OS_DISK_NAME,
                'createOption': 'FromImage'
            }
        },

        'network_profile': {
            'network_interfaces': [{
                'id': nic_id,
            }]
        }

    }
    print 'out of parameters'
# for i in range(0,5):
#print __file__,__name__
#if __name__=="__main__"   :
    #vmcreation([["9a1ada8b-c888-11e8-bace-000c29b9b7fd","9a1ada8b-c888-11e8-bace-000c29b9b7fa","namenode","9a1ada8b-c888-11e8-bace-000c29b9b7fc","south india",1],["9a1ada8b-c888-11e8-bace-000c29b9b7fd","9a1ada8b-c888-11e8-bace-000c29b9b7fa","datanode","9a1ada8b-c888-11e8-bace-000c29b9b7fc","south india",1]])



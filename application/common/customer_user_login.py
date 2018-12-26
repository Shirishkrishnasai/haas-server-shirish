from azure.graphrbac import GraphRbacManagementClient
from azure.common.credentials import UserPassCredentials
from azure.mgmt.authorization import AuthorizationManagementClient

# See above for details on creating different types of AAD credentials
credentials = UserPassCredentials(
    'leonia2@bhaskarhighgear.onmicrosoft.com',
    'password@123',

)
print (credentials)


schema_statement="set search_path to highgear;"
request_status=5
assigned_status=1
client_id='5ad67325-9d85-4664-be5d-34d117f52436'
secret='iQGyjnaRDvfzGQi7z+1bZXvhRwFTDLwmNq+zX9rW3JY='
tenant='07272dbe-1df8-41bd-b29c-ae16bb7b9b83'
resource="https://graph.windows.net"
ldap_connection ="ldap://52.172.28.18:389"
ldap_connection_dn="cn=admin,dc=kwartile,dc=local"
ldap_connection_password="password"
application_id='5ad67325-9d85-4664-be5d-34d117f52436'
customer_client_id='5ad67325-9d85-4664-be5d-34d117f52436'
secret_code ='iQGyjnaRDvfzGQi7z+1bZXvhRwFTDLwmNq+zX9rW3JY='
tenant_id='07272dbe-1df8-41bd-b29c-ae16bb7b9b83'
subscription_id='cfed96cf-1241-4c76-827e-785b6d5cff7c'
kafka_bootstrap_server = ['52.172.28.18:9092']
kafka_api_version = (0, 10, 1)

file_upload_url="http://104.211.222.41:5000/fileupload"
path="/opt/mapred-site.xml"


#postgres_conn = 'postgres://postgres:password@104.211.222.41/haas_demo2'
conn_string = "host='92.168.100.81' user='postgres' password='password' dbname='haas_demo3'"
postgres_conn = 'postgres://postgres:password@192.168.100.81/haas_demo3'

SQLALCHEMY_DATABASE_URI = 'postgres://postgres:password@192.168.100.81/haas_demo3'
mongo_conn_string="mongodb://192.168.100.81:27017"
sqlite_string= "/opt/agent/haas"
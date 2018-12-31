
import json
import argparse
import subprocess
import datetime
import os
import re
import urllib
import time

_endpoint_pg_root = "/flow/process-groups/root"
_endpoint_pg_id = "/flow/process-groups/"
_endpoint_connection_id = "/connections/"
_endpoint_processor_id = "/processors/"
_endpoint_token = "nifi-api/access/token"
_endpoint_client="/flow/client-id"
_endpoint_bulletins = "/flow/bulletin-board"
_endpoint_cluster = "/controller/cluster"
_endpoint_node = "/controller/cluster/nodes/"
_endpoint_flow_status = "/flow/status"


def getToken( url ):
	endpoint = url + _endpoint_token
	data = urllib.urlencode({"username":"hadoop", "password":"password"})
	p = subprocess.Popen("curl -k -X POST " + endpoint + " -H 'application/x-www-form-urlencoded' --data \"" + data + "\"",
							shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	token, err = p.communicate()
	print token
	#print token, err
	endpoint_cli=url+_endpoint_client
	if p.returncode == 0:
		curl = "curl -k " + endpoint_cli + " -H 'Authorization: Bearer " + token + "'"
		process=subprocess.Popen(curl, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout = process.communicate()[0]
		print 'STDOUT:{}'.format(stdout)

	else:
		print "Failed to get token"
		print err
		print out
		return None

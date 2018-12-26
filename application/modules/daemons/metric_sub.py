import pymongo
mongo_conn_string="mongodb://192.168.100.108:27017"

data={
 	"event_type": "metrics",
 	"time":"1537961010001",
 	"customer_id": "60938a80-bcc3-11e8-a355-529269fb1452",
 	"cluster_id": "60938a80-bcc3-11e8-a355-529269fb1452",
 	"agent_id": "60938a80-bcc3-11e8-a355-529269fb1453",
 	"payload": [{
 			"metric_name": "ram",
 			"metric_value": 123,
 			"base_value": 0,
			"measured_in":"bytes"
 		},
		{
 			"metric_name": "cpu",
 			"metric_value": 0.44,
 			"base_value": 0,
			"measured_in":"percentage"
 		},
 		{
 			"metric_name": "disk",
 			"disk_read": 1234,
 			"disk_write": 12,
			"measured_in":"bytes"
 		},
		{
 			"metric_name": "network",
 			"data_in": 192,
 			"data_out": 0,
			"measured_in":"bytes"
 		},
		{
			"metric_name":"storage",
			"available_storage":1234,
			"measured_in":"bytes"

		}
 	]

 }
def metricSubscriber(data):
	try:
		customerid=data['customer_id']
		print customerid
		mongo_db_conn=pymongo.MongoClient(mongo_conn_string)
		database_conn=mongo_db_conn['local']
		db_collection=database_conn[customerid]

		result=db_collection.insert_one(data)
		print result
		#query_statement= database_conn.find(dat
        #object_id=query_statement[0]["_id"]
        #print object_id

	except pymongo.errors.ConnectionFailure, e:
		my_logger.debug(e)
		return jsonify(message='unable to connect mongo')

metricSubscriber(data)

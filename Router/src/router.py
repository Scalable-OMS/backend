# make db connection - MongoDB
# for the requested date, get the document data
# for each city get the orderids and
# for each of the order id, get the user data
# get the outlet address for those cities
# for each of those orders in the city get distances from the warehouse
# create a distance matrix and use a naive travelling salesman problem and get the route
# store the route in mongoDB document for that date

import pika
import os
from pymongo import MongoClient
import mysql.connector
import json
import requests


######### MongoDB ###########

m_uri = "mongodb://{host}:{port}/{dbname}".format(
	host=os.getenv("mongodb_host"), 
	port=os.getenv("mongodb_port"), 
	dbname=os.getenv("mongodb")
)
client = MongoClient(m_uri)
mongodb = client.routesDB

######### END - MongoDB ###########

######### MYSQL ###########

mysqldb = mysql.connector.connect(
  host=os.getenv("mysql_host"),
  user=os.getenv("mysql_username"),
  password=os.getenv("mysql_password"),
  database=os.getenv("mysql_database")
)

def getOrdersByDate(deliveryDate):
	try:
		sqlcursor =  mysqldb.cursor()
		sqlcursor.execute("SELECT * FROM orders o, users u WHERE o.customerId=u.customerId AND o.deliveryDate={date}".format(date=deliveryDate))
		result = sqlcursor.fetchall()
		print("orders response")
		for x in result:
			print(x)
		return result
	except Exception as e:
		print(e)
	finally:
		sqlcursor.close()

def getWarehouseLocations():
	try:
		sqlcursor =  mysqldb.cursor()
		sqlcursor.execute("SELECT * FROM warehouses")
		result = sqlcursor.fetchall()
		print("wareshouses response")
		for x in result:
			print(x)
		return result
	except Exception as e:
		print(e)
	finally:
		sqlcursor.close()

######### END - MYSQL ###########

def getRequestUrls(cityOrders, warehouseLocations):
	addressDelimiter = "|"
	requestUris = []
	for city in cityOrders.keys():
		addresses = ""
		warehouseAddress = warehouseLocations[city]['address']
		addresses += warehouseAddress + addressDelimiter
		for order in cityOrders[city]:
			orderAddress = order["orderAddress"]
			addresses += orderAddress + addressDelimiter
		uri = """https://maps.googleapis.com/maps/api/distancematrix/json?
		destinations={addresses}&origins={addresses}&units=imperial&key={google_api_key}"""\
		.format(
			addresses=addresses,
			google_api_key=os.getenv("google_api_key")
		)
		requestUris.append({"uri": uri, "city": city})
	print("All google api requests")
	print(requestUris)
	return requestUris




# google api response will be in the same order as passed in the request
# if the request was like origin=["address1", "address2", "address3"], destinations=["address1", "address2", "address3"]
# response will have a list of object where the first object will be the distance between origin_address1 and destination_address1, 
# origin_address1 and destination_address2 etc..

# how to create a matrix of address, challenge is to maintain the order
# because google returns only the physical address and there is no way 
# to identify which was the warehouse and which are the ordered locations.
# Solution: we can create a hashmap which will store the hash of the address
# and the index corresponding to that address, later we can use that index to create a matrix
# address_index = hashmap.get(address), using the address index, we create the matrix
def routeOrders(ch, method, properties, body):
	req_body = json.loads(body.decode('utf-8'))
	deliveryDate = req_body['deliveryDate']
	orders = getOrdersByDate(deliveryDate)
	warehouseLocations = getWarehouseLocations()
	warehouseLocationsMap = {}
	for warehouse in warehouseLocations:
		warehouse_city = warehouse["city"]
		if warehouse_city not in warehouseLocationsMap:
			warehouseLocationsMap[warehouse_city] = { }
		warehouseLocationsMap[warehouse_city]['address'] = warehouse["address"]

	cityDistanceMatrixMap = {}
	cityOrdersMap = {}
	for order in orders:
		order_city = order['city']
		if order_city not in cityOrdersMap:
			cityOrdersMap[order_city] = []

		cityOrdersMap[order_city].append({
			"orderId": order["orderId"],
			"city": order_city,
			"orderAddress": order["address"]
		})
	requestsUrls = getRequestUrls(cityOrdersMap, warehouseLocationsMap)
	for request_uri in requestsUrls:
		response = requests.get(request_uri['uri'])
		address_list = response['origin_addresses']
		city = request_uri['city']
		# creating a 2-d empty distance matrix
		origin_index = 0
		destination_index = 0
		tempDistanceMatrix = [[0]*len(address_list)]*len(address_list)
		for origin_distance_details in response["rows"]:
			for origin_destination_dist in origin_distance_details['elements']:
				tempDistanceMatrix[origin_index][destination_index] = origin_destination_dist["distance"]["value"]
				# for each of the destination from the origin we update the matrix
				# destinations as column in the matrix
				destination_index += 1
			# origin as row in the matrix
			origin_index += 1
		cityDistanceMatrixMap[city] = tempDistanceMatrix
	# now we have the distance matrix of all the cities
	# all we need to do now is run the travelling salesman problem on each of these matrices



######### RabbitMQ connection ###########
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "rabbitmq"
rabbitMQ = pika.BlockingConnection(
	pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toSortingWorker')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
rabbitMQChannel.basic_consume(queue='toSortingWorker', on_message_callback=routeOrders, auto_ack=False)
rabbitMQChannel.start_consuming()

######### END - RabbitMQ connection ###########
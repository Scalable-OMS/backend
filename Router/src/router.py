# make db connection - MongoDB
# for the requested date, get the document data
# for each city get the orderids and
# for each of the order id, get the user data
# get the outlet address for those cities
# for each of those orders in the city get distances from the warehouse
# create a distance matrix and use a naive travelling salesman problem and get the route
# store the route in mongoDB document for that date
from math import *
from Router.src import config
import pika
import pymongo
import mysql.connector
import json
import sys
import config as c


######### MongoDB ###########
user = c.config['mongo_user']
password = c.config['mongo_password']
mongodb = c.config['mongodb']
host = c.config['mongo_host']
connection_url = f"mongodb+srv://{user}:{password}@{host}/gameMeta?retryWrites=true&w=majority".\
	format(user, password, host)
client = pymongo.MongoClient(connection_url)
db = client.oms
routes = db['routes']
######### END - MongoDB ###########

######### MYSQL ###########
mysqldb = mysql.connector.connect(
	host=c.config['mysql_host'],
	user=c.config['mysql_username'],
	password=c.config['mysql_password'],
	database=c.config['mysql_dbname']
)

def getOrdersByDateAndCity(deliveryDate, cities):
	try:
		sqlcursor =  mysqldb.cursor()
		query = f"SELECT * FROM orders o, users u WHERE o.userId=u.id AND o.deliveryDate=\'{deliveryDate}\' AND u.city in ({cities})"
		print(query)
		sqlcursor.execute(query)
		result = sqlcursor.fetchall()
		return result
	except Exception as e:
		print(e)
	finally:
		sqlcursor.close()

def getOrdersByDate(deliveryDate):
	try:
		sqlcursor =  mysqldb.cursor()
		query = f"SELECT * FROM orders o, users u WHERE o.userId=u.id AND o.deliveryDate=\'{deliveryDate}\'"
		sqlcursor.execute(query)
		result = sqlcursor.fetchall()
		return result
	except Exception as e:
		print(e)
	finally:
		sqlcursor.close()


def getCoordinatesForAddress(customerId):
	try:
		sqlcursor = mysqldb.cursor()
		sqlcursor.execute("SELECT lat, lng FROM orders o, users u WHERE o.userId=u.id AND u.id={customerId}".format(
			customerId=customerId))
		result = sqlcursor.fetchall()
		for x in result:
			return str(x[0]) + "," + str(x[1])
	except Exception as e:
		print(e)
	finally:
		sqlcursor.close()


def getWarehouseLocations():
	try:
		sqlcursor =  mysqldb.cursor()
		sqlcursor.execute("SELECT * FROM warehouses")
		result = sqlcursor.fetchall()
		return result
	except Exception as e:
		print(e)
	finally:
		sqlcursor.close()
######### END - MYSQL ###########

# def getRequestUrls(cityOrders, warehouseLocations):
# 	addressDelimiter = "|"
# 	requestUris = []
# 	for city in cityOrders.keys():
# 		addresses = ""
# 		warehouseAddress = warehouseLocations[city]['address']
# 		addresses += warehouseAddress + addressDelimiter
# 		for order in cityOrders[city]:
# 			orderAddress = order["orderAddress"]
# 			addresses += orderAddress + addressDelimiter
# 		uri = """https://maps.googleapis.com/maps/api/distancematrix/json?
# 		destinations={addresses}&origins={addresses}&units=imperial&key={google_api_key}""" \
# 			.format(
# 			addresses=addresses,
# 			google_api_key=os.getenv("google_api_key")
# 		)
# 		requestUris.append({"uri": uri, "city": city})
# 	return requestUris

######## DISTANCE CALCULATION UTILS ########
def getDistanceBetweenOrders(cityOrders, warehouseLocations):
	city_distance_map = {}
	city_orders_indexing = {}

	for city in cityOrders.keys():
		city_addresses = []
		if city not in warehouseLocations:
			return city_distance_map
		warehouse = warehouseLocations[city]['coordinates']
		city_addresses.append(warehouse)
		orders = cityOrders[city]
		index = 1
		if city not in city_orders_indexing:
			# including the warehouse location with the number of ordered locations, hence the + 1
			city_orders_indexing[city] = [0 for _ in range(len(orders) + 1)]
			city_orders_indexing[city][0] = "warehouseLocation"
		for order in orders:
			order_address = getCoordinatesForAddress(order["customerId"])
			city_addresses.append(order_address)
			city_orders_indexing[city][index] = {"orderId": order["orderId"], "deliveryAddress": order['orderAddress']}
			index += 1
		city_distance_map[city] = getDistanceMatrix(city_addresses)

	return city_distance_map, city_orders_indexing


def getDistanceMatrix(addresses):
	distance_matrix = [[0 for _ in range(len(addresses))] for _ in range(len(addresses))]

	for i in range(len(addresses)):
		for j in range(len(addresses)):
			distance_matrix[i][j] = round(getDistance(addresses[i], addresses[j]), 3)
	return distance_matrix

def getDistance(coord1, coord2):
	x = coord1.split(",")
	x1, x2 = float(x[0].strip()), float(x[1].strip())
	y = coord2.split(",")
	y1, y2 = float(y[0].strip()), float(y[1].strip())

	lon1 = radians(x2)
	lon2 = radians(y2)
	lat1 = radians(x1)
	lat2 = radians(y1)

	# Haversine formula
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

	c = 2 * asin(sqrt(a))

	# Radius of earth in kilometers. Use 3956 for miles
	r = 6371

	# calculate the result
	return (c * r)

# split the matrix into multiple matrices of 100 deliveries in each
# so that a driver assigned to a city will have to delivery atmost 100 orders per day
def findShortestPathFromWH(matrix):
	if len(matrix) < 100:
		numberOfDivisions = 1
	else:
		numberOfDivisions = int(len(matrix) / 100)
		if len(matrix) - (numberOfDivisions * 100) > 0:
			numberOfDivisions += 1

	currentDivision = 1
	paths = {}
	source = 0
	visited = [source]
	divisionPath = [source]
	currentVertex = source
	numberOfLocationsCovered = 1
	while currentDivision <= numberOfDivisions or numberOfLocationsCovered == len(matrix):
		unvisitedNeighbours = [i for i in range(len(matrix[currentVertex])) if i not in visited]
		leastDistance = sys.maxsize
		nearestNeighbour = -1
		for i in unvisitedNeighbours:
			if matrix[currentVertex][i] < leastDistance:
				leastDistance = matrix[currentVertex][i]
				nearestNeighbour = i
		visited.append(nearestNeighbour)
		divisionPath.append(nearestNeighbour)
		currentVertex = nearestNeighbour
		numberOfLocationsCovered += 1
		if (numberOfLocationsCovered + 1) % 100 == 0:
			paths["path_{division}".format(division=currentDivision)] = divisionPath
			currentDivision += 1
			divisionPath = []
			divisionPath = [source]
			currentVertex = source
	return paths
######## DISTANCE CALCULATION UTILS ########


######## ORDER ROUTING ########
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
	######## Testing variables ########
	# deliveryDate = body['deliveryDate']
	# cities = body['cities']
	# orders = getOrdersByDateAndCity(deliveryDate, cities)
	# print(len(orders))
	###################################
	orders = getOrdersByDate(deliveryDate)
	warehouseLocations = getWarehouseLocations()
	warehouseLocationsMap = {}
	for warehouse in warehouseLocations:
		warehouse_city = warehouse[1]
		if warehouse_city not in warehouseLocationsMap:
			warehouseLocationsMap[warehouse_city] = { }
		warehouseLocationsMap[warehouse_city]['address'] = warehouse[2]
		warehouseLocationsMap[warehouse_city]['coordinates'] = warehouse[3]
		warehouseLocationsMap[warehouse_city]['warehouseId'] = warehouse[0]

	cityOrdersMap = {}
	for order in orders:
		order_city = order[11]
		if order_city not in cityOrdersMap:
			cityOrdersMap[order_city] = []

		cityOrdersMap[order_city].append({
			"orderId": order[0],
			"city": order_city,
			"orderAddress": order[10],
			"customerId": order[2]
		})
	print(cityOrdersMap.keys())
	cityDistanceMatrixMap, city_orders_indexing = getDistanceBetweenOrders(cityOrdersMap, warehouseLocationsMap)
	city_delivery_routes = {}
	for city in cityDistanceMatrixMap.keys():
		distanceMatrix = cityDistanceMatrixMap[city]
		result = findShortestPathFromWH(distanceMatrix)
		city_delivery_routes[city] = {}
		for path in result.keys():
			city_delivery_routes[city][path] = { "orders": [] }
			for orderIndex in result[path]:
				if orderIndex != -1:
					if orderIndex == 0:
						city_delivery_routes[city][path]["orders"].append(warehouseLocationsMap[city]["warehouseId"])
					else:
						city_delivery_routes[city][path]["orders"].append(city_orders_indexing[city][orderIndex])	
	
	db_entry = {
		'_id': deliveryDate,
		'orderRouting': city_delivery_routes
	}
	routes.insert_one(db_entry)
	print('inserted one')
######## END - ORDER ROUTING ########

######## Testing scripts ########
# cities = '"Phoenix", "Los Angeles", "Sacramento", "Denver", "Las Vegas", "Boston", "Seattle", "New York", "Chicago", "San Jose"'
# routeOrders(None, None, None, { "cities": cities, "deliveryDate": "2021-12-31" })
#################################


######## RabbitMQ connection ###########
rabbitMQ = pika.BlockingConnection(
	pika.ConnectionParameters(host=c.config['rabbitmq_host'], port=c.config['rabbitmq_port']))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toRoutingWorker')
rabbitMQChannel.basic_consume(queue='toRoutingWorker', on_message_callback=routeOrders, auto_ack=False)
rabbitMQChannel.start_consuming()
######## END - RabbitMQ connection ###########
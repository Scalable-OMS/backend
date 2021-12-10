# make db connection - MongoDB
# for the requested date, get the document data
# for each city get the orderids and
# for each of the order id, get the user data
# get the outlet address for those cities
# for each of those orders in the city get distances from the warehouse
# create a distance matrix and use a naive travelling salesman problem and get the route
# store the route in mongoDB document for that date
from math import *
from queue import PriorityQueue

import pika
import os

import pymongo
from pymongo import MongoClient
import mysql.connector
import json
import requests


######### MongoDB ###########

# m_uri = "mongodb://{host}:{port}/{dbname}".format(
#     host=os.getenv("mongodb_host"),
#     port=os.getenv("mongodb_port"),
#     dbname=os.getenv("mongodb")
# )
# client = MongoClient(m_uri)
# mongodb = client.routesDB

user = os.getenv("mongodb_user")
password = os.getenv("mongodb_pwd")
routes_db = os.getenv("routes_db")
client = pymongo.MongoClient(
    f"mongodb+srv://{user}:{password}@mygamecluster.e4sni.mongodb.net/gameMeta?retryWrites=true&w=majority")
db = client.oms
routes = db["routes"]


######### END - MongoDB ###########

######### MYSQL ###########

mysqldb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="oms"
)

def getOrdersByDate(deliveryDate, city):
    try:
        sqlcursor =  mysqldb.cursor()
        query = f"SELECT * FROM orders o, users u WHERE o.userId=u.id AND o.deliveryDate=\'{deliveryDate}\' and u.city=\'{city}\'"
        sqlcursor.execute(query)
        result = sqlcursor.fetchall()
        print("orders response")
        for x in result:
            print(x)
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
        print("getCoordinatesForAddress response")
        for x in result:
            print(x)
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
        destinations={addresses}&origins={addresses}&units=imperial&key={google_api_key}""" \
            .format(
            addresses=addresses,
            google_api_key=os.getenv("google_api_key")
        )
        requestUris.append({"uri": uri, "city": city})
    print("All google api requests")
    print(requestUris)
    return requestUris


def getDistanceBetweenOrders(cityOrders, warehouseLocations):
    city_distance_map = {}

    for city in cityOrders.keys():
        city_addresses = []
        if city not in warehouseLocations:
            return city_distance_map
        warehouse = warehouseLocations[city]['coordinates']
        city_addresses.append(warehouse)
        orders = cityOrders[city]
        for order in orders:
            order_address = getCoordinatesForAddress(order["customerId"])
            city_addresses.append(order_address)

    city_distance_map[city] = getDistanceMatrix(city_addresses)

    return city_distance_map


def getDistanceMatrix(addresses):
    distance_matrix = [[0 for _ in range(len(addresses))] for _ in range(len(addresses))]

    for i in range(len(addresses)):
        for j in range(len(addresses)):
            distance_matrix[i][j] = getDistance(addresses[i], addresses[j])

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
def route(city):
    # orders = getOrdersByDate(deliveryDate)
    orders = getOrdersByDate("2021-12-31", city)
    warehouseLocations = getWarehouseLocations()
    warehouseLocationsMap = {}
    for warehouse in warehouseLocations:
        warehouse_city = warehouse[1]
        if warehouse_city not in warehouseLocationsMap:
            warehouseLocationsMap[warehouse_city] = { }
        warehouseLocationsMap[warehouse_city]['address'] = warehouse[2]
        warehouseLocationsMap[warehouse_city]['coordinates'] = warehouse[3]

    cityDistanceMatrixMap = {}
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
    # requestsUrls = getRequestUrls(cityOrdersMap, warehouseLocationsMap)
    # for request_uri in requestsUrls:
    #     response = requests.get(request_uri['uri'])
    #     address_list = response['origin_addresses']
    #     city = request_uri['city']
    #     # creating a 2-d empty distance matrix
    #     origin_index = 0
    #     destination_index = 0
    #     tempDistanceMatrix = [[0]*len(address_list)]*len(address_list)
    #     for origin_distance_details in response["rows"]:
    #         for origin_destination_dist in origin_distance_details['elements']:
    #             tempDistanceMatrix[origin_index][destination_index] = origin_destination_dist["distance"]["value"]
    #             # for each of the destination from the origin we update the matrix
    #             # destinations as column in the matrix
    #             destination_index += 1
    #         # origin as row in the matrix
    #         origin_index += 1
    #     cityDistanceMatrixMap[city] = tempDistanceMatrix

    cityDistanceMatrixMap = getDistanceBetweenOrders(cityOrdersMap, warehouseLocationsMap)
    # if order_city not in cityDistanceMatrixMap:
    #     continue
    g = Graph(len(cityDistanceMatrixMap[city]))
    add_edges(g, cityDistanceMatrixMap[city])
    D = g.dijkstra(0)

    for vertex in range(len(D)):
        print("Distance from vertex 0 to vertex", vertex, "is", D[vertex])

    # now we have the distance matrix of all the cities
    # all we need to do now is run the travelling salesman problem on each of these matrices

def add_edges(graph, matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            graph.add_edge(i, j, matrix[i][j])


class Graph:

    def __init__(self, num_of_vertices):
        self.v = num_of_vertices
        self.edges = [[-1 for i in range(num_of_vertices)] for j in range(num_of_vertices)]
        self.visited = []

    def add_edge(self, u, v, weight):
        self.edges[u][v] = weight
        self.edges[v][u] = weight

    #todo add shortest path
    def dijkstra(self, start_vertex):
        D = {v: float('inf') for v in range(self.v)}
        D[start_vertex] = 0

        pq = PriorityQueue()
        pq.put((0, start_vertex))

        while not pq.empty():
            (dist, current_vertex) = pq.get()
            self.visited.append(current_vertex)

            for neighbor in range(self.v):
                if self.edges[current_vertex][neighbor] != -1:
                    distance = self.edges[current_vertex][neighbor]
                    if neighbor not in self.visited:
                        old_cost = D[neighbor]
                        new_cost = D[current_vertex] + distance
                        if new_cost < old_cost:
                            pq.put((new_cost, neighbor))
                            D[neighbor] = new_cost
        return D

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
# this will connect to SQL database
# get all the orders for the passed date
# sort orders based on zipcode
# now for each of those zipcodes get only orderids and 
# create a document with key as deliveryDate in mongodb storing the orderids under each city and zipcode
import pika
import os
from pymongo import MongoClient
import mysql.connector
import json


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
		for x in result:
			print(x)
		return result
	except Exception as e:
		print(e)

######### END - MYSQL ###########

def categorizeOrders(ch, method, properties, body):
	req_body = json.loads(body.decode('utf-8'))
	deliveryDate = req_body['deliveryDate']
	orders = getOrdersByDate(deliveryDate)
	citymap = {}
	try:
		for order in orders:
			order_city = order["city"]
			order_postalCode = order["postalCode"]
			order_id = order["orderId"]
			if order_city in citymap:
				if order_postalCode in citymap:
					citymap[order_city][order_postalCode].append(order_id)
				else:
					citymap[order_city][order_postalCode] = []
					citymap[order_city][order_postalCode].append(order_id)
			else:
				citymap[order_city] = {}
		db_entry = { "deliveryDate": deliveryDate, "orderData": citymap }
		inserted = mongodb.routes.insert_one(db_entry)
		print(inserted.inserted_id)
	except Exception as e:
		print(e)

######### RabbitMQ connection ###########

rabbitMQHost = os.getenv("RABBITMQ_HOST") or "rabbitmq"
rabbitMQ = pika.BlockingConnection(
	pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toSortingWorker')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
rabbitMQChannel.basic_consume(queue='toSortingWorker', on_message_callback=categorizeOrders, auto_ack=False)
rabbitMQChannel.start_consuming()

######### END - RabbitMQ connection ###########
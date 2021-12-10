# this will connect to SQL database
# get all the orders for the passed date
# sort orders based on zipcode
# now for each of those zipcodes get only orderids and 
# create a document with key as deliveryDate in mongodb storing the orderids under each city and zipcode
import pika
import os
import pymongo
import mysql.connector
import json
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
orders_categorized = db['orders']
######### END - MongoDB ###########

######### MYSQL ###########
mysqldb = mysql.connector.connect(
	host=c.config['mysql_host'],
	user=c.config['mysql_username'],
	password=c.config['mysql_password'],
	database=c.config['mysql_dbname']
)

def getOrdersByDate(deliveryDate):
	try:
		sqlcursor =  mysqldb.cursor()
		sqlcursor.execute("SELECT * FROM orders o, users u, products p WHERE o.userId=u.id AND o.productId=p.id AND \
			o.deliveryDate='{date}'".format(date=deliveryDate))
		result = sqlcursor.fetchall()
		return result
	except Exception as e:
		print(e)
######### END - MYSQL ###########

######### Order Categorization ###########
def categorizeOrders(ch, method, properties, body):
	# req_body = json.loads(body.decode('utf-8'))
	# deliveryDate = req_body['deliveryDate']
	deliveryDate = body['deliveryDate']
	orders = getOrdersByDate(deliveryDate)
	citymap = {}
	print(orders[0])
	try:
		for order in orders:
			order_city = order[11]
			order_postalCode = order[12]
			order_id = order[0]
			product_id = order[13]
			product_name = order[14]
			if order_city not in citymap:
				citymap[order_city] = {}
			if order_postalCode not in citymap[order_city]:
				citymap[order_city][order_postalCode] = []
			citymap[order_city][order_postalCode].append({"orderId": order_id, "productName": product_name, "productId": product_id})
		db_entry = { "_id": deliveryDate, "orderData": citymap }
		orders_categorized.insert_one(db_entry)
		print("Completed Task - Categorizing orders for date={date}".format(date=deliveryDate))
	except Exception as e:
		print(e)
######### END - Order Categorization ###########

######### Testing scripts ###########
categorizeOrders(None, None, None, { "deliveryDate": "2021-12-31" })
######### END - Testing scripts ###########

######### RabbitMQ connection ###########
rabbitMQ = pika.BlockingConnection(
	pika.ConnectionParameters(host=c.config['rabbitmq_host'], port=c.config['rabbitmq_port']))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toSortingWorker')
rabbitMQChannel.basic_consume(queue='toSortingWorker', on_message_callback=categorizeOrders, auto_ack=False)
rabbitMQChannel.start_consuming()
######### END - RabbitMQ connection ###########
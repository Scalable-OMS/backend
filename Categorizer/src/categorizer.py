# this will connect to SQL database
# get all the orders for the passed date
# sort orders based on zipcode
# now for each of those zipcodes get only orderids and 
# create a document with key as deliveryDate in mongodb storing the orderids under each city and zipcode
import pika
import os

rabbitMQHost = os.getenv("RABBITMQ_HOST") or "rabbitmq"

def categorize():


rabbitMQ = pika.BlockingConnection(
	pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toSortingWorker')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
rabbitMQChannel.basic_consume(queue='toSortingWorker', on_message_callback=categorize, auto_ack=False)
rabbitMQChannel.start_consuming()
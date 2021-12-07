# connect to mongoDB and get route data for the given date
from flask import Flask, request, Response
import jsonpickle
import schedule
from Controllers.orders import orders_api
from Controllers.auth import auth_api
import os
import pika

#######################
# Initialize the Flask application
app = Flask(__name__)
app.register_blueprint(orders_api)
app.register_blueprint(auth_api)
#######################

#######################
# MongoDB connection
app.config['MONGODB_SETTINGS'] = {
	'db': os.getenv("mongodb"),
	'host': os.getenv("mongodb_host"),
	'port': os.getenv("mongodb_port")
}
#######################

#######################
# rabbitmq connection
rabbitMQ = pika.BlockingConnection(
pika.ConnectionParameters(host=rabbitMQHost, heartbeat=0))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toSortingWorker')
#######################

#######################
# main route
@app.route('/api/', methods='GET')
def main():
	res = { "data": "ok" }
	return Response(response=jsonpickle.encode(res), status=200)
#######################

#######################
# start cron jobs
def job():
	# schedule a job to the categorizer worker
	rabbitmq.publish_action()
#######################

schedule.every().day.at("00:00").do(job)
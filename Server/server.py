# connect to mongoDB and get route data for the given date
import json
from flask import Flask, request, Response
import jsonpickle
import base64
import os
from flask_pymongo import PyMongo
import schedule
from Controllers.orders import orders_api

# Initialize the Flask application
app = Flask(__name__)

# MongoDB connection
app.config['MONGODB_SETTINGS'] = {
	'db': os.getenv("mongodb"),
	'host': os.getenv("mongodb_host"),
	'port': os.getenv("mongodb_port")
}
uri = "mongodb://{host}:{port}/{dbname}".format(
	host=os.getenv("mongodb_host"), 
	port=os.getenv("mongodb_port"), 
	dbname=os.getenv("mongodb"))
mongodb_client = PyMongo(app, uri=uri)
db = mongodb_client.db

app.register_blueprint(orders_api)

@app.route('/api/', methods='GET')
def main():
	res = { "data": "ok" }
	return Response(response=jsonpickle.encode(res), status=200)

# URL: /api/routes&city=denver&deliveryDate=2021-10-08
# queries MongoDB for route information which will include only the orderIds
@app.route('/api/routes', methods='GET')
def getOrderRoutes():
	city = request.args.get('city')
	deliveryDate = request.args.get('deliveryDate')
	try:
		routes = db.routes.find({ "_id": deliveryDate })
		cityOrders = filter(lambda x: x.city == city, routes)
		return Response(response=jsonpickle.encode({ "data": cityOrders }), status=200)
	except Exception as e:
		return Response(response=jsonpickle.encode({ "error": e }, status=404))

# start cron jobs
def job():
	# schedule a job to the categorizer worker
	rabbitmq.publish_action()

schedule.every().day.at("00:00").do()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys
from apscheduler.schedulers.background import BackgroundScheduler
import pika
from .config import config
import pymongo
from flask_cors import CORS

db = SQLAlchemy()

######### MongoDB ###########
user = config['mongo_user']
password = config['mongo_password']
mongodb = config['mongodb']
host = config['mongo_host']
connection_url = f"mongodb+srv://{user}:{password}@{host}/gameMeta?retryWrites=true&w=majority".\
	format(user, password, host)
client = pymongo.MongoClient(connection_url)
m_db = client.oms
routes_collection = m_db['routes']
orders_collection = m_db['orders']
driver_assignment = m_db['driver_assignment']
######### END - MongoDB ###########

########## RABBITMQ Connection ############
rabbitMQ = pika.BlockingConnection(
pika.ConnectionParameters(host=config['rabbitmq_host'], port=config['rabbitmq_port'], heartbeat=0))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toSortingWorker')
rabbitMQChannel.queue_declare(queue='toRoutingWorker')
########## END RABBITMQ Connection ############

########### CRON Jobs ###########
def job():
	print("job called", file=sys.stderr)
	# schedule a job to the categorizer worker
	rabbitMQ.publish_action()

scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})
a_job = scheduler.add_job(job, trigger='cron', hour='18', minute='23', second='0')
scheduler.start()
########### CRON Jobs ############

def create_app():
	"""Construct the core application."""
	app = Flask(__name__, instance_relative_config=False)
	# app.config.from_object("config.Config")
	s_uri = "mysql+mysqlconnector://{username}:{password}@{host}/{dbname}".format(
		username=config['username'],
		password=config['password'],
		host=config['host'],
		dbname=config['dbname']
	)
	app.config['SQLALCHEMY_DATABASE_URI'] = s_uri
	db.init_app(app)

	########## MongoDB connection #############
	app.config['MONGODB_SETTINGS'] = {
		'db': config['mongodb'],
		'user': config['mongo_user'],
		'password': config['mongo_password'],
	}
	########## END - MongoDB connection #############

	with app.app_context():
		from .orders import orders_api
		from .auth import auth_api
		from .routes import routes_api
		
		# CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers='content-type, role, token', expose_headers='content-type, role, token')
		CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers='*', expose_headers='*')
		# db.create_all()
		app.register_blueprint(orders_api)
		app.register_blueprint(auth_api)
		app.register_blueprint(routes_api)
		return app
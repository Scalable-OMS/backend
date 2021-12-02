from flask import g
import os
from pymongo import MongoClient
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy


######### MYSQL ###########
# SQLAlchemy Database Configuration With Mysql
s_uri = "mysql://{username}:{password}@{host}/{dbname}".format(
	username=os.getenv("mysql_username"),
	password=os.getenv("mysql_password"),
	host=os.getenv("mysql_host"),
	dbname=os.getenv("mysql_dbname")
)
app.config['SQLALCHEMY_DATABASE_URI'] = s_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

######### Models ###########
class Users(db.Model):
	id = db.Column(db.String(100), primary_key = True)
	name = db.Column(db.String(100))
	address = db.Column(db.String(400))
	postalcode = db.Column(db.Integer)
	city = db.Column(db.String(100))
	role = db.Column(db.String(50))

	def __init__(self, id, name, address, postalcode, city, role):
		self.id = id
		self.name = name
		self.address = address
		self.postalcode = postalcode
		self.city = city
		self.role = role

class Orders(db.Model):
	id = db.Column(db.String(100), primary_key = True)
	productId = db.Column(db.String(100))
	userId = db.Column(db.String(100))

	def __init__(self, id, productId, userId):
		self.id = id
		self.productId = productId
		self.userId = userId

class Products(db.Model):
	id = db.Column(db.String(100), primary_key = True)
	productName = db.Column(db.String(100))

	def __init__(self, id, productName):
		self.id = id
		self.productName = productName

class Warehouses(db.Model):
	id = db.Column(db.String(100), primary_key = True)
	city = db.Column(db.String(100))
	address = db.Column(db.String(400))

	def __init__(self, id, address, city):
		self.id = id
		self.address = address
		self.city = city

######### END - Models ###########

def mysql_db():
	return db

######### END - MYSQL ###########


######### MongoDB ###########

m_uri = "mongodb://{host}:{port}/{dbname}".format(
	host=os.getenv("mongodb_host"), 
	port=os.getenv("mongodb_port"), 
	dbname=os.getenv("mongodb")
)

def mongo_db():
	if 'db' not in g:
		mongodb_client = PyMongo(app, uri=m_uri)
		g.db = mongodb_client.db

	return g.db

def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()

######### END - MONGO_DB ###########
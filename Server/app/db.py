from flask import g
import os
# from pymongo import MongoClient
# from flask import current_app as app
# from flask_sqlalchemy import SQLAlchemy
# from config import config
from . import db


######### MYSQL ###########
# SQLAlchemy Database Configuration With Mysql
# db = None
# def init_db():
# 	s_uri = "mysql://{username}:{password}@{host}/{dbname}".format(
# 		username=config['username'],
# 		password=config['password'],
# 		host=config['host'],
# 		dbname=config['dbname']
# 	)
# 	app.config['SQLALCHEMY_DATABASE_URI'] = s_uri
# 	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 	db = SQLAlchemy(app)

######### Models ###########
class Users(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))
	address = db.Column(db.String(400))
	postalcode = db.Column(db.Integer)
	city = db.Column(db.String(100))

	def __init__(self, id, name, address, postalcode, city, email):
		self.id = id
		self.name = name
		self.address = address
		self.postalcode = postalcode
		self.city = city
		self.email = email

class Orders(db.Model):
	id = db.Column(db.String(100), primary_key = True)
	productId = db.Column(db.String(100), db.ForeignKey("products.id"))
	userId = db.Column(db.Integer, db.ForeignKey("users.id"))
	deliveryDate = db.Column(db.String(100))
	status = db.Column(db.String(100))

	# user = db.relationship("Users", foreign_keys="Orders.userId")
	# product = db.relationship("Products", foreign_keys="Orders.productId")

	def __init__(self, id, productId, userId, deliveryDate, status):
		self.id = id
		self.productId = productId
		self.userId = userId
		self.deliveryDate = deliveryDate
		self.status = status

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

class Auth(db.Model):
	id = db.Column(db.String(100), primary_key = True)
	email = db.Column(db.String(100))
	password = db.Column(db.String(200))
	token = db.Column(db.String(200))
	role = db.Column(db.String(20))

class Drivers(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	city = db.Column(db.String(100))
	name = db.Column(db.String(100))

######### END - Models ###########

def mysql_db():
	return db

##### orders #####
def getAllOrders(deliveryDate):
	return db.session.query(Orders).filter_by(deliveryDate=deliveryDate).all()

def getOrderDetails():
	orderDetails = db.session.query(Orders, Users).join(Orders).join(Users).filter_by(Orders.userId == Users.id).all()
	print(orderDetails)
	return orderDetails

def createOrder(order):
	order_obj = Orders(productId=order["productId"], userId=order["userId"], deliveryDate=order["deliveryDate"])
	db.session.add(order_obj)
	db.session.commit()

def cancelOrder(orderId):
	order = db.session.query(Orders).filter_by(orderId=orderId).first()
	order.status = "cancelled"
	db.session.commit()

##### END - orders #####

def getAllWarehouses():
	return Warehouses.query.all()

def getProductById(id):
	return Products.query.filter_by(id=id).all()

##### auth #####

def verifyUser(creds):
	user = db.session.query(Auth).filter_by(email=creds["email"]).first()
	if user is not None:
		return user
	return None

def updateToken(token, email):
	user = db.session.query(Auth).filter_by(email=email).first()
	user.token = token
	db.session.commit()

##### END - auth #####

##### Routes #####

def updateOrdersStatus(category, status, deliveryDate):
	if category['key'] == 'city':
		# db.session.query(Orders, Users).join(Orders).join(Users).filter_by(Orders.userId == Users.id).all()
		query = "SELECT * FROM Orders o, Users u WHERE o.userId=u.id AND u.city='{city}' AND o.deliveryDate='{deliveryDate}'".\
			format(city=category['value'], deliveryDate=deliveryDate)
		result = db.\
			engine.\
			execute(query)
		print(result)
	elif category['key'] == 'postalCode':
		query = "SELECT * FROM Orders o, Users u WHERE o.userId=u.id AND u.postalCode='{postalCode}' AND o.deliveryDate='{deliveryDate}'".\
			format(postalCode=category['value'], deliveryDate=deliveryDate)
		result = db.\
			engine.\
			execute(query)
		print(result)
	else:
		query = "UPDATE TABLE Orders SET status={status} WHERE id={orderId}".format(status=status, orderI=category['value'])
		result = db.\
			engine.\
			execute(query)
		print(result)

def getDriversByCity(city):
	drivers = db.session.query(Drivers).filter_by(city=city).all()
	return drivers


######### END - MYSQL ###########


######### MongoDB ###########

m_uri = "mongodb://{host}:{port}/{dbname}".format(
	host=os.getenv("mongodb_host"), 
	port=os.getenv("mongodb_port"), 
	dbname=os.getenv("mongodb")
)

def mongo_db():
	return None
	# if 'db' not in g:
	# 	mongodb_client = PyMongo(app, uri=m_uri)
	# 	g.db = mongodb_client.db

	# return g.db

def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()

######### END - MONGO_DB ###########
from . import db
from . import orders_collection, routes_collection, driver_assignment
import mysql.connector
from .config import config

######### Models ###########
class Users(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))
	address = db.Column(db.String(400))
	postalCode = db.Column(db.Integer)
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

	user = db.relationship("Users", foreign_keys="Orders.userId")
	product = db.relationship("Products", foreign_keys="Orders.productId")

	def __init__(self, id, productId, userId, deliveryDate, status):
		self.id = id
		self.productId = productId
		self.userId = userId
		self.deliveryDate = deliveryDate
		self.status = status

def serializeOrder(order):
	res = {
			"id": order[0].id,
			"deliveryDate": order[0].deliveryDate,
			"status": order[0].status,
			"user": {
				"id": order[1].id,
				"name": order[1].name,
				"email": order[1].email,
				"address": order[1].address,
				"postalCode": order[1].postalCode,
				"city": order[1].city
			}
		}
	if len(order) == 3:
		res['product'] = {
			"id": order[2].id,
			"productName": order[2].productName
		}
	return res


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
	driver_name = db.Column(db.String(100))
	email = db.Column(db.String(100))

######### END - Models ###########

def mysql_db():
	return db

##### orders #####
# def getAllOrders():
# 	try:
# 		return db.session.query(Orders).filter_by(deliveryDate=deliveryDate).all()
# 	except Exception as e:
# 		print(e)

def getOrderDetails(deliveryDate, city, postalCode):
	if city:
		response = db.\
			session.\
			query(Orders, Users, Products).\
			join(Users, Users.id==Orders.userId).\
			join(Products, Products.id==Orders.productId).\
			filter(Users.city==city).\
			filter(Orders.deliveryDate==deliveryDate).\
			all()
	elif postalCode:
		response = db.\
			session.\
			query(Orders, Users, Products).\
			join(Users, Users.id==Orders.userId).\
			join(Products, Products.id==Orders.productId).\
			filter(Users.postalCode==postalCode).\
			filter(Orders.deliveryDate==deliveryDate).\
			all()

	orderDetails = [ serializeOrder(order) for order in response ]
	return orderDetails

def getOrderCities(deliveryDate):
	response = db.session.\
		query(Users, Orders).\
		join(Orders, Orders.userId == Users.id).\
		filter(Orders.deliveryDate==deliveryDate).\
		all()
	citiesMap = {}
	for order in response:
		if order[0].city in citiesMap:
			citiesMap[order[0].city] += 1
		else:
			citiesMap[order[0].city] = 1
	return citiesMap

def createOrder(order):
	order_obj = Orders(productId=order["productId"], userId=order["userId"], deliveryDate=order["deliveryDate"])
	db.session.add(order_obj)
	db.session.commit()

def cancelOrder(orderId):
	order = db.session.query(Orders).filter_by(orderId=orderId).first()
	order.status = "cancelled"
	db.session.commit()

# response = db.session.\
# 	query(Users, Orders).\
# 	join(Orders, Orders.userId==Users.id).\
# 	filter(Users.city==category['value']).\
# 	filter(Orders.deliveryDate==deliveryDate).\
# 	update({ Orders.status: status }, synchronize_session=False)
def updateStatus(category, status, deliveryDate):
	mysqldb = mysql.connector.connect(
		host=config['host'],
		user=config['username'],
		password=config['password'],
		database=config['dbname']
	)
	if category['key'] == 'city':
		query = "UPDATE orders o \
			INNER JOIN users u ON o.userId=u.id \
			SET o.status='{status}' WHERE u.city='{city}' AND o.deliveryDate='{deliveryDate}'".\
			format(status=status, city=category['value'], deliveryDate=deliveryDate)

	elif category['key'] == 'postalCode':
		query = "UPDATE orders o \
			INNER JOIN users u ON o.userId=u.id \
			SET o.status='{status}' WHERE u.postalCode='{postalCode}' AND o.deliveryDate='{deliveryDate}'".\
			format(status=status, postalCode=category['value'], deliveryDate=deliveryDate)
	else:
		query = "UPDATE orders o \
			INNER JOIN users u ON o.userId=u.id \
			SET o.status='{status}' WHERE o.id='{orderId}'".\
			format(status=status, orderId=category['value'])

	sqlcursor =  mysqldb.cursor()
	sqlcursor.execute(query)
	mysqldb.commit()
	sqlcursor.close()
	mysqldb.close()
##### END - orders #####

##### GET entities ########
def getAllWarehouses():
	return Warehouses.query.all()

def getProductById(id):
	return db.session.query(Products).filter(Products.id==id).all()

def getDriversByCity(city):
	drivers = db.session.query(Drivers).filter(Drivers.city==city).all()
	return drivers

def getDriverCity(email):
	driver = db.\
		session.\
		query(Drivers).\
		filter(Drivers.email==email).\
		first()
	return driver.city, driver.id
##### END - GET entities ########

##### auth #####
def verifyUser(creds):
	# user = db.session.query(Auth).filter(Auth.email==creds["email"]).first()
	user = db.session.query(Auth).filter(Auth.email==creds["email"]).first()
	if user is not None:
		return user
	return None

def updateToken(token, email):
	print(email)
	user = db.session.query(Auth).filter(Auth.email==email).first()
	user.token = token['access_token']
	db.session.commit()
##### END - auth #####

######### END - MYSQL ###########


######### MONGO_DB ###########
def getOrdersByCity(deliveryDate, city):
	orders = orders_collection.find_one({ "_id": deliveryDate })
	if city in orders['orderData']:
		return orders['orderData'][city]
	else:
		return {}

def getDriverPathAssignment(driver_id, city, deliveryDate):
	# result = driver_assignment.find_one({ "deliveryDate": deliveryDate, "city": city })
	result = driver_assignment.find_one({ "deliveryDate": deliveryDate, "city": "Chicago" })
	driver_path = None
	# print(result.keys())
	if result:
		for key in result.keys():
			# print(type(result[key]))
			if result[key] == driver_id:
				driver_path = key
	return driver_path

def getOrderRoutingForCity(deliveryDate, city, path=None):
	result = routes_collection.find_one({ "_id": deliveryDate })
	driversAssigned = driver_assignment.find_one({ "deliveryDate": deliveryDate, "city": city })
	if result:
		if path:
			city_routes = result['orderRouting'][city][path]['orders']
		else:
			city_routes = []
			for order_path in result['orderRouting'][city].keys():
				obj = {
					"path_id": order_path,
					"noOfOrders": len(result['orderRouting'][city][order_path]['orders'])
				}
				if driversAssigned != None:
					obj["driverAssigned"] = driversAssigned[order_path]
				city_routes.append(obj)
		return city_routes

def updateDriverForPath(deliveryDate, city, path, driverId):
	filter = { "deliveryDate": deliveryDate, "city": city }
	query = {}
	query[path] = driverId
	update = { "$set": query}
	# print(update)
	driver_assignment.update_one(filter, update)

def getOrderDetailsForEachOrder(deliveryRoute):
	orders = []
	for order in deliveryRoute:
		try:
			order_details = { "orderId": order['orderId'], "deliveryAddress": order["deliveryAddress"] }
			entry = db.session.query(Orders).filter(Orders.id==order['orderId']).first()
			order_details["status"] = entry.status
			orders.append(order_details)
		except:
			print('warehouse location')
	return orders
######### END - MONGO_DB ###########
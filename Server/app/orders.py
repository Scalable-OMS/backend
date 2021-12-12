from flask import Blueprint, Response, request
import jsonpickle

from .auth import getTokenAttribute, responseFormatter
from .db import createOrder,\
	cancelOrder,\
	getDriverCity,\
	getDriverPathAssignment, getDriversByCity,\
	getOrderDetails,\
	getOrderCities, getOrderDetailsForEachOrder,\
	getOrderRoutingForCity,\
	getOrdersByCity, updateDriverForPath,\
	updateStatus
import json

orders_api = Blueprint("orders_api", __name__)

# this will create orders and get orders and put them to the mysql database

@orders_api.route("/orders", methods=['GET'])
def GetOrders():
	# get orders data
	try:
		deliveryDate = request.args.get('deliveryDate')
		city = request.args.get('city')
		postalCode = request.args.get('postalCode')
		orders = getOrderDetails(deliveryDate, city, postalCode)
		return Response(response=jsonpickle.encode(orders), status=200)
	except Exception as e:
		print(e)
		return Response(response=jsonpickle.encode(e), status=400)

@orders_api.route("/orders/cities", methods=['GET'])
def GetOrderCities():
	try:
		deliveryDate = request.args.get('deliveryDate')
		cityDetails = getOrderCities(deliveryDate)
		return Response(response=jsonpickle.encode(cityDetails), status=200)
	except Exception as e:
		return Response(response=jsonpickle.encode(e), status=400)

@orders_api.route("/orders/city", methods=['GET'])
def GetOrdersByCity():
	try:
		deliveryDate = request.args.get('deliveryDate')
		token = json.loads(request.headers.get('token'))
		role, email = getTokenAttribute(token['access_token'], "role"), getTokenAttribute(token['access_token'], "email")
		if role == "admin":
			city = request.args.get('city')
			cityOrders = getOrdersByCity(deliveryDate, city)
			return responseFormatter(cityOrders, request)
		else:
			city, driver_id = getDriverCity(email)
			if city:
				driverPathAssignment = getDriverPathAssignment(str(driver_id), city, deliveryDate)
				cityDeliveryRoute = getOrderRoutingForCity(deliveryDate, city, driverPathAssignment)
				orders = getOrderDetailsForEachOrder(cityDeliveryRoute)
				return responseFormatter(orders, request)
			else:
				return responseFormatter({ "status": "no path assigned" }, request)
	except Exception as e:
		return Response(response=jsonpickle.encode(e), status=400)

@orders_api.route("/orders/routing", methods=['GET'])
def GetOrderRouting():
	try:
		deliveryDate = request.args.get('deliveryDate')
		city = request.args.get('city')
		paths = getOrderRoutingForCity(deliveryDate, city)
		return responseFormatter(paths, request)
	except Exception as e:
		return responseFormatter(e, request, 400)

@orders_api.route("/orders", methods=['POST'])
def CreateOrders():
	# create orders
	order = json.loads(request.data)
	try:
		createOrder(order)
		return Response(response='ok', status=200)
	except Exception as e:
		print(e)
		return Response(response=jsonpickle.encode(e), status=400)

@orders_api.route("/orders/cancel", methods=['PUT'])
def CancelOrders():
	# cancel orders
	orderId = request.args.get('orderId')
	try:
		cancelOrder(orderId)
		return Response(response='Order Cancelled', status=200)
	except Exception as e:
		return Response(response=jsonpickle.encode(e), status=400)

@orders_api.route("/orders/status", methods=['PUT'])
def UpdateOrderStatus():
	req_body = json.loads(request.data)
	category, status, deliveryDate = req_body['category'], req_body['status'], req_body["deliveryDate"]
	try:
		updateStatus(category, status, deliveryDate)
		return Response(response="Updated", status=200)
	except Exception as e:
		return Response(response=jsonpickle.encode(e), status=400)

@orders_api.route("/drivers", methods=['GET'])
def getDrivers():
	city = request.args.get('city')
	try:
		drivers = getDriversByCity(city)
		return responseFormatter(drivers, request)
	except Exception as e:
		return Response(response=jsonpickle.encode(e), status=400)

@orders_api.route("/drivers", methods=['PUT'])
def updateDriver():
	body = json.loads(request.data)
	deliveryDate, driverId, city, path = body['deliveryDate'], body['driverId'], body['city'], body['path']
	try:
		updateDriverForPath(deliveryDate, city, path, driverId)
		return responseFormatter({ "status": "ok" }, request)
	except Exception as e:
		return Response(response=jsonpickle.encode(e), status=400)
from os import stat
from flask import Blueprint, Response, request
import jsonpickle
from Database.db import getAllOrders, createOrder
from Server.src.Database.db import cancelOrder

orders_api = Blueprint("orders_api", __name__)

# this will create orders and get orders and put them to the mysql database

@orders_api.route("/orders", methods='GET')
def GetOrders():
	# get orders data
	try:
		deliveryDate = request.args.get('deliveryDate')
		orders = getAllOrders(deliveryDate)
		return Response(response=jsonpickle.encode(orders), status=200)
	except Exception as e:
		print(e)
		return Response(response=e, status=400)

@orders_api.route("/orders", methods='POST')
def CreateOrders():
	# create orders
	order = request.body
	try:
		createOrder(order)
		return Response(response='ok', status=200)
	except Exception as e:
		print(e)
		return Response(response=e, status=400)

@orders_api.route("/orders", methods='PUT')
def UpdateOrders():
	# cancel orders
	orderId = request.args.get('orderId')
	try:
		cancelOrder(orderId)
		return Response(response='Order Cancelled', status=200)
	except Exception as e:
		return Response(response=e, status=400)
		
		
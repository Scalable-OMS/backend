from flask import Blueprint, Response, request
import jsonpickle
from .db import getAllOrders, createOrder, cancelOrder

orders_api = Blueprint("orders_api", __name__)

# this will create orders and get orders and put them to the mysql database

@orders_api.route("/orders", methods=['GET'])
def GetOrders():
	# get orders data
	try:
		deliveryDate = request.args.get('deliveryDate')
		orders = getAllOrders(deliveryDate)
		print(orders)
		return Response(response=jsonpickle.encode(orders), status=200)
	except Exception as e:
		print(e)
		return Response(response=e, status=400)

@orders_api.route("/orders", methods=['POST'])
def CreateOrders():
	# create orders
	order = request.body
	try:
		createOrder(order)
		return Response(response='ok', status=200)
	except Exception as e:
		print(e)
		return Response(response=e, status=400)

@orders_api.route("/orders/cancel", methods=['PUT'])
def CancelOrders():
	# cancel orders
	orderId = request.args.get('orderId')
	try:
		cancelOrder(orderId)
		return Response(response='Order Cancelled', status=200)
	except Exception as e:
		return Response(response=e, status=400)
		
		
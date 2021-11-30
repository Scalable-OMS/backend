from flask import Blueprint
from flask.wrappers import Response

orders_api = Blueprint("orders_api", __name__)

# this will create orders and get orders and put them to the mysql database

@orders_api.route("/orders", methods='GET')
def GetOrders():
	# get orders data
	return Response(response='ok', status=200)

@orders_api.route("/orders", methods='POST')
def CreateOrders():
	# create orders
	return Response(response='ok', status=200)

@orders_api.route("/orders", methods='PUT')
def CreateOrders():
	# cancel orders
	return Response(response='ok', status=200)
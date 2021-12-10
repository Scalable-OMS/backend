import json
from flask import Blueprint, Response, request
from .db import mongo_db, updateOrdersStatus, getDriversByCity
import jsonpickle

routes_api = Blueprint("routes_api", __name__)

#######################
# URL: /api/routes&city=denver&deliveryDate=2021-10-08
# queries MongoDB for route information which will include only the orderIds
@routes_api.route('/api/routes', methods=['GET'])
def getOrderRoutes():
	city = request.args.get('city')
	deliveryDate = request.args.get('deliveryDate')
	try:
		routes = mongo_db().routes.find({ "deliveryDate": deliveryDate })
		cityOrders = filter(lambda x: x.city == city, routes)
		return Response(response=jsonpickle.encode({ "data": cityOrders }), status=200)
	except Exception as e:
		return Response(response=jsonpickle.encode({ "error": e }, status=404))

@routes_api.route('/api/routes', methods=['PUT'])
def updateOrderRoutes():
	req_body = json.loads(request.data)
	# body: { category: { "key": "city", "value": "Boston" }, status: "Delivered", deliveryDate: "2021-10-08" }
	category, status, deliveryDate = req_body['category'], req_body['status'], req_body['deliveryDate']
	try:
		updateOrdersStatus(category, status, deliveryDate)
		return Response(response=jsonpickle.encode({ "data": "ok" }, status=200))
	except Exception as e:
		return Response(response=jsonpickle.encode({ "error": e }, status=404))

@routes_api.route('/api/routes/drivers', methods=['GET'])
def getDrivers():
	city = request.args.get("city")
	try:
		drivers = getDriversByCity(city)
		return Response(response=jsonpickle.encode({ "data": drivers }, status=200))
	except Exception as e:
		return Response(response=jsonpickle.encode({ "error": e }, status=404))
#######################

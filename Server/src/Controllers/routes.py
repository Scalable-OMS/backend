from flask import Blueprint
from flask.wrappers import Response, request
from Database.db import get_db
import jsonpickle

routes_api = Blueprint("routes_api", __name__)

#######################
# URL: /api/routes&city=denver&deliveryDate=2021-10-08
# queries MongoDB for route information which will include only the orderIds
@routes_api.route('/api/routes', methods='GET')
def getOrderRoutes():
	city = request.args.get('city')
	deliveryDate = request.args.get('deliveryDate')
	try:
		routes = get_db().routes.find({ "_id": deliveryDate })
		cityOrders = filter(lambda x: x.city == city, routes)
		return Response(response=jsonpickle.encode({ "data": cityOrders }), status=200)
	except Exception as e:
		return Response(response=jsonpickle.encode({ "error": e }, status=404))
#######################
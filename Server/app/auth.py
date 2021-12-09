from flask import Blueprint, Response, request
import jsonpickle
import jwt
import os
from .db import verifyUser, updateToken
from datetime import datetime
from datetime import timedelta

auth_api = Blueprint("auth_api", __name__)
secret = os.getenv("encoding_secret")
algorithm = os.getenv("encoding_algo")

def getTokenAttribute(token, id):
	decoded = jwt.encode(token, secret, algorithm)
	return decoded[id]

def getExp(tokenId):
	today = datetime.today().strptime('%Y-%m-%d')
	a_end = today + timedelta(days=2)
	a_exp = a_end.timestamp()
	r_end = today + timedelta(days=15)
	r_exp = r_end.timestamp()
	if tokenId == "a":
		return a_exp
	elif tokenId == "r":
		return r_exp
	else:
		return { "a_exp": a_exp, "r_exp": r_exp }

def createJWT(creds):
	token_expiry = getExp('both')
	a_payload = {
		"email": creds["email"],
		"password": creds["password"],
		"exp": token_expiry['a_exp']
	}
	r_payload = {
		"email": creds["email"],
		"exp": token_expiry["r_exp"]
	}
	access_token = jwt.encode(a_payload, secret, algorithm)
	refresh_token = jwt.encode(r_payload, secret, algorithm)
	return {
		"access_token": access_token,
		"refresh_token": refresh_token
	}

def validateToken(token):
	try:
		a_payload = jwt.decode(token["access_token"], os.getenv("encoding_secret"), os.getenv("encoding_algo"))
		r_payload = jwt.decode(token["refresh_token"], os.getenv("encoding_secret"), os.getenv("encoding_algo"))
		a_exp = datetime.fromtimestamp(a_payload["a_exp"])
		today = datetime.today()
		if today > a_exp:
			res = {}
			r_exp = datetime.fromtimestamp(r_payload["exp"])
			if today > r_exp:
				return False
			a_payload["exp"] = getExp('a')
			access_token = jwt.encode(a_payload, secret, algorithm)
			refresh_token = jwt.encode(r_payload, secret, algorithm)
			res["access_token"] = access_token
			res["refresh_token"] = refresh_token
			updateToken({
				"access_token": access_token,
				"refresh_token": refresh_token
			}, a_payload["email"])
			return res
		return token
	except Exception as e:
		print(e)
		return None

@auth_api.route("/auth/login", methods=['POST'])
def login():
	try:
		res = {
			"token": None,
			"status": False
		}
		creds = request.body
		user = verifyUser(creds)
		if user is not None:
			token = createJWT(creds)
			res = {}
			res["token"] = token
			res["status"] = True
			updateToken(token, user["email"])
			return Response(response=jsonpickle.encode(res), status=200)
		else:
			return Response(response=jsonpickle.encode(res), status=403)
	except Exception as e:
		return Response(response=jsonpickle.encode(e), status=400)

@auth_api.route("/auth/logout", methods=['PUT'])
def logout():
	try:
		token = request.headers.get("token")
		email = getTokenAttribute(token, "email")
		updateToken({
			"access_token": "",
			"refresh_token": ""
		}, email)
		return Response(response=jsonpickle.encode({ "msg": "logged out successfully" }), status=200)
	except Exception as e:
		return Response(response=jsonpickle.encode(e), status=400)
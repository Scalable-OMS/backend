from dotenv import load_dotenv
import os
import sys

load_dotenv()

config = {}
config['username']=os.getenv("mysql_user")
config['password']=os.getenv("mysql_password")
config['host']=os.getenv("mysql_host")
config['dbname']=os.getenv("mysqldb")

config['mongodb'] = os.getenv("mongodb")
config['mongo_user'] = os.getenv("mongo_user")
config['mongo_password'] = os.getenv("mongo_password")
config['mongo_host'] = os.getenv("mongo_host")

config['rabbitmq_host'] = os.getenv("rabbitmq_host")
config['rabbitmq_port'] = os.getenv("rabbitmq_port")

# print(config, file=sys.stderr)
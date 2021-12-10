from dotenv import load_dotenv
import os

load_dotenv()

config = {}
config['mongo_host'] = os.getenv('mongo_host')
config['mongodb'] = os.getenv("mongodb")
config['mongo_user'] = os.getenv("mongo_user")
config['mongo_password'] = os.getenv("mongo_password")

config['rabbitmq_host'] = os.getenv("rabbitmq_host")
config['rabbitmq_port'] = os.getenv("rabbitmq_port")

config['mysql_host']=os.getenv("mysql_host")
config['mysql_username']=os.getenv("mysql_user")
config['mysql_password']=os.getenv("mysql_password")
config['mysql_dbname']=os.getenv("mysqldb")
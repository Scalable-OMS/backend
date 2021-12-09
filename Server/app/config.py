from dotenv import load_dotenv
import os

load_dotenv()

config = {}
config['username']=os.getenv("mysql_user")
config['password']=os.getenv("mysql_password")
config['host']=os.getenv("mysql_host")
config['dbname']=os.getenv("mysqldb")
config['mongodb'] = os.getenv("mongodb")
config['mongodb_host'] = os.getenv("mongodb_host")
config['mongodb_port'] = os.getenv("mongodb_port")
config['rabbitmq_host'] = os.getenv("rabbitmq_host")
config['rabbitmq_port'] = os.getenv("rabbitmq_port")
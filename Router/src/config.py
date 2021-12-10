from dotenv import load_dotenv
import os

load_dotenv()

config = {}
config['mongodb'] = os.getenv("mongodb")
config['mongodb_host'] = os.getenv("mongodb_host")
config['mongodb_port'] = os.getenv("mongodb_port")
config['mongo_user'] = os.getenv("mongo_user")
config['rabbitmq_host'] = os.getenv("rabbitmq_host")
config['rabbitmq_port'] = os.getenv("rabbitmq_port")
import os
import pika
import json
import mysql.connector
import smtplib
from email.mime.text import MIMEText

mysqldb = mysql.connector.connect(
  host=os.getenv("mysql_host"),
  user=os.getenv("mysql_username"),
  password=os.getenv("mysql_password"),
  database=os.getenv("mysql_database")
)

def sendEmail(emails, status):
	templates_file = open("./emailTemplate.json")
	templates = json.load(templates_file)
	body = templates[status]["body"]
	msg = MIMEText(body)
	msg['Subject'] = templates[status]["subject"]
	mail_obj = smtplib.SMTP(os.getenv("email_host"))
	mail_obj.sendmail(os.getenv("email_from"), emails, msg.as_string())
	mail_obj.quit()


def sendNotification(ch, method, properties, body):
	try:
		decoded = body.decode('utf-8')
		req_body = json.loads(decoded)
		emails = []
		for order in req_body["orders"]:
			sqlcursor =  mysqldb.cursor()
			sqlcursor.execute("SELECT * FROM orders o, users u WHERE o.customerId=u.customerId AND o.orderId={orderId}".format(orderId=order["orderId"]))
			order_details = sqlcursor.fetchall()
			print(order_details)
			emails.append(order_details[0].email)
		sendEmail(emails, req_body["status"])

	except Exception as e:
		print(e)



rabbitMQHost = os.getenv("RABBITMQ_HOST") or "rabbitmq"
rabbitMQ = pika.BlockingConnection(
	pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toNotifier')
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
rabbitMQChannel.basic_consume(queue='toNotifier', on_message_callback=sendNotification, auto_ack=False)
rabbitMQChannel.start_consuming()
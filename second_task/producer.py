from random import choice
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from faker import Faker
import pika


from config.models import Contact
from customlogger import logger
import config.connect_db


fake = Faker()


credentials = pika.PlainCredentials("guest", "guest")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672, credentials=credentials)
)
channel = connection.channel()


exchange = "web_08_exch"
queues = ["sms_", "email_"]


channel.exchange_declare(exchange=exchange, exchange_type="topic")


try:
    channel.queue_declare(queue=queues[0], durable=True)
    channel.queue_bind(exchange=exchange, queue=queues[0], routing_key="sms_")
except Exception as e:
    logger.log(f"Error while setting up SMS queue: {e}")

try:
    channel.queue_declare(queue=queues[1], durable=True)
    channel.queue_bind(exchange=exchange, queue=queues[1], routing_key="email_")
except Exception as e:
    logger.log(f"Error while setting up Email queue: {e}")


def create_tasks(numbers: int = 0) -> None:
    """
    Generates fake contacts and sends them to the queue RabbitMQ.

    Args:
        numbers (int): The number of contacts to create.

    Returns:
        None
    """
    try:
        for _ in range(numbers):
            task = Contact(
                fullname=fake.name(), email=fake.email(), phone_num=fake.phone_number()
            ).save()

            channel.basic_publish(
                exchange=exchange,
                routing_key=choice(queues),
                body=str(task.id).encode(),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )
        connection.close()
        logger.log("Tasks created and sent successfully.")
    except Exception as e:
        logger.log(f"Error while creating tasks: {e}")


if __name__ == "__main__":
    create_tasks(10)

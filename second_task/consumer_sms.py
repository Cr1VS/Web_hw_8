from datetime import datetime
import sys
import os


import pika


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from config.models import Contact
from custom_logger import logger
import config.connect_db


def sms_notification(task: Contact) -> bool:
    """
    Sends an SMS notification to the contact.

    Args:
        task (Contact): The contact to send the notification to.

    Returns:
        bool: True if the SMS notification was successfully sent, False otherwise.
    """
    try:
        # Simulating sending an SMS notification
        logger.log(f"SMS successfully delivered to {task.phone_num}")
        return True
    except Exception as e:
        logger.log(f"Error during SMS delivery: {e}", level=40)
        return False


def callback(ch, method, properties, body) -> None:
    """
    Callback function to process messages from the RabbitMQ queue.

    Args:
        ch: The RabbitMQ channel connection.
        method: The message method.
        properties: The message properties.
        body: The message body.

    Returns:
        None
    """
    try:
        pk = body.decode()
        task = Contact.objects(id=pk, logic_field=False).first()
        if task:
            result = sms_notification(task)
            if result:
                task.update(set__logic_field=True, set__date_of=datetime.now())
            else:
                logger.log("Failed during SMS delivery!", level=40)
        else:
            logger.log("Empty data, I can't proceed further!", level=40)
    except Exception as e:
        logger.log(f"Error processing message: {e}", level=40)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    """
    Main function to consume messages from the RabbitMQ queue.
    """
    try:
        credentials = pika.PlainCredentials("guest", "guest")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="localhost", port=5672, credentials=credentials
            )
        )
        channel = connection.channel()

        queue = "sms_"
        channel.queue_declare(queue=queue, durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=callback)

        logger.log(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.log("Consumer interrupted by user.", level=40)
        sys.exit(0)
    except Exception as e:
        logger.log(f"Error in main function: {e}", level=40)
        sys.exit(1)


if __name__ == "__main__":
    main()

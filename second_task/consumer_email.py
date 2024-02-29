from datetime import datetime
import sys
import os


import pika


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from config.models import Contact
from customlogger import logger
import config.connect_db


def email_notification(task: Contact) -> bool:
    """
    Sends an email notification to the contact.

    Args:
        task (Contact): The contact to send the notification to.

    Returns:
        bool: True if the email notification was successfully sent, False otherwise.
    """
    try:
        # Simulating sending an email notification
        logger.log(f"Email successfully delivered to {task.email}")
        return True
    except Exception as e:
        logger.error(f"Error during email delivery: {e}")
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
            result = email_notification(task)
            if result:
                task.update(set__logic_field=True, set__date_of=datetime.now())
            else:
                logger.error("Failed during email delivery!")
        else:
            logger.error("Empty data, I can't proceed further!")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

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

        queue = "email_"
        channel.queue_declare(queue=queue, durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=callback)

        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.warning("Consumer interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

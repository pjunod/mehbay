import logging
import pika

mq_user = "user"
mq_pass = "password"

credentials = pika.PlainCredentials(mq_user, mq_pass)

logger = logging.getLogger


def create_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        'localhost',
        5672,
        '/',
        credentials
        ))
    channel = connection.channel()
    channel.queue_declare(queue='bids')
    connection.close()


def get_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        'localhost',
        5672,
        '/',
        credentials
        ))
    channel = connection.channel()
    return channel
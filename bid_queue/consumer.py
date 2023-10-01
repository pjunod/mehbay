import pika, sys, os
import logging
sys.path.append('../')

import db
import mq
import ops 

db.DB_NAME = "../app.db"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
mq_user = "user"
mq_pass = "password"

credentials = pika.PlainCredentials(mq_user, mq_pass)


def main():
    # connection = pika.BlockingConnection(pika.ConnectionParameters(
    #     host='localhost',
    #     credentials=credentials
    # ))
    # channel = connection.channel()
    channel = mq.get_queue()

    channel.queue_declare(queue='bids')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        item,bid,user,qid = body.decode().split(',')
        ackquery = """INSERT INTO bid_ack (qid,result) VALUES (?, ?)"""
        ret = ops.bid(item, bid, user)
        dbconn = db.get_db()
        with dbconn:
            dbconn.execute(ackquery, [qid,ret])
        dbconn.close()


    channel.basic_consume(queue='bids', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
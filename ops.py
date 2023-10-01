from flask_smorest import abort
import logging
import uuid

import db
import mq

logger = logging.getLogger()


def create_user(username):
    conn = db.get_db()
    query = """INSERT INTO users (username) VALUES (?)"""
    with conn:
        try:
            conn.execute(query, [username])
            return True
        except Exception as e:
            logger.debug("DB exception creating user: [%s] % e")
            abort(
                400,
                message="Error creating user"
            )
    conn.close()


def create_item(username, name, desc, price=0.0):
    conn = db.get_db()
    query = """INSERT INTO items (user, name, desc, price) VALUES (?, ?, ?, ?)"""
    with conn:
        try:
            conn.execute(query, [username, name, desc, price])
            # return conn.lastrowid
            return True
        except:
            abort(
                500,
                message="Unknown error occurred saving to DB"
            )
        finally:
            conn.close()


def get_bid(item):
    conn = db.get_db()
    queryprice = """SELECT bid FROM bids where item_id is (?)"""
    with conn:
        try:
            res = conn.execute(queryprice, [item])
        except:
            res = False
        finally:
            conn.close()
            return res


def bid_publish(item, bid, user):
    logger.debug("Publishing bid to queue")
    m = mq.get_queue()
    qid = str(uuid.uuid4())
    payload = f"{item},{bid},{user},{qid}"
    m.basic_publish(exchange='', routing_key='bids', body=payload)
    return qid


def bid(item, bid, user):
    logger.debug("Entered bid function")
    conn = db.get_db()
    queryprice = """SELECT bid FROM bids where item_id = ?"""
    logger.debug("item is [%s]" % item)
    with conn:
        try:
            q = conn.execute(queryprice, str(item))
            res = q.fetchall()
            logger.debug("res is [%s]" % res)
        except Exception as e:
            logger.debug("DB Exception: [%s]" % e)
            res = False
    if not res:
        logger.debug("Aborting: no result")
        # abort(
        #     400,
        #     message="Error getting current bid."
        # )
        # conn.close()

    if len(res) > 0:
        logger.debug("bid exists")
        if float(res[0][0]) >= float(bid):
            logger.debug("Bid not high enough")
            ret = False
        else:
            logger.debug("New winning bid")
            querybid = """UPDATE bids SET bid = ?, bid_owner = ? WHERE item_id = ?"""
            with conn:
                try:
                    _ = conn.execute(querybid, [bid, user, item])
                except Exception as e:
                    logger.debug("DB Exception updating bid: [%s]" % e)
                    abort(
                        400,
                        message="Error occurred updating bid"
                    )
            conn.close()
            ret = True
    else:
        querybid = """INSERT into bids (bid, bid_owner, item_id) VALUES (?, ?, ?)"""
        with conn:
            try:
                _ = conn.execute(querybid, [bid, user, item])
            except:
                abort(
                    400,
                    message="Error occurred placing bid"
                )
        conn.close()
        ret = True
    return ret


def bid_ack(qid, ret):
    conn = db.get_db()
    ackquery = """INSERT INTO bid_ack (qid,result) VALUES (?, ?)"""
    with conn:
        try:
            _ = conn.execute(ackquery, [qid, ret])
        except Exception as e:
            logger.debug("DB exception occurred adding bid ack: [%s]" % e)
    conn.close()

    return True


def check_bid_ack(qid):
    conn = db.get_db()
    ackquery = """SELECT result from bid_ack where qid = ?"""
    logger.debug("qid is [%s]" % qid)
    with conn:
        try:
            query = conn.execute(ackquery, [qid])
            result = query.fetchall()
        except Exception as e:
            logger.debug("DB exception polling for bid ack: [%s]" % e)
    conn.close()

    if len(result) == 1:
        return True
    return False


def get_bid_result(qid):
    conn = db.get_db()
    ackquery = """SELECT result from bid_ack where qid = ?"""
    with conn:
        try:
            qres = conn.execute(ackquery, [qid])
            result = qres.fetchall()
        except Exception as e:
            logger.debug("DB exception polling for bid result: [%s]" % e)
    conn.close()

    return result[0][0]

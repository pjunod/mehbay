from flask_smorest import abort
import logging

import db

logger = logging.getLogger()


def create_user(username):
    conn = db.get_db()
    query = """INSERT INTO users (username) VALUES (?)"""
    with conn:
        try:
            conn.execute(query, [username])
            conn.commit()
            # return conn.lastrowid
            return True
        except:
            abort(
                500,
                message="Error creating user"
            )
        finally:
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
        abort(
            400,
            message="Error getting current bid."
        )
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

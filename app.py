from flask import Flask, Response, request, make_response, render_template
from flask_smorest import abort
import logging
import time

import db
import ops

logger = logging.getLogger()

app = Flask(__name__)

with app.app_context():
    db.create_tables


@app.route("/user", methods=['POST'])
def create_user():
    item_data = request.get_json()
    if "username" not in item_data:
        abort(
            400,
            message="Please specify username."
        )
    ret = ops.create_user(**item_data)
    if ret:
        resp = make_response(f"User successfully created: {ret}", 201)
        return resp


@app.route("/item", methods=['POST'])
def create_item():
    item_data = request.get_json()
    if "name" not in item_data or "desc" not in item_data:
        abort(
            400,
            message="Bad request. Ensure 'price', and 'name' are included\
                  in the JSON payload.",
        )
    ret = ops.create_item(**item_data)

    if ret:
        return make_response("Item successfully created", 201)
    else:
        abort(
            400,
            message="Unknown error occurred creating item. Sux 4 u!"
        )


@app.route("/bid", methods=['POST'])
def place_bid():
    '''
    Inputs:
    {
	    "item": 1,
	    "bid": 59.95,
	    "user": 1
    }
    '''
    item_data = request.get_json()

    # res = ops.bid(**item_data)
    bid_id = ops.bid_publish(**item_data)

    count = 0
    while (ops.check_bid_ack(bid_id) is False and count <= 5):
        time.sleep(1)
        count += 1
        logger.debug("count is [%s]" % count)
        logger.debug("polling for bid ack...")

    if count >= 5:
        logger.debug("Ack polling count timed out")
        abort(
            400,
            message="Ack polling timed out"
        )
    res = ops.get_bid_result(bid_id)
    if res:
        return make_response("You're the high bidder!", 200)
    else:
        return make_response("You've been outbid.", 200)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db.create_tables()
    app.run(host="127.0.0.1", port=5005, debug=True)

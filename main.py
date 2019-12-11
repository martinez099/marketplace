import random
import redis
import time
import marketplace

import gevent
from gevent import monkey
monkey.patch_all()


def run(conn, user_id):
    """
    Run a market agent, trying to list and purchase items.

    :param conn: A Redis connection instance.
    :param user_id: An user ID.
    """

    # each user starts with 100 funds
    conn.hset("user:%s" % user_id, "funds", 100)

    # each user starts with 10 items
    conn.sadd("user:%s:inventory" % user_id, *range(1, 11))

    while True:

        # trying to list a random item
        item_id = conn.srandmember("user:%s:inventory" % user_id)
        price = random.randint(1, 100)
        ret = marketplace.list_item(conn, item_id, user_id, price)
        if ret:
            print('user:{} listed item:{} with price {}'.format(user_id, item_id, price))
        elif ret is False:
            print('user:{} could NOT list item:{} with price {}'.format(user_id, item_id, price))

        time.sleep(random.randint(1, 10) / 10)

        # trying to purchase a random item
        item_id = random.randint(1, 10)
        seller_id = random.randint(1, 10)
        price = random.randint(1, 100)
        ret = marketplace.purchase_item(conn, user_id, item_id, seller_id, price)
        if ret:
            print('user:{} purchased item:{} for price {} from user:{}'.format(user_id, item_id, price, seller_id))
        elif ret is False:
            print('user:{} could NOT purchase item:{} for price {} from user:{}'.format(user_id, item_id, price, seller_id))

        time.sleep(random.randint(1, 10) / 10)


if __name__ == '__main__':

    # create a Redis client
    r = redis.StrictRedis(decode_responses=True)

    try:

        # spawn 10 greenlets, each simulating an user
        gevent.joinall([gevent.spawn(run, r, i) for i in range(1, 11)])

    except KeyboardInterrupt:
        pass

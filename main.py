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

    r.hset("user:%s" % user_id, "funds", 100)
    r.sadd("inventory:%s" % user_id, *range(1, 10))

    while True:
        item_id = random.randint(1, 10)
        price = random.randint(1, 100)
        ret = marketplace.list_item(conn, item_id, user_id, price)
        if ret:
            print('user:{} listed item:{} with price {}'.format(user_id, item_id, price))
        elif ret is False:
            print('user:{} could NOT list item:{} with price {}'.format(user_id, item_id, price))

        time.sleep(random.randint(1, 10) / 10)

        item_id = random.randint(1, 10)
        buyer_id = random.randint(1, 10)
        price = random.randint(1, 100)
        ret = marketplace.purchase_item(conn, buyer_id, item_id, user_id, price)
        if ret:
            print('user:{} purchased item:{} for price {} from user:{}'.format(user_id, item_id, price, buyer_id))
        elif ret is False:
            print('user:{} could NOT purchase item:{} for price {} from user:{}'.format(user_id, item_id, price, buyer_id))

        time.sleep(random.randint(1, 10) / 10)


if __name__ == '__main__':
    # r = redis.StrictRedis(host="redis-12000.martin.fmecloudscout.de", port=12000, decode_responses=True)
    r = redis.StrictRedis(decode_responses=True)

    # spawn 100 greenlets, each simulating a user
    gevent.joinall([gevent.spawn(run, r, i) for i in range(1, 100)])

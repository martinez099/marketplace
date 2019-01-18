import random
import redis
import time
import marketplace

import gevent
from gevent import monkey
monkey.patch_all()


def run_user(conn, user_id):

    r.hset("user:%s" % user_id, "funds", 100)
    r.sadd("inventory:%s" % user_id, *range(1, 10))

    while True:
        item_id = random.randint(1, 10)
        price = random.randint(1, 100)
        if marketplace.list_item(conn, item_id, user_id, price):
            print('user{}: listed item:{} with price {}'.format(user_id, item_id, price))

        time.sleep(random.randint(1, 10) / 10)

        item_id = random.randint(1, 10)
        buyer_id = random.randint(1, 10)
        price = random.randint(1, 100)
        if marketplace.purchase_item(conn, buyer_id, item_id, user_id, price):
            print('user{}: purchased item:{} for price {} from user:{}'.format(user_id, item_id, price, buyer_id))

        time.sleep(random.randint(1, 10) / 10)


r = redis.StrictRedis(decode_responses=True)

gevent.joinall([gevent.spawn(run_user, r, i) for i in range(1, 10)])

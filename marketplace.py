import time
import redis


def list_item(conn, item_id, seller_id, price):
    inventory = "inventory:%s" % seller_id
    item = "item:%s.%s" % (item_id, seller_id)
    end = time.time() + 5
    pipe = conn.pipeline()

    while time.time() < end:
        try:
            pipe.watch(inventory)

            if not pipe.sismember(inventory, item_id):
                pipe.unwatch()
                return None

            pipe.multi()
            pipe.zadd("market", {item: price})
            pipe.srem(inventory, item_id)

            pipe.execute()

            return True
        except redis.exceptions.WatchError:
            print('WATCH ERROR for {} in list_item(), retrying ...'.format(inventory))
            pass

    return False


def purchase_item(conn, buyer_id, item_id, seller_id, lprice):
    buyer = "user:%s" % buyer_id
    seller = "user:%s" % seller_id
    item = "item:%s.%s" % (item_id, seller_id)
    inventory = "inventory:%s" % buyer_id
    end = time.time() + 10
    pipe = conn.pipeline()

    while time.time() < end:
        try:
            pipe.watch("market", buyer)

            price = pipe.zscore("market", item)
            funds = pipe.hget(buyer, "funds")
            if not price or not funds:
                pipe.unwatch()
                return None

            if price > lprice or price > int(funds):
                pipe.unwatch()
                return None

            pipe.multi()
            pipe.hincrby(seller, "funds", int(price))
            pipe.hincrby(buyer, "funds", int(-price))
            pipe.sadd(inventory, item_id)
            pipe.zrem("market", item)
            pipe.execute()

            return True
        except redis.exceptions.WatchError:
            print('WATCH ERROR for {} in purchase_item(), retrying ...'.format(buyer))
            pass

    return False



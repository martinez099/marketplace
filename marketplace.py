import time
import redis


def list_item(conn, item_id, seller_id, price):
    """
    Try to list an item on the market.

    :param conn: A Redis instance.
    :param item_id: The ID of the item to list.
    :param seller_id: The ID of the user who wants to sell the item.
    :param price: The price to sell.
    :return: True on success, None on unmet criteria, False on failure.
    """
    if not item_id:
        return

    inventory = "user:%s:inventory" % seller_id
    item = "item:%s.%s" % (item_id, seller_id)
    end = time.time() + 5
    pipe = conn.pipeline()

    # try for 5 seconds
    while time.time() < end:

        try:
            pipe.watch(inventory)

            if not pipe.sismember(inventory, item_id):
                pipe.unwatch()
                return

            pipe.multi()
            pipe.zadd("market", {item: price})
            pipe.srem(inventory, item_id)
            pipe.execute()

            return True
        except redis.exceptions.WatchError:
            print('WATCH ERROR for user:{} in list_item(), retrying ...'.format(seller_id))

    return False


def purchase_item(conn, buyer_id, item_id, seller_id, lprice):
    """
    Try to purchase an item from the market.

    :param conn: A Redis instance.
    :param buyer_id: The ID of the user who wants to buy the item.
    :param item_id: The ID of the item to buy.
    :param seller_id: The ID of the user from who sells the item.
    :param lprice: The max price to buy the item.
    :return: True on success, None on unmet criteria, False on failure.
    """
    if buyer_id == seller_id:
        return

    buyer = "user:%s" % buyer_id
    seller = "user:%s" % seller_id
    item = "item:%s.%s" % (item_id, seller_id)
    inventory = "uesr:%s:inventory" % buyer_id
    end = time.time() + 10
    pipe = conn.pipeline()

    # try for 10 seconds
    while time.time() < end:

        try:
            pipe.watch("market", buyer)

            price = pipe.zscore("market", item)
            funds = pipe.hget(buyer, "funds")
            if not price or not funds:
                pipe.unwatch()
                return

            if price > lprice or price > int(funds):
                pipe.unwatch()
                return

            pipe.multi()
            pipe.hincrby(seller, "funds", int(price))
            pipe.hincrby(buyer, "funds", int(-price))
            pipe.sadd(inventory, item_id)
            pipe.zrem("market", item)
            pipe.execute()

            return True
        except redis.exceptions.WatchError as we:
            print('WATCH ERROR for user:{} in purchase_item(), retrying ...'.format(buyer_id))

    return False

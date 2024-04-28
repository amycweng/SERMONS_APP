from flask import current_app as app
import datetime

class Purchase:
    # Creates a new purchase entry with the given user id, seller id, product id, order id, time of purchase, quantity purchased, price at time of purchase,
    # and date the purchase. No two entries can have the same user id, seller id, product id, and order id at once. The date fulfilled may by None to denote
    #  a yet-to-be fulfilled purchase
    def __init__(self, uid, sid, pid, order_id, time_purchased, quantity, price, date_fulfilled):
        self.uid = uid
        self.sid = sid
        self.pid = pid
        self.order_id = order_id
        self.time_purchased = time_purchased
        self.quantity = quantity
        self.price = price
        self.date_fulfilled = date_fulfilled

    # Returns a purchase entry given the user, product, seller, and order ids
    @staticmethod
    def get(uid,pid,sid,order_id):
        rows = app.db.execute('''
        SELECT uid, sid, pid, order_id, time_purchased, quantity, date_fulfilled
        FROM Purchases
        WHERE uid = :uid AND pid = :pid AND sid =:sid AND order_id = :order_id
        ''',
        uid=uid, pid=pid, sid =sid, order_id = order_id)
        return Purchase(*(rows[0])) if rows else None

    # Returns the (at most) 10 purchases most recent purchases in reverse chronological order by a user after a specified date
    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
        SELECT *
        FROM Purchases
        WHERE uid = :uid
        AND time_purchased >= :since
        ORDER BY time_purchased DESC
        LIMIT 10
        ''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]
    
    # Returns the top 10 purchased products and their associated purchase counts.
    @staticmethod
    def get_top_ten():
        rows = app.db.execute('''
        SELECT pid, COUNT(*)
        FROM Purchases
        GROUP BY pid
        ORDER BY COUNT(*) DESC
        LIMIT 8''')
        top_purchases = []
        for row in rows:
            pid, count = row
            top_purchases.append(pid)
        return top_purchases
    
    # Returns all purchases made from a particular specified seller, sorting in reverse chronological order
    # However, unfulfilled orders will be placed at the top.
    @staticmethod
    def get_all_by_sid(sid):
        rows = app.db.execute('''
        SELECT *
        FROM Purchases
        WHERE sid = :sid
        ORDER BY CASE WHEN date_fulfilled IS NULL THEN 0 ELSE 1 END, time_purchased DESC
        ''',
                              sid=sid)
        return [Purchase(*row) for row in rows]
    
    # Returns total quantities of products ordered in order from highest to lowest for a particular specified seller.
    @staticmethod
    def get_order_counts_by_sid(sid):
        rows = app.db.execute('''
        WITH ProductNames(pid, pname) AS
        (SELECT pid, name FROM Products)
        SELECT pid, pname, SUM(quantity) AS sum
        FROM Purchases NATURAL JOIN ProductNames
        WHERE sid = :sid
        GROUP BY pid, pname
        ORDER BY sum DESC
        ''',
                              sid=sid)
        return rows
    
    # Returns a list of the total number of orders for a particular seller over each month for the last 3 years. If no product is specified, the numbers of orders are
    # summed up for all products. Otherwise, if a product is specified, then the numbers of orders are only summed up for that particular product.
    @staticmethod
    def get_num_orders_per_month(sid, pid=None):
        today = datetime.date.today()
        current_year = today.year
        current_month = today.month
        year_range = 3
        if not pid:
            rows = app.db.execute('''
            WITH RECURSIVE months AS (
                SELECT 1 AS month
                UNION ALL
                SELECT month+1 FROM months WHERE month+1 <= 12
            ),
            years AS (
                SELECT :current_year-:year_range+1 AS year
                UNION ALL
                SELECT year+1 FROM years WHERE year+1 <= :current_year               
            )
            SELECT monthYears.month, monthYears.year, COALESCE(count,0)
            FROM (
                SELECT month, year, COUNT(order_id) AS count
                FROM (
                    SELECT sid, order_id, EXTRACT(MONTH FROM time_purchased) AS month, EXTRACT(YEAR FROM time_purchased) AS year
                    FROM Purchases
                ) AS OrderMonths
                WHERE sid = :sid
                GROUP BY month, year
            ) AS OrderMonths
            RIGHT JOIN (
                SELECT month, year
                FROM months CROSS JOIN years
                ORDER BY year, month
            ) AS monthYears
            ON monthYears.month = OrderMonths.month
            AND monthYears.year = OrderMonths.year
            WHERE (monthYears.year = :current_year AND monthYears.month <= :current_month)
            OR (monthYears.year = :current_year-:year_range AND monthYears.month > :current_month)
            OR (monthYears.year < :current_year AND monthYears.year > :current_year-:year_range)
            ORDER BY monthYears.year, monthYears.month
            ''',
                                sid=sid,
                                current_year=current_year,
                                current_month=current_month,
                                year_range=year_range)
        else:
            rows = app.db.execute('''
            WITH RECURSIVE months AS (
                SELECT 1 AS month
                UNION ALL
                SELECT month+1 FROM months WHERE month+1 <= 12
            ),
            years AS (
                SELECT :current_year-:year_range+1 AS year
                UNION ALL
                SELECT year+1 FROM years WHERE year+1 <= :current_year               
            )
            SELECT monthYears.month, monthYears.year, COALESCE(count,0)
            FROM (
                SELECT month, year, COUNT(order_id) AS count
                FROM (
                    SELECT sid, pid, order_id, EXTRACT(MONTH FROM time_purchased) AS month, EXTRACT(YEAR FROM time_purchased) AS year
                    FROM Purchases
                ) AS OrderMonths
                WHERE sid = :sid
                AND pid = :pid
                GROUP BY month, year
            ) AS OrderMonths
            RIGHT JOIN (
                SELECT month, year
                FROM months CROSS JOIN years
                ORDER BY year, month
            ) AS monthYears
            ON monthYears.month = OrderMonths.month
            AND monthYears.year = OrderMonths.year
            WHERE (monthYears.year = :current_year AND monthYears.month <= :current_month)
            OR (monthYears.year = :current_year-:year_range AND monthYears.month > :current_month)
            OR (monthYears.year < :current_year AND monthYears.year > :current_year-:year_range)
            ORDER BY monthYears.year, monthYears.month
            ''',
                                sid=sid,
                                pid=pid,
                                current_year=current_year,
                                current_month=current_month,
                                year_range=year_range)
        return rows

    # Updates a purchase as fulfilled by setting a new fulfillment date
    @staticmethod
    def fulfill(uid, sid, pid, order_id, date_fulfilled):
        try:
            rows = app.db.execute("""
            UPDATE Purchases
            SET date_fulfilled=:date_fulfilled
            WHERE uid=:uid AND sid=:sid AND pid=:pid AND order_id=:order_id
            """,
                                  uid=uid,
                                  sid=sid,
                                  pid=pid,
                                  order_id=order_id,
                                  date_fulfilled=date_fulfilled
                                )
            return date_fulfilled
        except Exception as e:
            print(str(e))

    # Returns all purchases by a user within a single order specified by the order id
    @staticmethod
    def get_order(uid, order_id):
        rows = app.db.execute('''
        SELECT *
        FROM PURCHASES
        WHERE uid = :uid AND order_id = :order_id
        ''', uid = uid, order_id=order_id)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_total_price_order(uid, order_id): # sums up quantity * price for an order
        rows = app.db.execute("""
        WITH C(total) AS
            (SELECT quantity * price FROM Purchases
            WHERE uid = :uid AND Purchases.order_id = :order_id)
        SELECT SUM(total)
        FROM C
        """,
        uid=uid, order_id=order_id)
        return float(rows[0][0]) if rows and rows[0][0] is not None else 0.0
    
    @staticmethod
    def get_fulfillment_status(uid, order_id):
        fulfilled = True
        #loops through date fulfilled to get overall order status
        rows = app.db.execute('''
        SELECT date_fulfilled
        FROM Purchases
        WHERE uid = :uid AND Purchases.order_id = :order_id
        ''',
                              uid=uid, order_id=order_id)
        for row in rows:
            if row[0] == None:
                fulfilled = False
        if fulfilled:
            return "Fulfilled"
        else:
            return "Not fulfilled"

    @staticmethod
    def get_unique_orders_by_uid(uid):
        #returns orders, list of products, price, fulfillment status
        rows = app.db.execute('''
        SELECT DISTINCT order_id
        FROM Purchases
        WHERE uid = :uid
        ''',
                              uid=uid)
        unique_orders = []
        for row in rows:
            order_id = row[0]
            total_price = Purchase.get_total_price_order(uid, order_id)
            row_as_list = list(row) #make list so we can append results
            row_as_list.append(Purchase.get_order_products(uid, order_id))
            row_as_list.append(total_price)
            row_as_list.append(Purchase.get_fulfillment_status(uid, order_id))
            unique_orders.append(row_as_list)
        return unique_orders

    @staticmethod
    def get_order_products(uid, order_id):
        rows = app.db.execute('''
        SELECT name, Products.pid
        FROM PURCHASES, Products
        WHERE uid = :uid AND order_id = :order_id AND Purchases.pid = Products.pid
        ''', uid = uid, order_id=order_id)
        name_list = []
        for row in rows:
            name_list.append([str(row[0]), row[1]])
        #returns list of lists where inner list[0] is name, list[1] is id
        return name_list
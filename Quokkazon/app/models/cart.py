from flask import current_app as app

class CartItem:
    def __init__(self, uid, sid, pid, quantity, price, saved_for_later = 0):
        self.uid = uid
        self.sid = sid
        self.pid = pid
        self.quantity = quantity
        self.price = price
        self.saved_for_later = saved_for_later

    @staticmethod
    def get(uid, sid, pid):
        rows = app.db.execute('''
SELECT *
FROM Cart
WHERE uid = :uid AND sid = :sid AND pid = :pid
''',
                              uid=uid,
                              sid = sid,
                              pid = pid)
        return CartItem(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT uid, Cart.sid, Cart.pid, Cart.quantity, price, saved_for_later
FROM Cart, Inventory
WHERE uid = :uid AND Cart.sid = Inventory.sid AND Cart.pid = Inventory.pid
''', uid = uid)
        return [CartItem(*row) for row in rows]
    
    @staticmethod
    def get_total_price(uid): #sums quantity * price to get total for cart
        rows = app.db.execute("""
        WITH C(total) AS
            (SELECT Cart.quantity * price FROM Cart, Inventory
            WHERE uid = :uid AND Cart.sid = Inventory.sid AND Cart.pid = Inventory.pid AND saved_for_later = B'0')
        SELECT SUM(total)
        FROM C
        """,
        uid=uid)
        return float(rows[0][0]) if rows and rows[0][0] is not None else 0.0
    
    @staticmethod
    def add_item(uid, sid, pid, quantity, saved_for_later): #new entry in cart
        rows = app.db.execute("""
        INSERT INTO CART(uid, sid, pid, quantity, saved_for_later)
        VALUES(:uid, :sid, :pid, :quantity, :saved_for_later)
        """,
        uid=uid,
        sid = sid,
        pid = pid,
        quantity = quantity,
        saved_for_later = saved_for_later)
        return
    
    @staticmethod
    def remove_item(uid, sid, pid): #removes item from cart table
        rows = app.db.execute("""
        DELETE FROM CART
        WHERE uid = :uid AND sid = :sid AND pid = :pid
        """,
        uid=uid,
        sid=sid,
        pid=pid)
        return
    
    @staticmethod
    def update_quantity(uid, sid, pid, quantity):
        rows = app.db.execute("""
        UPDATE CART
        SET quantity = :quantity
        WHERE uid = :uid AND sid = :sid AND pid = :pid
        """,
        uid=uid,
        sid=sid,
        pid=pid,
        quantity=quantity)
        return

    @staticmethod
    def submit(uid): #removes from cart table, is called along other fxns
        rows = app.db.execute("""
        DELETE FROM CART
        WHERE uid = :uid AND saved_for_later = B'0'
        """,
        uid=uid)
        return

    @staticmethod
    def newOrderId(uid): #ensures new order id is highest
        rows = app.db.execute("""
        SELECT MAX(order_id)
        FROM PURCHASES
        """, uid = uid)
        return int(rows[0][0]+1) if rows and rows[0][0] is not None else 1

    @staticmethod #called along submit to put info from cart as a new purchase
    def newPurchase(uid, sid, pid, order_id, quantity, price, date_fulfilled):
        rows = app.db.execute("""
        INSERT INTO PURCHASES(uid, sid, pid, order_id, quantity, price, date_fulfilled)
        VALUES(:uid, :sid, :pid, :order_id, :quantity, :price, :date_fulfilled)
        """, uid = uid, sid = sid, pid = pid, order_id=order_id, quantity = quantity, price = price, date_fulfilled= date_fulfilled
        )
        return
    
    @staticmethod
    def get_all_sids(uid): #find each seller for items in cart
        rows = app.db.execute('''
        SELECT DISTINCT sid
        FROM Cart
        WHERE uid = :uid
        ''', uid = uid)
        return [row[0] for row in rows]

    @staticmethod
    def increase_balances(sids, uid, multiplier): #update user balance for each seller id in cart
        for sid in sids:
            rows = app.db.execute('''
            WITH C(total) AS
            (SELECT Cart.quantity * price FROM Cart, Inventory
            WHERE uid = :uid AND Cart.sid = :sid AND Cart.pid = Inventory.pid AND saved_for_later = B'0')
            UPDATE USERS
            SET balance = balance + (SELECT SUM(total) FROM C) * :multiplier
            WHERE id = :sid
            ''', sid = sid, uid = uid, multiplier = multiplier)
        return

    @staticmethod
    def decrease_balance(uid, totalPrice): #subtract total cart price from balance on order
        rows = app.db.execute('''
        UPDATE USERS
        SET balance = balance - :totalPrice
        WHERE id = :uid
        ''', uid = uid, totalPrice = totalPrice)
        return

    @staticmethod
    def decrease_stock(sid, uid, pid): #update user balance for each seller id in cart
        rows = app.db.execute('''
        WITH C(cart_quantity) AS
        (SELECT Cart.quantity FROM Cart, Inventory
        WHERE uid = :uid AND Cart.sid = :sid AND Cart.pid = :pid AND Inventory.pid = Cart.pid AND Inventory.sid = Cart.sid AND saved_for_later = B'0')
        UPDATE INVENTORY
        SET num_for_sale = num_for_sale - (SELECT cart_quantity FROM C)
        WHERE sid = :sid AND Inventory.pid = :pid;

        WITH C(cart_quantity) AS
        (SELECT Cart.quantity FROM Cart, Inventory
        WHERE uid = :uid AND Cart.sid = :sid AND Cart.pid = :pid AND Inventory.pid = Cart.pid AND Inventory.sid = Cart.sid AND saved_for_later = B'0')
        UPDATE INVENTORY
        SET quantity = quantity - (SELECT cart_quantity FROM C)
        WHERE sid = :sid AND Inventory.pid = :pid;
        ''', sid = sid, uid = uid, pid = pid)
        return

    @staticmethod
    def move_to_cart(uid, sid, pid):
        rows = app.db.execute("""
        UPDATE CART
        SET saved_for_later = B'0'
        WHERE uid = :uid AND sid = :sid AND pid = :pid
        """,
        uid=uid,
        sid=sid,
        pid=pid)
        return

    @staticmethod
    def move_to_saved(uid, sid, pid):
        rows = app.db.execute("""
        UPDATE CART
        SET saved_for_later = B'1'
        WHERE uid = :uid AND sid = :sid AND pid = :pid
        """,
        uid=uid,
        sid=sid,
        pid=pid)
        return

    @staticmethod
    def compare(uid, total):
        if total == CartItem.get_total_price(uid):
            return False
        else:
            return True

    @staticmethod
    def check_stocks(uid): #check if quantity > stock
        inStock = True
        rows = app.db.execute('''
        SELECT Cart.quantity, num_for_sale
        FROM Cart, Inventory
        WHERE uid = :uid AND Cart.sid = Inventory.sid AND Cart.pid = Inventory.pid
        ''', uid = uid)
        for row in rows:
            if row[0] > row[1]:
                inStock = False
        return inStock

    
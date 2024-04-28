from flask import current_app as app

class Inventory:
    # Creates an inventory entry with seller id, product id, quantity in the inventory, number available for sale, and price
    def __init__(self, sid, pid, quantity, num_for_sale, price):
        self.sid = sid
        self.pid = pid
        self.quantity = quantity
        self.num_for_sale = num_for_sale
        self.price = price

    # Return all inventory entries for a particular seller
    @staticmethod
    def get_all_by_sid(sid):
        rows = app.db.execute('''
        SELECT *
        FROM Inventory
        WHERE sid = :sid
        ''', sid=sid)
        return [Inventory(*row) for row in rows]

    @staticmethod
    def get(sid, pid):
        rows = app.db.execute('''
        SELECT *
        FROM Inventory
        WHERE sid = :sid AND pid = :pid
        ''', sid=sid, pid=pid)
        return rows[0]

    # Return all inventory entries for a particular product owned by any seller
    @staticmethod
    def get_all_by_pid(pid):
        rows = app.db.execute('''
        SELECT *
        FROM Inventory
        WHERE pid = :pid
        ''', pid=pid)
        return [Inventory(*row) for row in rows]
    
    # Return whether the product associated with the given product id is contained within the given seller's own inventory, including if the item is not in stock
    @staticmethod
    def in_inventory(sid, pid):
        rows = app.db.execute('''
        SELECT *
        FROM Inventory
        WHERE sid = :sid
        AND pid = :pid 
        ''', sid=sid, pid=pid)
        return len(rows) > 0

    # Returns the entire inventory table
    @staticmethod
    def get_all():
        rows = app.db.execute('''
        SELECT *
        FROM Inventory
        ''')
        return [Inventory(*row) for row in rows]
    
    # Edits a row in the inventory for the given product id and seller id, updating the values to the new provided quantity, number for sale, and price
    @staticmethod
    def edit(pid, sid, quantity, num_for_sale, price):
        try:
            rows = app.db.execute("""
            UPDATE Inventory
            SET quantity=:quantity, num_for_sale=:num_for_sale, price=:price
            WHERE pid=:pid AND sid=:sid
            """,
                                  pid=pid,
                                  sid=sid, 
                                  quantity=quantity,
                                  num_for_sale=num_for_sale,
                                  price=price
                                )
            return pid, sid
        except Exception as e:
            print(str(e))
    
    # Adds a new entry to the inventory with all the new values provided.
    @staticmethod
    def add(pid, sid, quantity, num_for_sale, price):
        try:
            rows = app.db.execute("""
            INSERT INTO Inventory(pid, sid, quantity, num_for_sale, price)
            VALUES(:pid, :sid, :quantity, :num_for_sale, :price)
            """,
                                  pid=pid,
                                  sid=sid,
                                  quantity=quantity,
                                  num_for_sale=num_for_sale,
                                  price=price
                                )
            return pid, sid
        except Exception as e:
            print(str(e))

    # Deletes an entry from the inventory corresponding to the provided product and seller id
    @staticmethod
    def delete(pid, sid):
        try:
            rows = app.db.execute("""
            DELETE FROM Inventory
            WHERE pid=:pid AND sid=:sid
            """,
                                  pid=pid,
                                  sid=sid
                                )
            return pid, sid
        except Exception as e:
            print(str(e))
from flask import current_app as app

class Seller:
    def __init__(self, sid):
        self.sid = sid

    # Returns a seller object corresponding to the seller id if that id exists in the Seller table.
    @staticmethod
    def get(sid):
        rows = app.db.execute('''
        SELECT *
        FROM Seller
        WHERE sid = :sid
        ''',
        sid=sid)
        return Seller(*(rows[0])) if rows else None

    # Return the User object corresponding to a seller ID.
    @staticmethod
    def find(sid):
        rows = app.db.execute('''
        SELECT *
        FROM Users
        WHERE id = :sid
        ''',
        sid=sid)
        return ((rows[0])) if rows else None
    
    # Returns whether a user is a seller or not
    @staticmethod
    def is_seller(user):
        if hasattr(user,"id"):
            return Seller.get(user.id) != None
        return False


    # Method to check if a seller has any products
    @staticmethod
    def has_products(sid):
        rows = app.db.execute('''
        SELECT *
        FROM SellerFeedback
        WHERE sid = :sid
        ''',
        sid=sid)
        return True if rows else False


    # Method to add non-sellers to the seller table. (Register as sellers)
    @staticmethod
    def add_seller(id):
        try:
            app.db.execute("""
            INSERT INTO Seller(sid)
            VALUES(:id)
            RETURNING sid
            """,
                                  id=id)
            return None
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None


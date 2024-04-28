from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import *

from .. import login

class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, phone_number, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.phone_number = phone_number
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
                SELECT password, id, email, firstname, lastname, address, phone_number, balance
                FROM Users
                WHERE email = :email
                """,
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, firstname, lastname, address, password, phone_number):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, firstname, lastname, address, password, phone_number, balance)
VALUES(:email, :firstname, :lastname,:address,:password,:phone_number,0)
RETURNING id
""",
                                  email=email,
                                  firstname=firstname, 
                                  lastname=lastname,
                                  address=address,
                                  password=generate_password_hash(password),
                                  phone_number=phone_number
                                  )
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address, phone_number, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None


# Method to update a user's info
    @staticmethod
    def update_user_info(user_id, email, firstname, lastname, address, phone_number, password):
        try:
            # Update query to modify user details in the database
            app.db.execute(
                "UPDATE Users SET email = :email, firstname = :firstname, lastname = :lastname, "
                "address = :address, phone_number = :phone_number, password = :password WHERE id = :user_id",
                user_id=user_id, email=email, firstname=firstname, 
                lastname=lastname, address=address, phone_number=phone_number, password= generate_password_hash(password))
            return True
        except Exception as e:
            # Log the exception e
            return False


    # @staticmethod
    # def top_up(user_id, balance, added_money):
    #     try:
    #         # Update query to modify user details in the database
    #         new_bal = balance + added_money
    #         app.db.execute(
    #             "UPDATE Users SET balance = :balance WHERE id = :user_id",
    #             user_id=user_id, balance= new_bal)
    #         print("Success!")
    #         return True
    #     except Exception as e:
    #         # Log the exception e
    #         print("Failure!")
    #         return False
 
 # Method to top-up a user's balance
    @staticmethod
    def top_up(user_id, balance, added_money):
        # Update query to modify user details in the database
        try:
            added_decimal = Decimal(added_money)
            if added_decimal < 0:
                print("Added amount can't be negative!")
                return False
            new_bal = balance + added_decimal
            try:
                app.db.execute(
                    "UPDATE Users SET balance = :balance WHERE id = :user_id",
                    user_id=user_id, balance= new_bal)
                print("Success!")
                return True
            except:
                print("Error: balance out of range")
                return False
        except:
            print('Added amount must be a decimal!')
            return False
        

    @staticmethod
    def get_balance(user_id):
        rows = app.db.execute("""
        SELECT balance
        FROM Users
        WHERE id = :id
        """,
        id = user_id)
        return float(rows[0][0]) if rows and rows[0][0] is not None else 0.0


    @staticmethod
    def get_all():
        rows = app.db.execute('''
        SELECT id, email, firstname, lastname, address, phone_number, balance
        FROM Users
        ''')
        return [User(*row) for row in rows]
 
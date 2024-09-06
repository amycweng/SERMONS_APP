from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import *

from .. import login

class User(UserMixin):
    def __init__(self, id, email, username):
        self.id = id
        self.email = email
        self.username = username

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
                SELECT password, id, email, username
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
    def register(email, username,password):
        try:
            rows = app.db.execute("""
                INSERT INTO Users(email, username, password)
                VALUES(:email, :username, :password)
                RETURNING id
                """,
                email=email,
                username=username, 
                password=generate_password_hash(password)
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
            SELECT id, email, username
            FROM Users
            WHERE id = :id
            """,
            id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def get_activity(id):
        rows = app.db.execute("""
            SELECT table_name, operation, old_data, new_data, changed_at
            FROM audit_log
            WHERE changed_by = :changed_by
            ORDER BY changed_by asc 
            """,
            id=id)

        return rows
from flask import current_app as app

class Category:
    def __init__(self, cid, name, image):
        self.cid = cid
        self.name = name
        self.image = image

    #Get all categories
    @staticmethod
    def get_all():
        rows = app.db.execute('''
        SELECT *
        FROM Category
        ''')
        return [Category(*row) for row in rows]
    
    #Get the name of a category entry
    def get_name(cid):
        rows = app.db.execute('''
        SELECT *
        FROM Category
        WHERE cid = :cid
        ''', cid=cid)
        return Category(*(rows[0])) if rows is not None else None
    
from flask import current_app as app

class Product:
    def __init__(self, pid, name, description, image, altTxt, createdAt, updatedAt, cid, sid):
        self.pid = pid
        self.name = name
        self.description = description
        self.image = image
        self.altTxt = altTxt
        self.CreatedAt = createdAt
        self.UpdatedAt = updatedAt
        self.cid = cid
        self.sid = sid

    #Returns one product entry by pid
    @staticmethod
    def get(pid):
        rows = app.db.execute('''
        SELECT *
        FROM Products
        WHERE pid = :pid
        ''', pid=pid)
        return Product(*(rows[0])) if rows is not None else None
    
    #Returns one product entry by name
    @staticmethod
    def get_by_name(name):
        rows = app.db.execute('''
        SELECT *
        FROM Products
        WHERE name = :name
        ''', name=name)
        if rows:
            return Product(*(rows[0]))
        else:
            return None

    #Returns all product entries
    @staticmethod
    def get_all():
        rows = app.db.execute('''
        SELECT *
        FROM Products
        ''')
        return [Product(*row) for row in rows]
    
    #Returns all product entries a-z
    @staticmethod
    def get_az():
        rows = app.db.execute('''
        SELECT *
        FROM Products
        ORDER BY Products.name
        ''')
        return [Product(*row) for row in rows]
    
    #Returns all product entries z-a
    @staticmethod
    def get_za():
        rows = app.db.execute('''
        SELECT *
        FROM Products
        ORDER BY Products.name DESC
        ''')
        return [Product(*row) for row in rows]
    
    #Returns all product entries based on category
    @staticmethod
    def get_all_by_cat(cid):
        rows = app.db.execute('''
        SELECT *
        FROM Products
        WHERE cid = :cid
        ''', cid=cid)
        return [Product(*row) for row in rows]
    
    #Returns the name of a product entry based on pid
    @staticmethod
    def get_name(pid):
        product = Product.get(pid)
        if product != None:
            return product.name
        else:
            return None
        
    #Creates a new pid for product
    @staticmethod
    def newPID():
        rows = app.db.execute("""
        SELECT MAX(pid)
        FROM Products
        """)
        return rows
        
    #Inserts product values into the product table as a new entry 
    @staticmethod 
    def add_product(pid, name, description, image, altTxt, createdAt, updatedAt, cid, sid):
        app.db.execute("""
        INSERT INTO Products(pid, name, description, image, altTxt, createdAt, updatedAt, cid, sid)
        VALUES(:pid, :name, :description, :image, :altTxt, :createdAt, :updatedAt, :cid, :sid)
        """, 
        pid = pid, 
        name=name, 
        description=description, 
        image=image, altTxt=altTxt, 
        createdAt=createdAt, 
        updatedAt=updatedAt,
        cid=cid,
        sid=sid
        )
        return 
    
    #Get all product entries by creator 
    @staticmethod
    def get_all_by_sid(sid):
        rows = app.db.execute('''
        SELECT pid
        FROM Products
        WHERE sid = :sid
        ''', sid=sid)
        return [row[0] for row in rows]
    
    #Updates an existing product based on their pid and sid. 
    @staticmethod
    def edit(pid, name, description, image, altTxt, updatedAt, cid, sid):
        try:
            rows = app.db.execute("""
            UPDATE Products
            SET name=:name, description=:description, image=:image, altTxt=:altTxt, updatedAt=:updatedAt, cid=:cid
            WHERE pid=:pid AND sid=:sid
            """,
            pid = pid, 
            name=name, 
            description=description, 
            image=image, altTxt=altTxt, 
            updatedAt=updatedAt,
            cid=cid,
            sid=sid)
        except Exception as e:
            print(str(e))
    
class ProductRating:
    def __init__(self, pid, name, description, image, altTxt, createdAt, updatedAt, cid, rating):
        self.pid = pid
        self.name = name
        self.description = description
        self.image = image
        self.altTxt = altTxt
        self.CreatedAt = createdAt
        self.UpdatedAt = updatedAt
        self.cid = cid
        self.rating = rating
        
    # Gets all enries of joined table of product and product feedback to have access to ratings
    def all_ratings():
        rows = app.db.execute('''
        SELECT p.pid, p.name, p.description, p.image, p.altTxt, p.createdAt, p.updatedAt, p.cid, AVG(f.rating) as avg_rating
        FROM Products as p
        JOIN ProductFeedback as f ON p.pid = f.pid
        GROUP BY p.pid, p.name, p.description, p.image, p.altTxt, p.createdAt, p.updatedAt, p.cid
        ORDER BY avg_rating DESC;
        ''')
        return [ProductRating(*row) for row in rows]
    
    #Gets product entries based on category ordered descending on ratings
    def all_ratings_cid(cid):
        rows = app.db.execute('''
        SELECT p.pid, p.name, p.description, p.image, p.altTxt, p.createdAt, p.updatedAt, p.cid, AVG(f.rating) as avg_rating
        FROM Products as p
        JOIN ProductFeedback as f ON p.pid = f.pid
        WHERE p.cid = :cid
        GROUP BY p.pid, p.name, p.description, p.image, p.altTxt, p.createdAt, p.updatedAt, p.cid
        ORDER BY avg_rating DESC;
        ''', cid=cid)
        return [ProductRating(*row) for row in rows]
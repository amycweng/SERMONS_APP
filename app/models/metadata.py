from flask import current_app as app

class Metadata:
    def __init__(self,tcpID,estc,stc,title,authors,publisher,pubplace,subject_headings,pubyear):
        # id,estc,stc,title,authors,publisher,pubplace,subject_headings,date
        self.tcpID = tcpID 
        self.estc = estc 
        self.stc = stc
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.pubplace = pubplace
        self.subject_headings = subject_headings
        self.pubyear = pubyear 

    @staticmethod
    def all_tcpIDs(): 
        return app.db.execute('SELECT tcpID FROM Sermon')
    
    @staticmethod
    def get_by_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT *
        FROM Sermon as s 
        WHERE s.tcpID = :tcpID 
        ''',
        tcpID=tcpID)
        return [Metadata(*row) for row in rows]
    
    @staticmethod
    def get_all():
        # current user's ratings and reviews for all products 
        rows = app.db.execute('''
        SELECT *
        FROM Sermon as s 
        ''')
        return [Metadata(*row) for row in rows]
    
    @staticmethod
    def get_author_counts():
        # current user's ratings and reviews for all products 
        rows = app.db.execute('''
        SELECT *
        FROM Author 
        ''')
        author_counts = [(row[0],len(row[1].split("; "))) for row in rows]
        return author_counts


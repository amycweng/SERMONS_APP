from flask import current_app as app

class Sermon:
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
        return app.db.execute('SELECT id FROM Sermon')
    
    @staticmethod
    def get_by_tcpID(tcpID):
        # current user's ratings and reviews for all products 
        rows = app.db.execute('''
        SELECT *
        FROM Sermon as s 
        WHERE s.id = tcpID 
        ORDER BY s.pubyear ASC
        ''',
        tcpID=tcpID)
        return [Sermon(*row) for row in rows]
    
    def get_all():
        # current user's ratings and reviews for all products 
        rows = app.db.execute('''
        SELECT *
        FROM Sermon as s 
        ORDER BY s.pubyear ASC
        ''')
        return [Sermon(*row) for row in rows]


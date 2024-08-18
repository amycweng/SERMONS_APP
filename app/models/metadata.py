from flask import current_app as app

class Metadata:
    def __init__(self,tcpID,estc,stc,title,authors,publisher,pubplace,subject_headings,pubyear,phase):
        self.tcpID = tcpID 
        self.estc = estc 
        self.stc = stc
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.pubplace = pubplace
        self.subject_headings = subject_headings
        self.pubyear = pubyear 
        self.phase = phase 

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
        rows = app.db.execute('''
        SELECT *
        FROM Sermon as s 
        ORDER BY s.pubyear, s.title
        ''')
        return [Metadata(*row) for row in rows]
    
    @staticmethod
    def get_author_counts():
        rows = app.db.execute('''
        SELECT *
        FROM Author 
        ''')
        author_counts = {}
        for a,t in rows: 
            if a not in author_counts: author_counts[a] = 0 
            author_counts[a] += 1 
        author_counts = [(a,num) for a,num in author_counts.items()]
        return author_counts

    @staticmethod
    def get_author_tcpIDs():
        rows = app.db.execute('''
        SELECT *
        FROM Author 
        ''')
        return rows 
    
    @staticmethod
    def get_pubplace_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT *
        FROM Pubplace
        WHERE tcpID = :tcpID 
        ''',tcpID=tcpID)
        return rows

    @staticmethod
    def update_pubplace(old, new):
        rows = app.db.execute('''
        UPDATE Pubplace 
        SET pubplace = :new
        WHERE pubplace = :old 
        ''',
        old=old,
        new=new)
        return rows
    
    @staticmethod
    def get_pubplace():
        rows = app.db.execute('''
        SELECT *
        FROM Pubplace
        ''')
        return rows
    
    @staticmethod
    def get_pubplace_phrase(phrase):
        phrase = "%"+phrase+"%"
        rows = app.db.execute('''
        SELECT *
        FROM Pubplace
        WHERE pubplace LIKE :phrase
        ''',phrase=phrase)
        return rows
     
    @staticmethod
    def get_tcpIDs_by_aut(author):
        rows = app.db.execute('''
        SELECT *
        FROM Author
        WHERE author = :author 
        ''',
        author=author)
        return rows 

    @staticmethod
    def get_aut_by_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT author
        FROM Author
        WHERE tcpID = :tcpID
        ''',
        tcpID=tcpID)
        return rows 

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
    def get_all_for_ORCP():
        rows = app.db.execute('''
        SELECT m.tcpID, a.author, p.pubplace, s.subject_heading
        FROM Sermon as m, Author as a, Pubplace as p, SubjectHeading as s 
        WHERE m.tcpID = a.tcpID 
        AND a.tcpID = p.tcpID
        AND p.tcpID = s.tcpID
        ''')
        return [{'tcpID':m[0],'author': m[1],'pubplace':m[2],'subject_heading':m[3]} for m in rows]
    

    @staticmethod
    def get_by_author(author):
        rows = app.db.execute('''
        SELECT m.tcpID,m.estc,m.stc,m.title,m.authors,m.publisher,m.pubplace,m.subject_headings,m.pubyear,m.phase
        FROM Sermon as m, Author as a
        WHERE m.tcpID = a.tcpID 
        AND a.author = :author
        ORDER BY m.pubyear ASC
        ''', author=author)
        return [Metadata(*row) for row in rows]
    
    @staticmethod
    def get_author_counts():
        rows = app.db.execute('''
        SELECT author, COUNT(author)
        FROM Author 
        GROUP BY author
        ''')
        return rows

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
        SELECT a.author, s.tcpID, s.
        FROM Author as a, Sermon as s
        WHERE a.author = :author 
        AND s.tcpID = a.tcpID
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
    
    @staticmethod
    def get_topics():
        rows = app.db.execute('''
        SELECT t.tcpID, tw.topic_words
        FROM Topics as t 
        INNER JOIN TopicWords as tw 
        ON t.topic = tw.topic_idx                
        ''')
        rows = {t[0]:t[1] for t in rows}
        return rows 
    
    @staticmethod
    def get_section_counts():
        rows = app.db.execute('''
        SELECT section_name, COUNT(*)
        FROM Section 
        GROUP BY section_name
        ''')
        return rows
    
    @staticmethod
    def search_in_titles(phrase):
        k=50
        results = app.vectordb.search_title(phrase,k)
        return results


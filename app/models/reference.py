from flask import current_app as app

class Citation:
    def __init__(self,tcpID,sidx,loc,cidx,citation,outlier,replaced):
        self.tcpID = tcpID 
        self.sidx = sidx
        self.loc = loc 
        self.cidx = cidx
        self.citation = citation
        self.outlier = outlier
        self.replaced = replaced 

    @staticmethod
    def get_by_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT *
        FROM Citation as c
        WHERE c.tcpID = :tcpID 
        ''',
        tcpID=tcpID)
        return [Citation(*row) for row in rows]
    
    @staticmethod
    def get_by_aut(aut):
        rows = app.db.execute('''
        SELECT c.tcpID,sidx,loc,cidx,citation,outlier,replaced
        FROM Citation as c, Author as a 
        WHERE c.tcpID = a.tcpID 
        AND a.author = :aut 
        ''',
        aut = aut)
        return [Citation(*row) for row in rows]
    
    @staticmethod
    def get_by_tcpID_sidx(tcpID,sidx):
        rows = app.db.execute('''
        SELECT *
        FROM Citation as c
        WHERE c.tcpID = :tcpID 
        AND c.sidx = :sidx
        ''',
        tcpID=tcpID,
        sidx=sidx)
        return [Citation(*row) for row in rows]
    
    @staticmethod
    def get_by_tcpID_sidx_loc(tcpID,sidx,loc):
        rows = app.db.execute('''
        SELECT *
        FROM Citation as c
        WHERE c.tcpID = :tcpID 
        AND c.sidx = :sidx
        AND c.loc = :loc
        ''',
        tcpID=tcpID,
        sidx=sidx,
        loc=loc)
        return [Citation(*row) for row in rows]
    
    @staticmethod
    def get_by_label(label):
        rows = app.db.execute('''
        SELECT *
        FROM Citation as c
        WHERE c.citation LIKE :label
        ''',
        label=label)
        return [Citation(*row) for row in rows]
    
    @staticmethod
    def get_all():
        rows = app.db.execute('''
        SELECT *
        FROM Citation as c
        ''')
        return [Citation(*row) for row in rows]

    @staticmethod
    def get_ver_by_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT ver
        FROM BibleVersion
        WHERE tcpID = :tcpID
        ''',tcpID=tcpID)
        if len(rows) == 0: 
            return 'Unknown'
        return rows[0][0] 
    
    @staticmethod
    def remove_citation(tcpID, sidx,loc,cidx):
        app.db.execute('''
        DELETE FROM Citation 
        WHERE tcpID = :tcpID
        AND sidx = :sidx
        AND loc = :loc 
        AND cidx = :cidx
        ''',
        tcpID=tcpID,
        sidx=sidx,
        loc=loc,
        cidx=cidx)
    
    @staticmethod
    def update_text(tcpID, sidx,loc,cidx,new):
        app.db.execute("""
        UPDATE Citation 
        SET citation = :new        
        WHERE tcpID = :tcpID 
        AND sidx = :sidx
        AND loc = :loc
        AND cidx = :cidx 
        """,
        tcpID = tcpID,
        sidx=sidx,
        cidx=cidx,
        loc=loc,
        new=new)
        
    @staticmethod
    def update_index(tcpID, sidx,loc,cidx):
        app.db.execute("""
        UPDATE Citation 
        SET cidx = :cidx                      
        WHERE tcpID = :tcpID 
        AND sidx = :sidx
        AND loc = :loc
        """,
        tcpID = tcpID,
        sidx=sidx,
        cidx=cidx,
        loc=loc)
    
    @staticmethod
    def update_ver(tcpID, ver):
        app.db.execute("""
        UPDATE BibleVersion 
        SET ver = :ver                      
        WHERE tcpID = :tcpID 
        """,
        tcpID = tcpID,
        ver=ver)

    @staticmethod
    def add_ver(tcpID, ver):
        app.db.execute("""
        INSERT INTO BibleVersion VALUES (:tcpID,:ver)
        """,
        tcpID = tcpID,
        ver=ver)
    @staticmethod
    def add_citation(tcpID, sidx,loc,cidx,citation,replaced):
        app.db.execute("""
        INSERT INTO Citation VALUES (:tcpID, :sidx, :loc, :cidx, :citation, '',:replaced)  
        """,
        tcpID = tcpID,
        sidx=sidx,
        cidx=cidx,
        loc=loc,
        citation=citation,
        replaced=replaced)

class QuoteParaphrase:
    def __init__(self,tcpID,sidx,loc,vidx,score,freq,label,phrase,full):
        self.tcpID = tcpID 
        self.sidx = sidx
        self.loc = loc 
        self.label = label
        self.vidx = vidx
        self.score = score
        self.freq = freq
        self.phrase = phrase
        self.full = full

    @staticmethod
    def add_qp(tcpID, sidx,loc,verse_id,phrase):
        app.db.execute("""
        INSERT INTO QuoteParaphrase VALUES (:tcpID, :sidx, :loc, :verse_id,:phrase)  
        """,
        tcpID = tcpID,
        sidx=sidx,
        verse_id=verse_id,
        loc=loc,
        phrase=phrase)

    @staticmethod
    def remove_actual_qp(tcpID, sidx,loc,verse_id):
        app.db.execute("""
        DELETE FROM QuoteParaphrase
        WHERE tcpID = :tcpID
        AND sidx = :sidx
        AND verse_id = :verse_id 
        """,
        tcpID = tcpID,
        sidx=sidx,
        verse_id=verse_id,
        loc=loc)

    @staticmethod
    def get_actual_verse_id(verse_id):
        rows = app.db.execute('''
        SELECT *
        FROM QuoteParaphrase as p
        WHERE p.verse_id = :verse_id
        ''',
        verse_id = verse_id)
        return rows 
        
    @staticmethod
    def get_actual_by_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, p.phrase,b.verse_text
        FROM QuoteParaphrase as p, Bible as b 
        WHERE p.tcpID = :tcpID
        AND b.verse_id = p.verse_id
        ''',
        tcpID = tcpID)
        return rows 
    
    @staticmethod
    def get_actual_by_aut(aut):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, b.verse_text,p.phrase
        FROM QuoteParaphrase as p, Bible as b,Author as a  
        WHERE b.verse_id = p.verse_id
        AND p.tcpID = a.tcpID 
        AND a.author = :aut 
        ''',
        aut = aut)
        return rows 
    
    @staticmethod
    def get_actual_by_tcpID_sidx(tcpID,sidx):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, b.verse_text,p.phrase
        FROM QuoteParaphrase as p, Bible as b 
        WHERE p.tcpID = :tcpID
        AND b.verse_id = p.verse_id
        AND p.sidx = :sidx
        ''',
        tcpID = tcpID,
        sidx=sidx)
        return rows 
    @staticmethod
    def get_all():
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.vidx, p.score, p.freq, b.verse_id,bp.phrase,Bible.verse_text
        FROM PossibleQuoteParaphrase as p, BiblePhraseLabel as b, BiblePhrase as bp, Bible
        WHERE p.vidx = b.vidx 
        AND Bible.verse_id = b.verse_id 
        AND b.vidx = bp.vidx
        ''')
        return [QuoteParaphrase(*row) for row in rows]
    
    @staticmethod
    def get_by_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.vidx, p.score, p.freq, b.verse_id,bp.phrase,Bible.verse_text
        FROM PossibleQuoteParaphrase as p, BiblePhraseLabel as b, BiblePhrase as bp, Bible
        WHERE p.tcpID = :tcpID 
        AND p.vidx = b.vidx 
        AND Bible.verse_id = b.verse_id 
        AND b.vidx = bp.vidx
        ''',
        tcpID=tcpID)
        return [QuoteParaphrase(*row) for row in rows]
    
    @staticmethod
    def get_by_vidx(vidx):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.vidx, p.score, p.freq, b.verse_id,bp.phrase,Bible.verse_text
        FROM PossibleQuoteParaphrase as p, BiblePhraseLabel as b, BiblePhrase as bp, Bible
        WHERE p.vidx = :vidx 
        AND p.vidx = b.vidx 
        AND Bible.verse_id = b.verse_id 
        AND b.vidx = bp.vidx
        ''',
        vidx=vidx)
        return [QuoteParaphrase(*row) for row in rows]
    
    @staticmethod
    def get_by_tcpID_sidx(tcpID,sidx):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.vidx, p.score, p.freq, b.verse_id,bp.phrase,Bible.verse_text
        FROM PossibleQuoteParaphrase as p, BiblePhraseLabel as b, BiblePhrase as bp, Bible
        WHERE p.tcpID = :tcpID 
        AND p.vidx = b.vidx 
        AND Bible.verse_id = b.verse_id 
        AND b.vidx = bp.vidx
        AND p.sidx = :sidx
        ''',
        tcpID=tcpID,
        sidx=sidx)
        return [QuoteParaphrase(*row) for row in rows]
    
    @staticmethod
    def remove_by_tcpID_sidx_vidx(tcpID,sidx,vidx):
        app.db.execute('''
        DELETE FROM PossibleQuoteParaphrase as p
        WHERE p.tcpID = :tcpID 
        AND p.vidx = :vidx
        AND p.sidx = :sidx
        ''',
        tcpID=tcpID,
        sidx=sidx,
        vidx=vidx)
    
    @staticmethod
    def get_bible_verse_ids():
        rows = app.db.execute('''
        SELECT DISTINCT b.verse_id
        FROM BiblePhraseLabel as b
        ''')
        return rows 
    
    @staticmethod
    def get_bible_verse(verse_id):
        rows = app.db.execute('''
        SELECT b.verse_id,bp.phrase,Bible.verse_text,b.vidx,Bible.lemmatized
        FROM BiblePhraseLabel as b, BiblePhrase as bp, Bible
        WHERE Bible.verse_id = b.verse_id 
        AND b.vidx = bp.vidx
        AND b.verse_id = :verse_id
        ''',
        verse_id=verse_id)
        verse_text = rows[0][2]
        lemmatized = rows[0][4]
        vindices = [row[3] for row in rows]
        phrases = [(row[1],idx) for idx,row in enumerate(rows)]
        return verse_text,lemmatized, phrases,vindices 
   
    @staticmethod
    def get_bible_verse_by_vidx(vidx):
        rows = app.db.execute('''
        SELECT b.verse_id,bp.phrase,Bible.verse_text
        FROM BiblePhraseLabel as b, BiblePhrase as bp, Bible
        WHERE Bible.verse_id = b.verse_id 
        AND b.vidx = bp.vidx
        AND b.vidx = :vidx
        ''',
        vidx=vidx)
        return rows 

    @staticmethod
    def search_bible_phrase(era,phrase,loc,k):
        results = app.vectordb.search(era,phrase,loc,k)
        return results
    
    @staticmethod
    def search_in_bible(phrase,k):
        results = app.vectordb.search_bible(phrase,k)
        return results
    
    @staticmethod
    def remove_bible_phrase(vidx):
        app.db.execute('''
        DELETE FROM PossibleQuoteParaphrase as p
        WHERE p.vidx = :vidx
        ''',
        vidx=vidx)
        app.db.execute('''
        DELETE FROM BiblePhraseLabel as p
        WHERE p.vidx = :vidx
        ''',
        vidx=vidx)
        app.db.execute('''
        DELETE FROM BiblePhrase as p
        WHERE p.vidx = :vidx
        ''',
        vidx=vidx)
        
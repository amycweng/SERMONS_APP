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
        SELECT b.verse_id,bp.phrase,Bible.verse_text
        FROM BiblePhraseLabel as b, BiblePhrase as bp, Bible
        WHERE Bible.verse_id = b.verse_id 
        AND b.vidx = bp.vidx
        AND b.verse_id = :verse_id
        ''',
        verse_id=verse_id)
        verse_text = rows[0][2]
        phrases = [row[1] for row in rows]
        return verse_text, phrases 
    
    @staticmethod
    def search_bible_phrase(era,phrase,loc,k):
        results = app.vectordb.search(era,phrase,loc,k)
        return results
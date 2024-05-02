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

from flask import current_app as app

class Text:
    def __init__(self,tcpID,sidx,section,loc,loc_type,pidx,tokens,lemmatized):
        self.tcpID = tcpID 
        self.sidx = sidx
        self.section = section
        self.loc = loc 
        self.loc_type = loc_type
        self.pidx = pidx
        self.tokens = tokens 
        self.lemmatized = lemmatized

    @staticmethod
    def get_by_tcpID_sidx(tcpID,sidx):
        rows = app.db.execute('''
        SELECT *
        FROM Segment as s 
        WHERE s.tcpID = :tcpID
        AND s.sidx = :sidx
        ''',
        tcpID=tcpID,
        sidx=sidx)
        return [Text(*row) for row in rows]

class Marginalia:
    def __init__(self,tcpID,sidx,nidx,tokens,lemmatized):
        self.tcpID = tcpID 
        self.sidx = sidx
        self.nidx = nidx
        self.tokens = tokens 
        self.lemmatized = lemmatized

    @staticmethod
    def get_by_tcpID_sidx(tcpID,sidx):
        rows = app.db.execute('''
        SELECT *
        FROM Marginalia as s 
        WHERE s.tcpID = :tcpID
        AND s.sidx = :sidx
        ''',
        tcpID=tcpID,
        sidx=sidx)
        return [Marginalia(*row) for row in rows]

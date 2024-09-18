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
    def get_all():
        rows = app.db.execute('''
        SELECT *
        FROM Citation as c
        ''')
        return [Citation(*row) for row in rows]
    
    @staticmethod
    def get_by_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT *
        FROM Citation as c
        WHERE c.tcpID = :tcpID 
        ORDER BY c.sidx ASC 
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
    def get_by_pubplace(pubplace):
        rows = app.db.execute('''
        SELECT c.tcpID,sidx,loc,cidx,citation,outlier,replaced
        FROM Citation as c, Pubplace as pp 
        WHERE c.tcpID = pp.tcpID 
        AND pp.pubplace LIKE :pubplace 
        ''',
        pubplace = pubplace)
        return [Citation(*row) for row in rows]
    
    @staticmethod
    def get_by_pubyear(pubyear):
        rows = app.db.execute('''
        SELECT c.tcpID,sidx,loc,cidx,citation,outlier,replaced
        FROM Citation as c, Sermon as s 
        WHERE c.tcpID = s.tcpID 
        AND s.pubyear LIKE :pubyear 
        ''',
        pubyear = pubyear)
        return [Citation(*row) for row in rows]
    @staticmethod
    def get_by_subject(subject):
        rows = app.db.execute('''
        SELECT c.tcpID,sidx,loc,cidx,citation,outlier,replaced
        FROM Citation as c, SubjectHeading as s 
        WHERE c.tcpID = s.tcpID 
        AND s.subject_heading = :subject 
        ''',
        subject = subject)
        return [Citation(*row) for row in rows]
    @staticmethod
    def get_by_tcpID_sidx(tcpID,sidx):
        rows = app.db.execute('''
        SELECT *
        FROM Citation as c
        WHERE c.tcpID = :tcpID 
        AND c.sidx = :sidx
        ORDER BY c.sidx 
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
    def update_phrase(tcpID, sidx,loc,cidx,phrase):
        app.db.execute("""
        UPDATE Citation 
        SET replaced = :phrase                      
        WHERE tcpID = :tcpID 
        AND sidx = :sidx
        AND loc = :loc
        AND cidx = :cidx 
        """,
        tcpID = tcpID,
        sidx=sidx,
        cidx=cidx,
        loc=loc,
        phrase=phrase)
    
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

class Bible: 
    def __init__(self,verse_id,bible_version,part,book,chapter,verse,verse_text):
        self.verse_id = verse_id 
        self.bible_version = bible_version
        self.part = part 
        self.book = book
        self.chapter = chapter 
        self.verse = verse
        self.verse_text = verse_text
    
    @staticmethod
    def get_bible_verse_ids():
        rows = app.db.execute('''
        SELECT *
        FROM Bible
        ''')
        return [Bible(*row) for row in rows]
    @staticmethod
    def get_bible_verse_ids_only():
        rows = app.db.execute('''
        SELECT verse_id
        FROM Bible
        ORDER BY verse_id
        ''')
        return [r[0] for r in rows]
    @staticmethod
    def get_bible_verse_by_ids(verse_ids):
        rows = app.db.execute('''
        SELECT * 
        FROM Bible
        WHERE Bible.verse_id IN :verse_ids
        ''',
        verse_ids=verse_ids)
        return [Bible(*row) for row in rows]   
    
    @staticmethod
    def get_bible_verse_by_id(verse_id):
        rows = app.db.execute('''
        SELECT * 
        FROM Bible
        WHERE Bible.verse_id  = :verse_id
        ''',
        verse_id=verse_id)
        return [Bible(*row) for row in rows]  
    
    @staticmethod
    def get_bible_verse_by_part(verse_id,part):
        rows = app.db.execute('''
        SELECT * 
        FROM Bible
        WHERE Bible.verse_id = :verse_id
        AND Bible.part = :part
        ''',
        verse_id=verse_id,
        part=part)
        return [Bible(*row) for row in rows]

    @staticmethod
    def search_bible_phrase(phrase,loc,k):
        results = app.vectordb.search(phrase,loc,k)
        return results
    
    @staticmethod
    def search_in_bible(phrase,k):
        results = app.vectordb.search_bible(phrase,k)
        return results
    

class QuoteParaphrase:
    def __init__(self,tcpID,sidx,loc,verse_id,score,phrase,verse_text,scope):
        self.tcpID = tcpID 
        self.sidx = sidx
        self.loc = loc 
        self.verse_id = verse_id
        self.score = score
        self.phrase = phrase
        self.verse_text = verse_text
        self.scope = scope 

    
    @staticmethod
    def get_by_label(label):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, p.score,p.phrase,b.verse_text,p.scope
        FROM QuoteParaphrase as p, Bible as b
        WHERE b.verse_id LIKE :label
        AND b.verse_id = p.verse_id
        ORDER BY p.score DESC
        ''',
        label=label)
        return [QuoteParaphrase(*row) for row in rows]
    
    @staticmethod
    def add_qp(tcpID, sidx,loc,verse_id,score,phrase,scope):
        check = app.db.execute('''
        SELECT EXISTS (
            SELECT * 
            FROM QuoteParaphrase as p, Bible as b 
            WHERE p.tcpID = :tcpID
            AND b.verse_id = p.verse_id
            AND p.verse_id = :verse_id,
            AND p.sidx = :sidx,
            AND p.loc = :loc
        )
        ''',
        tcpID = tcpID,
        sidx=sidx,
        verse_id=verse_id,
        loc=loc
        )
        if not check: 
            app.db.execute("""
            INSERT INTO QuoteParaphrase VALUES (:tcpID, :sidx, :loc, :verse_id,:score,:scope,:phrase)  
            """,
            tcpID = tcpID,
            sidx=sidx,
            verse_id=verse_id,
            loc=loc,
            score=score,
            phrase=phrase)
        else: 
            score = f"<br>--<br>{score}"
            phrase = f"<br>--<br>{phrase}"
            scope = f"<br>--<br>{phrase}"
            app.db.execute("""
            INSERT INTO QuoteParaphrase VALUES (:tcpID, :sidx, :loc, :verse_id,:score,:scope,:phrase)
            UPDATE QuoteParaphrase
            SET score = CONCAT(score, :score),
                phrase = CONCAT(phrase,:phrase)
            WHERE p.tcpID = :tcpID
            AND b.verse_id = p.verse_id
            AND p.verse_id = :verse_id,
            AND p.sidx = :sidx,
            AND p.loc = :loc 
            """,
            tcpID = tcpID,
            sidx=sidx,
            verse_id=verse_id,
            loc=loc,
            scope=scope,
            score=score,
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
        SELECT p.verse_id
        FROM QuoteParaphrase as p
        WHERE p.verse_id = :verse_id
        ''',
        verse_id = verse_id)
        return [QuoteParaphrase(*row) for row in rows] 
        
    @staticmethod
    def get_actual_by_tcpID(tcpID):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, p.score,p.phrase,b.verse_text,p.scope
        FROM QuoteParaphrase as p, Bible as b 
        WHERE p.tcpID = :tcpID
        AND b.verse_id = p.verse_id
        ORDER BY p.tcpID ASC, p.sidx ASC 
        ''',
        tcpID = tcpID)
        return [QuoteParaphrase(*row) for row in rows]  
    
    @staticmethod
    def get_actual_by_aut(aut):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, p.score,p.phrase,b.verse_text,p.scope
        FROM QuoteParaphrase as p, Bible as b, Author as a  
        WHERE b.verse_id = p.verse_id
        AND p.tcpID = a.tcpID 
        AND a.author = :aut 
        ORDER BY p.tcpID ASC, p.sidx ASC 
        ''',
        aut = aut)
        return [QuoteParaphrase(*row) for row in rows]  
    
    @staticmethod
    def get_actual_by_pubplace(pubplace):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, p.score,p.phrase,b.verse_text,p.scope
        FROM QuoteParaphrase as p, Bible as b, Pubplace as pp 
        WHERE b.verse_id = p.verse_id
        AND p.tcpID = pp.tcpID 
        AND pp.pubplace LIKE :pubplace 
        ORDER BY p.tcpID ASC, p.sidx ASC 
        ''',
        pubplace = pubplace)
        return [QuoteParaphrase(*row) for row in rows]  
    
    @staticmethod
    def get_actual_by_pubyear(pubyear):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, p.score,p.phrase,b.verse_text,p.scope
        FROM QuoteParaphrase as p, Bible as b, Sermon as s 
        WHERE b.verse_id = p.verse_id
        AND p.tcpID = s.tcpID 
        AND s.pubyear LIKE :pubyear 
        ORDER BY p.tcpID ASC, p.sidx ASC 
        ''',
        pubyear = pubyear)
        return [QuoteParaphrase(*row) for row in rows]  
    
    @staticmethod
    def get_actual_by_subject(subject):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, p.score,p.phrase,b.verse_text,p.scope
        FROM QuoteParaphrase as p, Bible as b, SubjectHeading as s 
        WHERE b.verse_id = p.verse_id
        AND p.tcpID = s.tcpID 
        AND s.subject_heading = :subject 
        ORDER BY p.tcpID ASC, p.sidx ASC 
        ''',
        subject = subject)
        return [QuoteParaphrase(*row) for row in rows]  
    
    @staticmethod
    def get_actual_by_tcpID_sidx(tcpID,sidx):
        rows = app.db.execute('''
        SELECT p.tcpID, p.sidx, p.loc, p.verse_id, p.score,p.phrase,b.verse_text,p.scope
        FROM QuoteParaphrase as p, Bible as b 
        WHERE p.tcpID = :tcpID
        AND b.verse_id = p.verse_id
        AND p.sidx = :sidx
        ORDER BY p.sidx
        ''',
        tcpID = tcpID,
        sidx=sidx)
        return [QuoteParaphrase(*row) for row in rows]  
    
    @staticmethod
    def get_text_hits_by_ids(tcpID, sidx):
        rows = app.db.execute('''
        SELECT s.tokens 
        FROM Segment as s 
        WHERE tcpID = :tcpID
        AND sidx = :sidx 
        ''',
        tcpID = tcpID, sidx = sidx)
        return rows[0]
    
    @staticmethod
    def get_marginal_hits_by_ids(tcpID, sidx, nidx):
        rows = app.db.execute('''
        SELECT s.tokens 
        FROM Marginalia as s 
        WHERE tcpID = :tcpID
        AND sidx = :sidx 
        AND nidx = :nidx 
        ''',
        tcpID = tcpID, sidx = sidx, nidx =nidx)
        return rows[0]
    # @staticmethod
    # def get_text_hits_by_ids(keys):
    #     rows = app.db.execute('''
    #     WITH CIndices (cid,tcpID,sidx) AS (
    #         SELECT collection_name || '_' || idx, tcpID, sidx
    #         FROM ChromaIndices
    #         WHERE loc = -1 
    #     )
    #     SELECT CI.cid, s.tcpID, s.sidx, s.tokens 
    #     FROM CIndices as CI, Segment as s         
    #     WHERE CI.cid IN :keys  
    #     AND CI.tcpID = s.tcpID 
    #     AND CI.sidx = s.sidx 
    #     ''',
    #     keys=keys)
    #     hits = {}
    #     for r in rows: 
    #         if r[0] not in hits: hits[r[0]] = []
    #         hits[r[0]].append({"tcpID": r[1], "sidx":r[2], "loc": -1,"text": r[3]})
    #     return hits
    
    # @staticmethod
    # def get_marginal_hits_by_ids(keys):
    #     rows = app.db.execute('''
    #     WITH CIndices (cid,tcpID,sidx,loc) AS (
    #         SELECT collection_name || '_' || idx, tcpID, sidx
    #         FROM ChromaIndices
    #         WHERE loc <> -1  
    #     )
    #     SELECT s.tcpID, s.sidx, s.loc, s.tokens 
    #     FROM CIndices as CI, Marginalia as s 
    #     WHERE CI.cid IN :keys 
    #     AND CI.tcpID = s.tcpID 
    #     AND CI.sidx = s.sidx 
    #     AND CI.loc = s.nidx  
    #     ''',
    #     keys=keys)
    #     hits = {}
    #     for r in rows: 
    #         if r[0] not in hits: hits[r[0]] = []
    #         hits[r[0]].append({"tcpID": r[1], "sidx":r[2], "loc": r[3],"text": r[4]})
    #     return hits
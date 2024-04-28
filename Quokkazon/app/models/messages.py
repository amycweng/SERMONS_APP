from flask import current_app as app

class Messages:
    def __init__(self,sender,sname,receiver,rname,date_time,msg):
        self.sender = sender
        self.sname = sname 
        self.recipient = receiver,
        self.rname = rname
        self.date_time = date_time
        self.msg = msg 
    
    @staticmethod 
    def has_message(uid):
        # get the uid and names of the users who have either messaged the current user 
        # or received a message from the current user 
        rows = app.db.execute('''
        WITH receivers AS ( 
            SELECT m.receiver AS id,MAX(m.date_time) AS date_time
            FROM Messages as m 
            WHERE m.sender = :uid
            GROUP BY m.receiver
        ), senders AS (
            SELECT m.sender AS id,MAX(m.date_time) AS date_time
            FROM Messages as m
            WHERE m.receiver = :uid
            GROUP BY m.sender
        )
        SELECT DISTINCT u.id, (u.firstname || ' ' || u.lastname),MAX(m.date_time)
        FROM (SELECT * FROM receivers UNION SELECT * FROM senders) AS m, Users as u
        WHERE u.id = m.id
        GROUP BY u.id, (u.firstname || ' ' || u.lastname)
        ''',
        uid=uid)
        # rows[0] is the id of the user with whom the current user has interacted with 
        # rows[1] is the name of the user with id equal to rows[0]
        # rows[2] is the timestamp of the most recent interaction with that user 
        return rows
    
    @staticmethod 
    def get_by_uid(uid):
        rows = app.db.execute('''
        WITH my_messages AS (
            SELECT m.sender, m.receiver, m.date_time, m.msg
            FROM Messages as m 
            WHERE m.sender = :uid
            OR m.receiver = :uid
        )
        SELECT s.id, (s.firstname || ' ' || s.lastname), m.receiver, (r.firstname || ' ' || r.lastname), m.date_time, m.msg 
        FROM Users as s, Users as r, my_messages as m  
        WHERE s.id = m.sender
        AND r.id = m.receiver 
        ORDER BY m.date_time   
        ''',
        uid=uid)
        return [Messages(*row) for row in rows]
    
    @staticmethod 
    def message_thread(myid,otherid):
        rows = app.db.execute('''
        WITH my_messages AS (
            SELECT m.sender, m.receiver, m.date_time, m.msg
            FROM Messages as m 
            WHERE (m.sender = :myid AND m.receiver = :otherid)
            OR (m.receiver = :myid AND m.sender = :otherid)
        )
        SELECT s.id, (s.firstname || ' ' || s.lastname), m.receiver, (r.firstname || ' ' || r.lastname), m.date_time, m.msg 
        FROM Users as s, Users as r, my_messages as m  
        WHERE s.id = m.sender
        AND r.id = m.receiver 
        ORDER BY m.date_time   
        ''',
        myid=myid,
        otherid=otherid
        )
        return [Messages(*row) for row in rows]
    
    @staticmethod 
    def new_message(myid,otherid,date_time,msg):
        app.db.execute('''
        INSERT INTO Messages VALUES (:myid, :otherid, :date_time, :msg)  
        ''',
        myid=myid,
        otherid=otherid,
        date_time=date_time,
        msg=msg
        )
    

    
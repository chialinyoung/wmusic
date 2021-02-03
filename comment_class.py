import sqlite3
import database_class

DB_NAME = "music_store.db"
TABLE_NAME = "comments"
KEY_INDEX = "commentID"

class UserComment(database_class.Database):
    def __init__(self, commentID, instrument, username, time, contents):
        self.commentIID = commentID
        self.username = username
        self.instrument = instrument
        self.time = time
        self.contents = contents
        super().__init__(DB_NAME, TABLE_NAME, KEY_INDEX)
    def __str__(self):
        return f"Comment about {self.instrument}, by {self.username}, at {self.time}"
    def __repr__(self):
        return f"CommentID {self.commentID}: {self.contents}"

    @classmethod
    def from_commentID(cls, id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        query = f"SELECT * FROM {TABLE_NAME} WHERE {KEY_INDEX}=?"
        c.execute(query, (id,))
        comment_entry = c.fetchone()
        c.close()
        if comment_entry is not None:
            return cls(id, comment_entry[1], comment_entry[2], comment_entry[3], comment_entry[4])
        else:
            return None
    
    @classmethod
    def new_comment(cls, instrument, username, time, contents):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        query = f"INSERT INTO {TABLE_NAME} (instrument, username, datetime, contents) VALUES ({instrument}, \"{username}\", {time}, \"{contents}\")"
        c.execute(query)
        if c.rowcount == 1:
            new_ID = c.lastrowid
            conn.commit()
            conn.close()
            return cls(new_ID, instrument, username, time, contents)
        else:
            conn.close()
            return None    
    
    @staticmethod
    def allcomments_by_instrument(instrument):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        query = f"SELECT * FROM {TABLE_NAME} WHERE instrument={instrument}"
        c.execute(query)
        all_ids=[row[0] for row in c]
        conn.close()
        return all_ids
    

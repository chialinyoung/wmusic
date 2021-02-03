import sqlite3

class Database:
    def __init__ (self, db, table, key, fields=None):
        self.db = db
        self.table = table 
        self.key = key
        #self.fields = fields
    def __str__(self):
        return f"Datbase {self.DB} table {self.table}, with key index {self.key}"
    
    def delete_from_db(self, query, rows=1):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(query)
        if c.rowcount >= rows:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
            
    def update_to_db (self, query, rows=1):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(query)
        if c.rowcount >= rows:
            conn.commit()
            c.close()
            return True
        else:
            c.close()
            return False
        
    def add_to_db (self, query, check):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(query)
        if check == c.lastrowid:
            conn.commit()
            c.close()
            return True
        else:
            c.close()
            return False




import sqlite3

import database_class
#import instrument_model

## to handle incorrect reference number
MAX_REF=100000
MIN_REF=10000 
class MyException(Exception):
    def __init__ (self, msg=None):
        msg = f'My Error message {msg}'
        super().__init__(msg)

DB_NAME = "music_store.db"
TABLE_NAME = "instruments"
KEY_INDEX = "ref_num"

class Instrument(database_class.Database):
    def __init__(self, ref, category, name, url):
        self.ref = ref
        self.category = category
        self.name = name
        self.url = url
        super().__init__(DB_NAME, TABLE_NAME, KEY_INDEX)
    def __str__(self):
        return f"This is a {self.name} and is a {self.category} instrument"
    def __repr__(self):
        return f"Instrument({self.ref}, {self.name}, {self.category})"
    def dict_wrapper(self):
        return {"ref_num":self.ref,"category":self.category,"name":self.name,"url":self.url}

    @classmethod
    def from_reference(cls, ref):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        #instrument_model.show_one(c, (ref,))
        query = f"SELECT * FROM {TABLE_NAME} WHERE ref_num=?"
        c.execute(query, (ref,))
        record = c.fetchone()
        if record is not None:
            _, name, cat, url = record
            conn.close()
            return cls(ref, cat, name, url)
        else:
            conn.close()
            return None
        
    @staticmethod
    def find_all_ref():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        ##instrument_model.show_all(c)
        query = f"SELECT * FROM {TABLE_NAME};"
        c.execute(query)
        ##all_ref = [row[0] for row in c]
        all_ref=[]
        for row in c:
            try:
                if row[0] < MIN_REF:
                    raise MyException(f'find_all_ref error: {row[1]} with REF_NUM {row[0]}')
            except MyException as e:
                print(e.msg)
            else:
                all_ref.append(row[0])
        conn.close()
        return all_ref

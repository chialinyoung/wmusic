import sqlite3
import database_class

DB_NAME = "music_store.db"
TABLE_NAME = "users"
KEY_INDEX = "username"
    
class WebUser(database_class.Database):
    def __init__(self, username, role, cart, password=None):
        self.username = username
        self.role = role
        self.cart = cart
        self.password = password
        super().__init__(DB_NAME, TABLE_NAME, KEY_INDEX)
    def __str__(self):
        return f"ID: {self.username}, role: {self.role}"
    def __repr__(self):
        return f"ID: {self.username}, role: {self.role}, cart: {self.cart}"

    @classmethod
    def from_username(cls, username):
        conn = sqlite3.connect(DB_NAME)
        cu = conn.cursor()
        query = f"SELECT * FROM {TABLE_NAME} WHERE {KEY_INDEX}=?"
        cu.execute(query, (username,))
        user_entry = cu.fetchone()
        cu.close()
        if user_entry is not None:
            return cls(username, user_entry[2], user_entry[3], user_entry[1])
        else:
            return None

    ##@staticmethod
    

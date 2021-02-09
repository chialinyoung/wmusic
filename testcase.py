import unittest
import sqlite3
import random
import string
from datetime import datetime
import database_class as dclass
import instrument_class as iclass
import user_class as uclass
import comment_class as cclass

testDB = 'test.db'
class InstrumentTest (unittest.TestCase):
## instruemnt class test
    def test_findallref (self):
        conn = sqlite3.connect(testDB)
        c = conn.cursor()
        c.execute ("SELECT * FROM instruments;")
        all_ref = [row[0] for row in c]
        self.assertEqual (all_ref, iclass.Instrument.find_all_ref(), f'FindAllRef1 error: {all_ref}')
        conn.close()
        pass

    def test_fromreference (self):
        test_ref = None
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = 0
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = random.randrange(0,iclass.MIN_REF-1) # smaller than required
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = random.randrange(iclass.MAX_REF, iclass.MAX_REF * 100) # larger than required
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = random.randrange( -1*iclass.MAX_REF, 0)  # negative
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = random.uniform (0.0, 1.0) #pos float
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = random.uniform (-1.0, 0.0) #neg float
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = "".join([random.choice(string.digits) for i in range(200)]) # extrem case
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = "".join([random.choice(string.ascii_letters) for i in range(5)]) # string
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')
        test_ref = "".join([random.choice(string.ascii_letters) for i in range(200)]) # extrem case
        self.assertIsNone(iclass.Instrument.from_reference(test_ref), f'test_Ref:{test_ref}')

        conn = sqlite3.connect(testDB)
        c = conn.cursor()
        c.execute("SELECT * FROM instruments ORDER BY RANDOM() LIMIT 1;")
        entry = c.fetchone()
        conn.close()
        test_entry = iclass.Instrument.from_reference(entry[0])
        self.assertIsInstance(test_entry, iclass.Instrument, f'Entry[0]:{entry[0]}')
        # why?
        #self.assertEqual(test_entry, iclass.Instrument.from_reference(entry[0]), f'test_Ref: {entry[0]}')
        self.assertEqual(entry[0], test_entry.ref, f'Entry[0]: {entry[0]}')
        self.assertEqual(entry[1], test_entry.name, f'Entry[1]: {entry[1]}')
        self.assertEqual(entry[2], test_entry.category, f'Entry[2] {entry[2]}')
        self.assertEqual(entry[3], test_entry.url, f'Entry[3] {entry[3]}')
        
        pass


class UserTest (unittest.TestCase):
    def test_fromusername(self):
        test_name = None
        self.assertIsNone(uclass.WebUser.from_username(test_name), f'test_name: {test_name}')
        test_name = "".join([random.choice(string.ascii_letters) for i in range(20)])
        self.assertIsNone(uclass.WebUser.from_username(test_name), f'test_name: {test_name}')
        test_name = "".join([random.choice(string.ascii_letters) for i in range(200)])
        self.assertIsNone(uclass.WebUser.from_username(test_name), f'test_name: {test_name}')
        test_name = "".join([random.choice(string.ascii_letters) for i in range(10000)])
        self.assertIsNone(uclass.WebUser.from_username(test_name), f'test_name: {test_name}')
        
        conn = sqlite3.connect(testDB)
        c = conn.cursor()
        c.execute("SELECT * FROM users ORDER BY RANDOM() LIMIT 1;")
        entry = c.fetchone()
        conn.close()
        test_entry = uclass.WebUser.from_username(entry[0])
        self.assertIsInstance(test_entry, uclass.WebUser, f'test_name:{entry[0]}')
        self.assertEqual(entry[0], test_entry.username, f'Entry[0]: {entry[0]}')
        self.assertEqual(entry[1], test_entry.password, f'Entry[1]: {entry[1]}')
        self.assertEqual(entry[2], test_entry.role, f'Entry[2] {entry[2]}')
        self.assertEqual(entry[3], test_entry.cart, f'Entry[3] {entry[3]}')
        
        pass
        
class CommentTest (unittest.TestCase):
    cclass.DB_NAME = testDB
    def test_fromcommentid(self):
        test_id = None
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        test_id = 0
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        test_id = random.uniform (0.0, 1.0) #pos float
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        test_id = random.uniform (-1.0, 0.0) #neg float
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        test_id = "".join([random.choice(string.digits) for i in range(200)]) # extrem case
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        test_id = "".join([random.choice(string.ascii_letters) for i in range(5)]) # string
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        test_id = "".join([random.choice(string.ascii_letters) for i in range(200)]) # extrem case
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        
        conn = sqlite3.connect(testDB)
        c = conn.cursor()
        c.execute("SELECT * FROM comments ORDER BY commentID DESC LIMIT 1;")
        entry = c.fetchone()
        last_row = entry[0]
        c.execute("SELECT * FROM comments ORDER BY RANDOM() LIMIT 1;")
        entry = c.fetchone()
        conn.close()
        
        test_id = random.randrange(last_row, last_row*10)
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        test_id = random.randrange(last_row, last_row*1000)
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        test_id = random.randrange(-1*last_row, 0)  # negative
        self.assertIsNone(cclass.UserComment.from_commentID(test_id), f'test_ID:{test_id}')
        
        test_entry= cclass.UserComment.from_commentID(entry[0])
        self.assertIsInstance(test_entry, cclass.UserComment, f'test_ID:{entry[0]}')
        self.assertEqual(entry[0], test_entry.commentID, f'Entry[0]: {entry[0]}')
        self.assertEqual(entry[1], test_entry.instrument, f'Entry[1]: {entry[1]}')
        self.assertEqual(entry[2], test_entry.username, f'Entry[2] {entry[2]}')
        self.assertEqual(entry[3], test_entry.time, f'Entry[3] {entry[3]}')
        self.assertEqual(entry[4], test_entry.contents, f'Entry[3] {entry[4]}')
        
        pass

    def test_newcomment(self):
        conn = sqlite3.connect(testDB)
        c = conn.cursor()
        c.execute("SELECT * FROM instruments ORDER BY RANDOM() LIMIT 1;")
        test_inst = c.fetchone()[0]
        c.execute("SELECT * FROM users ORDER BY RANDOM() LIMIT 1;")
        test_user = c.fetchone()[0]
        test_time = int(datetime.timestamp(datetime.now()))
        test_text = "".join([random.choice(string.ascii_letters) for i in range(10000)])  
        test_entry = cclass.UserComment.new_comment(test_inst, test_user, test_time, test_text)
        if test_entry == None:
            print ("ERROR1")
            return
        c.execute("SELECT * FROM comments ORDER BY commentID DESC LIMIT 1;")
        entry = c.fetchone()
        conn.close()
        self.assertIsInstance(test_entry, cclass.UserComment, f'Entry[0]:{entry[0]}')
        self.assertEqual(entry[0], test_entry.commentID, f'Entry[0]: {entry[0]}')
        self.assertEqual(entry[1], test_entry.instrument, f'Entry[1]: {entry[1]}')
        self.assertEqual(entry[2], test_entry.username, f'Entry[2] {entry[2]}')
        self.assertEqual(entry[3], test_entry.time, f'Entry[3] {entry[3]}')
        self.assertEqual(entry[4], test_entry.contents, f'Entry[3] {entry[4]}')
        
        #need to change comment check flag
        cclass.comment_check = True
        tmp_instrument = random.randrange(iclass.MAX_REF*10, iclass.MAX_REF*100)
        tmp_user = "".join([random.choice(string.ascii_letters) for i in range(1000)]) 
        tmp_time = "".join([random.choice(string.ascii_letters) for i in range(1000)]) 
        test_entry = cclass.UserComment.new_comment(tmp_instrument, test_user, test_time, test_text)
        self.assertIsNone(test_entry, f'test_instrument:{tmp_instrument}')
        test_entry = cclass.UserComment.new_comment(test_inst, tmp_user, test_time, test_text)
        self.assertIsNone(test_entry, f'test_user:{tmp_user}')
        test_entry = cclass.UserComment.new_comment(test_inst, test_user, tmp_time, test_text)
        self.assertIsNone(test_entry, f'test_time:{tmp_time}')
        test_entry = cclass.UserComment.new_comment(tmp_instrument, tmp_user, tmp_time, test_text)
        self.assertIsNone(test_entry, f'test_instrument{tmp_instrument}, test_user{tmp_user}, test_time:{tmp_time}')
        
        pass

    def test_allcommentsbyinstrument(self):
        instrument = random.randrange(iclass.MAX_REF*10, iclass.MAX_REF*100)
        all_comments = cclass.UserComment.allcomments_by_instrument(instrument)
        self.assertEqual([], all_comments, f'test_instrument{instrument}')
        
        conn = sqlite3.connect(testDB)
        c = conn.cursor()
        c.execute("SELECT * FROM instruments ORDER BY RANDOM() LIMIT 1;")
        test_inst = c.fetchone()[0]
        c.execute ("SELECT * FROM comments WHERE instrument=?", (test_inst,))
        test_comments=[row[0] for row in c]
        conn.close()
        all_comments = cclass.UserComment.allcomments_by_instrument(test_inst)
        self.assertEqual(all_comments, test_comments, f'commentID comp: {all_comments} - {test_comments}')
        
        pass
            
        
if __name__ == '__main__':
    unittest.main()
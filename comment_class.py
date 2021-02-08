import sqlite3
import database_class
import re

DB_NAME = "music_store.db"
TABLE_NAME = "comments"
KEY_INDEX = "commentID"

comment_check = True

class UserComment(database_class.Database):
    def __init__(self, commentID, instrument, username, time, contents):
        self.commentID = commentID
        self.username = username
        self.instrument = instrument
        self.time = time
        self.contents = contents
        super().__init__(DB_NAME, TABLE_NAME, KEY_INDEX)
    def __str__(self):
        return f"Comment about {self.instrument}, by {self.username}, at {self.time}"
    def __repr__(self):
        return f"CommentID {self.commentID}: {self.contents}"

    def rating_analysis(self):
        # sentence_pattern = re.compile(r'(.*?\.)(\s|$)', re.DOTALL)
        # matches = sentence_pattern.findall(self.contents) 
        # sentences = [match[0] for match in matches]
        # word_pattern = re.compile(r"([\w\-']+)([\s,.])?")  
        # words = []
        # for sentence in sentences:
        #     matches = word_pattern.findall(sentence)
        #     for match in matches:
        #         words.append(match)
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        from nltk.sentiment import SentimentIntensityAnalyzer
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(self.contents)
        #filtered_tokens = [w for w in tokens if w not in stop_words]
        filtered_tokens =''
        for w in tokens:
            if w not in stop_words:
                filtered_tokens+=f' {w}'
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(filtered_tokens)
        return scores['compound']

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
        if comment_check:
            import instrument_class as iclass
            all_ref = iclass.Instrument.find_all_ref()
            if int(instrument) not in all_ref:
                return None
            
            import user_class as uclass
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            if uclass.WebUser.from_username(username) is None:
                return None
            
            if re.match('\d{10}', str(time)) == None:
                return None
        ## end of comment check
        
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
    

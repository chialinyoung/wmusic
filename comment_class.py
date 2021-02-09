import sqlite3
import database_class
import re

comment_check = False
USE_NLTK = True

DB_NAME = "music_store.db"
TABLE_NAME = "comments"
KEY_INDEX = "commentID"


if USE_NLTK:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.sentiment import SentimentIntensityAnalyzer

def absolute_sentiment(p, n, t):
    if t==0:
        return 0
    else:
        return (p-n)/t

def test_sentiment(p, n, t):
    return round(absolute_sentiment(p, n, t),4)

def content_check (text):
    if text:
        filtered_text = re.sub('<[^<]+?>', '', text)
        if filtered_text[-1] not in ['.','?','!']:
            filtered_text += '.' 
        return filtered_text
    else:   
        return text

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

    def rating_analysis(self, good_set, bad_set, stop_set):
        ### sentence_pattern = re.compile(r'(.*?\.)(\s|$)', re.DOTALL)
        ### matches = sentence_pattern.findall(self.contents) 
        ### sentences = [match[0] for match in matches]
        word_pattern = re.compile(r"([\w\-']+)([\s,.])?")  
        matches = word_pattern.findall(self.contents)
        filtered_words = [match[0] for match in matches if match[0] not in stop_set]
        num_total = len(filtered_words)
        good_words = good_set.intersection(filtered_words)
        bad_words = bad_set.intersection(filtered_words)
        num_good = len(good_words)
        num_bad = len(bad_words)
        return test_sentiment(num_good, num_bad, num_total)
        
    def nltk_analysis(self):        
        stop_words = set(stopwords.words('english'))
        token_words = set(word_tokenize(self.contents))
        filtered_words = token_words - stop_words
        filtered_string = " ".join(filtered_words)
        scores = SentimentIntensityAnalyzer().polarity_scores(filtered_string)
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
        
        filtered_contents = content_check(contents)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        query = f"INSERT INTO {TABLE_NAME} (instrument, username, datetime, contents) VALUES ({instrument}, \"{username}\", {time}, \"{filtered_contents}\")"
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
    
    @staticmethod
    def nltk_package_check():
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt') 
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords') 
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
            ## vader_lexicon needs zip??
        except LookupError:
            nltk.download('vader_lexicon') 

import requests
import json
import random

#find Songsterr data
def fine_songsterr ():
    artists = ['BTS', 'Michael Jackson', 'Lady Gaga', 'ABBA', 'Aerosmith']
    songURL = 'https://www.songsterr.com/a/ra/songs/byartists.json'
    artist = artists[random.randint(0,len(artists))-1]
    r = requests.get(songURL, params={'artists':'"'+artist+'"'})
    if r.status_code == 200:
        j=r.json()
        songNo = random.randint(0,len(j)-1)
        songsterrURL = "http://www.songsterr.com/a/wa/song?id="+str(j[songNo]['id'])
        return {'song':j[songNo]['title'], 'artist':artist, 'songURL':songsterrURL}
    else:
        return None

# return a simple HTML POST form
def simple_post_form (type_name_value):
    input_fields = '<p><input '.join([f'type={item[0]} name={item[1]} value={item[2]}>'for item in type_name_value])
    return f'''<form method="post"> 
        <p><input {input_fields}
    </form>
    ''' 
    
# check role in session
def role_check (session):
    if session is None:
        return 0
    elif 'role' not in session:
        return 0
    else:
        return session['role']

    


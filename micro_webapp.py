#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import json
import random
from datetime import datetime
import instrument_class as iclass
import user_class as uclass
import comment_class as cclass
# [MODELS]
#import instrument_model
import instrument_helpers

# [APP START]
app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'this_IS_$up3r_SECUR3~'

# [MAIN][Admin Route]
@app.route('/instruments/show/all')
def show_all():
    ##jan18
    if  instrument_helpers.role_check(session) != 'admin':
        res = "for admin only, please login"
        return render_template('messages.html', message=res)
    
    res = []
    refList = iclass.Instrument.find_all_ref()
    for ref in refList:
        instrument = iclass.Instrument.from_reference(ref)
        res.append(instrument.dict_wrapper())
    return render_template('index.html', instruments=res)

@app.route('/instruments/show/<ref_number>')
def show_detail_page(ref_number):
    instrument = iclass.Instrument.from_reference(ref_number)
    res = instrument.dict_wrapper()
    if instrument.category == 'string':
        songSterr = instrument_helpers.fine_songsterr()
        if songSterr is not None:
            res["songs"]=songSterr['song']
            res["artist"]=songSterr['artist']
            res["songURL"]=songSterr['songURL']
    all_comments = cclass.UserComment.allcomments_by_instrument(ref_number)
    user_comments=[]
    for cID in all_comments:
        entry = cclass.UserComment.from_commentID(cID)
        user_comments.append({'username':entry.username, 'datetime':datetime.fromtimestamp(entry.time), 'contents':entry.contents})
    return render_template('detailed.html', instrument=res, comments=user_comments)

@app.route('/instruments/create', methods=["GET", "POST"])
def create_instrument():
    if request.method == "POST":    
        
        ref_num = random.randint(iclass.MIN_REF,iclass.MAX_REF-1)
        while iclass.Instrument.from_reference(ref_num) is not None:
            ref_num = random.randint(iclass.MIN_REF,iclass.MAX_REF-1)
        instrument = iclass.Instrument(ref_num, request.form['cat'],  request.form['name'], request.form['url'])
        query = f"INSERT INTO {instrument.table} VALUES ({ref_num},\"{request.form['name']}\",\"{request.form['cat']}\",\"{request.form['url']}\")"
        if instrument.add_to_db(query, ref_num):
            res = "added!"
        else:
            res = 'oops, something happened please ask the administrator'
            # DRY
        return render_template('messages.html', message=res) 
    else:
        # this is GET
        return render_template("create_instrument.html")
@app.route('/instruments/update/<ref_number>', methods=['GET', 'POST'])
def update_one_instrument(ref_number):
    if request.method == 'POST':
        instrument = iclass.Instrument.from_reference(ref_number)
        query = f"UPDATE {instrument.table} SET name=\"{request.form['name']}\", category=\"{request.form['cat']}\", image=\"{request.form['url']}\" WHERE {instrument.key}={ref_number}"
        if instrument.update_to_db(query):
            res = 'update success'
        else:
            res = 'update failed'
        return render_template("update.html", res=res)
    else:
        # for GET methods
        instrument = iclass.Instrument.from_reference(ref_number)
        ins = instrument.dict_wrapper()
        return render_template('update.html', instrument=ins)
@app.route('/instruments/delete/<ref_number>', methods=["GET", "DELETE", "POST"])
def delete_instrument(ref_number):
    if request.method == "POST" or  request.method == "DELETE":
        ins = iclass.Instrument.from_reference(ref_number)
        if ins.delete_from_db(f"DELETE FROM {ins.table} WHERE {ins.key}={ref_number}"):
            res = "Deleted successfully"
        else:
            res = "Oops, something happened please ask the administrator"
        if request.method == "DELETE":
            return res
        return render_template('delete.html', res=res)
    else:
        instrument = iclass.Instrument.from_reference(ref_number)
        ins = instrument.dict_wrapper()
        return render_template('delete.html', instrument=ins)
        # return redirect(url_for('/instruments/show/all'))
@app.route('/') #root URL
def welcome():
    storedName = request.cookies.get('user_id')
    res = []
    refList = iclass.Instrument.find_all_ref()
    for ref in refList:
        instrument = iclass.Instrument.from_reference(ref)
        res.append(instrument.dict_wrapper())
    return render_template("welcome.html", instruments=res)
@app.route('/cart/add/<ref_number>')
def add_to_cart(ref_number):
    if instrument_helpers.role_check(session) == 'buyer':
        web_user = uclass.WebUser.from_username(session['username'])
        if session['cart'] is None:
            session['cart'] = f'{ref_number}'
        else:
            session['cart'] += f' {ref_number}'
        query = f"UPDATE {web_user.table} SET cart=\"{session['cart']}\" WHERE {web_user.key}=\"{web_user.username}\""
        if web_user.update_to_db(query):
            res = "added to cart!"
        else:
            res = "faile to add to cart!"
    else:
        res = "please login as buyer" 
    return render_template('messages.html', message=res) 
# --- SOLUTION ---
@app.route('/cart/show/all')
def show_cart():
    if  instrument_helpers.role_check(session) == 'buyer':
        all_ref = iclass.Instrument.find_all_ref()
        cart = []
        if session['cart'] is not None:
            cart = [int(x) for x in session['cart'].split()]
        ref_number_count = {}
        for instrument_number in cart:
            if ref_number_count.get(instrument_number) is None:
                ref_number_count[instrument_number] = 0
            ref_number_count[instrument_number] += 1
        
        res = []
        for ins_ref in all_ref:
            if ins_ref in ref_number_count:
                instrument = iclass.Instrument.from_reference(ins_ref)
                resA = instrument.dict_wrapper()
                resA["count"]=ref_number_count[ins_ref]
                res.append(resA)
        return render_template('cart.html', cart=res)
    else:
        res = "please login as buyer" 
        return render_template('messages.html', message=res) 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        web_user = uclass.WebUser.from_username(request.form['username'])
        if web_user is not None:
            if web_user.password == request.form['password']:
                session['username'] = web_user.username
                session['role'] = web_user.role
                session['cart'] = web_user.cart
                resp = redirect(url_for('welcome'))
                resp.set_cookie('user_id', session['username'])
                session.permanent = True
                return resp
        res = "invalid username/password"
        return render_template('messages.html', message=res)
    else: #GET
        user_id = request.cookies.get('user_id') or ''
        html_type = ['text', 'password', 'submit']
        html_names = ['username', 'password', '']
        html_values = [user_id, '', 'Login']
        return instrument_helpers.simple_post_form(zip(html_type, html_names, html_values))
    
@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('cart')
    session.pop('role')
    resp = redirect(url_for('welcome'))
    return resp

@app.route('/greeting')
def greeting():
    print('[DEBUG][greeting]::', session)
    return 'Good morning!'

@app.route('/instruments/comment/<ref_number>', methods=['GET', 'POST'])
def comment_page(ref_number):
    if request.method == 'POST':
        contents = request.form['comments']
        if not contents:
            res = "Empty comment is not saved"
        else:
            new_comment = cclass.UserComment.new_comment(ref_number, session['username'], int(datetime.timestamp(datetime.now())), contents)
            if new_comment is not None:
                res = "Thank you for your comment!"
            else:
                res = "Comment not saved, oops..."
        return render_template('messages.html', message=res)
    else: #GET
        if instrument_helpers.role_check(session) != 'buyer':
            res = "for registered buyer only, please login"
            return render_template('messages.html', message=res)
        else:
            html_type = ['text', 'submit']
            html_names = ['comments', '']
            html_values = ['', 'submit']
            return instrument_helpers.simple_post_form(zip(html_type, html_names, html_values))
    
@app.route('/instruments/analysis/<ref_number>')
def comment_analysis(ref_number):
    instrument = iclass.Instrument.from_reference(ref_number)
    all_comments = cclass.UserComment.allcomments_by_instrument(ref_number)
    instr = {'name':instrument.name, 'rating': 'no rating yet'}
    user_comments=[]
    if len(all_comments)>0:
        if cclass.USE_NLTK == False:
            good_set = set(line.strip() for line in open('good_words.txt'))
            bad_set = set(line.strip() for line in open('bad_words.txt'))
            stop_set = set(line.strip() for line in open('stop_words.txt'))
        else:
            cclass.UserComment.nltk_package_check()
        ttl_rating = []
        for count, cID  in enumerate(all_comments, start=1):
            entry = cclass.UserComment.from_commentID(cID)
            if cclass.USE_NLTK == True:
                rating = entry.nltk_analysis()
            else:
                rating = entry.rating_analysis(good_set, bad_set, stop_set)
            user_comments.append({'number':count, 'username':entry.username, 'datetime':datetime.fromtimestamp(entry.time), 'contents':entry.contents, 'rating':rating})  
            ttl_rating.append(rating)
        instr['rating'] = round(sum(ttl_rating)/len(ttl_rating),4)
        
    return render_template('comment_analysis.html', instrument=instr, comments=user_comments)

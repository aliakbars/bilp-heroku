#!/usr/bin/python
import os
from flask import Flask, flash, current_app, render_template, request, redirect, session
from functools import wraps
from collections import Counter
from database import db
from models import Sentence, User, Dictionary, ScoreLog
from sqlalchemy.sql import func

import hashlib
import random
import requests
import json
import re
from nltk.tokenize import TweetTokenizer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.debug = True
app.secret_key = 'jbblhivghyrvcl_ec2-107-20-178-83'
db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def filter_words(words):
    with open('kbbi.txt') as f:
        lemmas = f.read().splitlines()
        lemmas = set(lemmas)
        return filter(lambda x: x not in lemmas, set(words))

@app.route('/', methods=['GET', 'POST'])
@login_required
def hello():
    errors = []
    sentence = Sentence.query.order_by(func.random()).first()
    words = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", sentence.text.lower()).split()
    words = filter_words(words)
    random.shuffle(words)
    words = words[:4]

    # TODO Memunculkan kata yang sebelumnya jika tidak berhasil

    if request.method == 'POST':
        if not request.form.getlist('word_alay') or not request.form.getlist('word_normal') or not request.form['sentence_id']:
            errors.append('Isilah semua kolom yang tersedia!')
        else:
            words_alay = request.form.getlist('word_alay')
            words_normal = request.form.getlist('word_normal')
            for i, word_alay in enumerate(words_alay):
                word_normal = words_normal[i]
                d = Dictionary(word_alay, word_normal, request.form['sentence_id'], request.headers.get('User-Agent'))
                db.session.add(d)
                db.session.commit()
            flash('Data berhasil tersimpan.')
            return redirect('/')

    return render_template('index.html', errors=errors, sentence=sentence, words=words)

@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')

@app.route('/words', methods=['GET'])
def words():
    dicts = Dictionary.query.all()
    c = Counter(((d.word_alay, d.word_normal) for d in dicts))
    d = sorted(c.items())
    return render_template('words.html', dicts=d)

# comparator
@app.route('/sentence', methods=['GET', 'POST'])
@login_required
def sentence():
    errors = []

    if request.method == 'POST':
        if not request.form['sentence']:
            errors.append('Isilah semua kolom yang tersedia!')
        else:
            d = Sentence(request.form['sentence'], request.form['source'])
            db.session.add(d)
            db.session.commit()
            flash('Data berhasil tersimpan.')
            return redirect('/sentence')
    return render_template('sentence.html', errors=errors)

@app.route('/check', methods=['GET'])
def check():
    check_id = request.args.get("id")
    if check_id is not None:
        check_sentence = Sentence.query.get(check_id)
        if check_sentence is not None:
            # TODO Ganti dengan pengecekan menggunakan hasil scraping KBBI
            Word.query.filter_by(sentence_id=check_id).delete()
            tweet_tokenizer = TweetTokenizer()
            tokens = tweet_tokenizer.tokenize(check_sentence.text)
            for token in tokens:
                url = "http://kateglo.com/api.php?format=json&phrase="+token
                resp = requests.get(url)
                exist = False
                if (resp.ok):
                    try:
                        resp_json = json.loads(resp.content)
                        exist = True
                    except ValueError:
                        exist = False
                word = Word(check_sentence.id, token, exist)
                db.session.add(word)
            db.session.commit()
    sentences = Sentence.query.all()
    c = ((sentence.id, 
        sentence.source, 
        sentence.text, 
        ((w.word, w.exist,) for w in sentence.words.all()), 
        ) for sentence in sentences)
    return render_template('check.html', rows=c)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            error = 'Please enter username and password.'
        else:
            user = User.query.filter_by(username=request.form['username']).first()
            if not user:
                d = User(request.form['username'], request.form['password'])
                db.session.add(d)
                db.session.commit()
                session['user_id'] = d.id
                session['authenticated'] = True
                return redirect('/')
            else:
                error = 'Username already exists!'
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            error = 'Please enter username and password.'
        else:
            user = User.query.filter_by(username=request.form['username']).first()
            if user:
                if user.password == hashlib.sha512(request.form['password'] + user.salt).hexdigest():
                    session['user_id'] = user.id
                    session['authenticated'] = True
                    return redirect('/')
            error = 'Invalid credentials. Please try again.'
    return render_template('signin.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    if session.get('authenticated'):
        del session['user_id']
        del session['authenticated']
    return redirect('/login')

@app.route('/scores', methods=['GET'])
def show_scores():
    raise NotImplementedError("")

def add_score():
    # TODO Tambahkan score ke log dan update di tabel User
    raise NotImplementedError("")

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
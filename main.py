#!/usr/bin/python
import os
from flask import Flask, flash, current_app, render_template, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku
from collections import Counter
from datetime import datetime

import requests
import json
from nltk.tokenize import TweetTokenizer

app = Flask(__name__)
heroku = Heroku(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///bilpdev"
db = SQLAlchemy(app)
app.debug = False
app.secret_key = 'jbblhivghyrvcl_ec2-107-20-178-83'


class Word(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sentence_id = db.Column(db.Integer, db.ForeignKey('sentence.id'))
	word = db.Column(db.String(40))
	exist = db.Column(db.Boolean)
	created_at = db.Column(db.DateTime)

	def __init__(self, sentence_id, word, exist):
		self.sentence_id = sentence_id
		self.word = word
		self.exist = exist
		self.created_at = datetime.today()

	def __repr__(self):
		return '<Word %d - %s [%s]>' % (self.sentence_id, self.word, self.exist)

class Sentence(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(255))
	source = db.Column(db.String(40))
	words = db.relationship('Word', backref='sentence', lazy='dynamic')
	created_at = db.Column(db.DateTime)

	def __init__(self, text, source):
		self.text = text
		self.source = source
		self.created_at = datetime.today()

	def __repr__(self):
		return '<Sentence %s - %s>' % (self.source, self.text)

class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_alay = db.Column(db.String(255))
    word_normal = db.Column(db.String(255))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)

    def __init__(self, word_alay, word_normal, user_agent):
        self.word_alay = word_alay
        self.word_normal = word_normal
        self.user_agent = user_agent
        self.created_at = datetime.today()

    def __repr__(self):
        return '<Content %s - %s>' % (self.word_alay, self.word_normal)

@app.route('/', methods=['GET', 'POST'])
def hello():
	errors = []

	if request.method == 'POST':
		if not request.form['word_alay'] or not request.form['word_normal']:
			errors.append('Isilah semua kolom yang tersedia!')
		else:
			d = Dictionary(request.form['word_alay'], request.form['word_normal'], request.headers.get('User-Agent'))
			db.session.add(d)
			db.session.commit()
			flash('Data berhasil tersimpan.')
			return redirect('/')
	return render_template('index.html', errors=errors)

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

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
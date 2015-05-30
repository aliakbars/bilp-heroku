#!/usr/bin/python
import os
from flask import Flask, flash, current_app, render_template, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku
from collections import Counter
from datetime import datetime

app = Flask(__name__)
heroku = Heroku(app)
db = SQLAlchemy(app)
app.debug = False
app.secret_key = 'jbblhivghyrvcl_ec2-107-20-178-83'

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

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
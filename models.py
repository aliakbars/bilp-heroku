from database import db
from datetime import datetime
import hashlib
import uuid

# class Word(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   sentence_id = db.Column(db.Integer, db.ForeignKey('sentence.id'))
#   word = db.Column(db.String(40))
#   exist = db.Column(db.Boolean)
#   created_at = db.Column(db.DateTime)

#   def __init__(self, sentence_id, word, exist):
#       self.sentence_id = sentence_id
#       self.word = word
#       self.exist = exist
#       self.created_at = datetime.today()

#   def __repr__(self):
#       return '<Word %d - %s [%s]>' % (self.sentence_id, self.word, self.exist)

class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))
    source = db.Column(db.String(40))
    # words = db.relationship('Word', backref='sentence', lazy='dynamic')
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
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentence.id'))
    user_agent = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime)

    def __init__(self, word_alay, word_normal, sentence_id, user_agent):
        self.word_alay = word_alay
        self.word_normal = word_normal
        self.sentence_id = sentence_id
        self.user_agent = user_agent
        self.created_at = datetime.today()

    def __repr__(self):
        return '<Content %s - %s>' % (self.kata_id, self.word_normal)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(255)) # hash
    salt = db.Column(db.String(255))
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    def __init__(self, username, password):
        self.username = username
        self.salt = uuid.uuid4().hex
        self.password = hashlib.sha512(password + self.salt).hexdigest()
        self.score = 0
        self.created_at = datetime.today()

class ScoreLog(db.Model):
    # TODO Add backref relationship
    id = db.Column(db.Integer, primary_key=True)
    dictionary_id = db.Column(db.Integer, db.ForeignKey('dictionary.id'))
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    def __init__(self, dictionary_id, target_user_id, score):
        self.target_user_id = target_user_id
        self.score = score
        self.created_at = datetime.today()
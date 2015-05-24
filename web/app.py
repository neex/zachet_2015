from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import string, random

import one_way_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    recovery_question = db.Column(db.String(80))
    recovery_answer = db.Column(db.String(80))
    big_fat_csrf_token = db.Column(db.String(50))
    

    def __init__(self, username, password, recovery_question, recovery_answer):
        self.username = username
        self.password = password
        self.recovery_question = recovery_question
        self.recovery_answer = recovery_answer
        self.big_fat_csrf_token = ''.join([random.choice(string.ascii_letters) for i in xrange(48)])

    def __repr__(self):
        return '<User {}>'.format(self.__dict__)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cookie_session_id = db.Column(db.String(50), unique=True)

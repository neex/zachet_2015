from flask.ext.sqlalchemy import SQLAlchemy
import string, random, datetime
import one_way_crypt

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index = True)
    password = db.Column(db.String(80))
    recovery_question = db.Column(db.String(80))
    recovery_answer = db.Column(db.String(80))
    secret = db.Column(db.String(16))    
    big_fat_csrf_token = db.Column(db.String(50))    
    rsa_n = db.Column(db.String(1000))
    rsa_e = db.Column(db.String(1000))
    midcrypt_key = db.Column(db.LargeBinary)

    def __init__(self, username, password, recovery_question, recovery_answer, secret):
        self.username = username
        self.password = password
        self.recovery_question = recovery_question
        self.recovery_answer = recovery_answer
        self.secret = secret
        self.big_fat_csrf_token = "csrf_{}".format(''.join([random.choice(string.ascii_letters) for i in xrange(40)]))
        cr = one_way_crypt.Cryptor()
        self.rsa_n = str(cr.n)
        self.rsa_e = str(cr.e)
        self.midcrypt_key = cr.mk 
        

    def __repr__(self):
        return '<User {}>'.format(self.__dict__)

    def new_e(self):
        cr = self.get_cryptor()
        cr.gen_new_e()
        self.rsa_e = str(cr.e)

    def new_n(self):
        cr = self.get_cryptor()
        cr.gen_new_n()
        self.rsa_n = str(cr.n)

    def midcrypt_key_hex(self):
        return " ".join("{:02x}".format(ord(c)) for c in self.midcrypt_key)
    def get_cryptor(self):
        return one_way_crypt.Cryptor(int(self.rsa_n), int(self.rsa_e), self.midcrypt_key)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cookie_session_id = db.Column(db.String(50), unique=True, index = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pseudo_session = db.Column(db.Boolean)

    def __init__(self, username, pseudo_session = False):
        self.user_id = User.query.filter_by(username = username).first().id
        self.pseudo_session = pseudo_session
        self.cookie_session_id = "sess_{}".format(''.join([random.choice(string.ascii_letters) for i in xrange(40)]))        

    def __repr__(self):
        return '<Session {}>'.format(self.__dict__)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_id =  db.Column(db.Integer, db.ForeignKey('user.id'), index = True)
    to_id =  db.Column(db.Integer, db.ForeignKey('user.id'), index = True)
    text = db.Column(db.LargeBinary)
    crypted = db.Column(db.Boolean)
    date_created = db.Column(db.DateTime)
    
    def __init__(self, from_name, to_name, crypted, text):
        user_from  = User.query.filter_by(username = from_name).first()
        user_to = User.query.filter_by(username = to_name).first()
        self.from_id = user_from.id
        self.to_id = user_to.id
        self.crypted = crypted
        self.datetime = datetime.datetime.now()        
        if not self.crypted:
            self.text = text
        else:
            cr = user_from.get_cryptor()
            text = text.rjust(16)[:16]
            self.text = cr.do_encrypt(text)
            
    def __repr__(self):
        return '<Message {}>'.format(self.__dict__)        

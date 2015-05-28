from flask import Flask, request, render_template, make_response, redirect, url_for
import logging
import json

from models import *
from login_management import *
from forms import *
from functools import wraps

logger = logging.getLogger('zachet_webapp')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('zachet.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

app = Flask(__name__)
app.debug = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://prak:2014prakvmk2014@localhost/prak4?charset=utf8&use_unicode=0'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db.init_app(app)

def log_exceptions(f):
    @wraps(f)
    def wr(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            logger.exception("Exception")
            raise

    return wr

@app.route('/')
@log_exceptions
def index():
    user = get_user_if_not_pseudo()
    return render_template("index.html", user = user)

if app.debug:
    @app.route('/recreate_db')
    def recreate_db():
        db.drop_all()
        db.create_all()
        db.session.commit()
        return "no"


@app.route('/register', methods=['GET', 'POST'])
@log_exceptions
def register():
    user = get_user_if_not_pseudo()
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.password.data, form.recovery_question.data, form.recovery_answer.data, form.secret.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login') + '?blue_message=Thank+you+for+registration.+You+can+login+now')
    return render_template('register.html', form = form, user = user)


@app.route('/login', methods=['GET', 'POST'])
@log_exceptions
def login():
    user = get_user_if_not_pseudo()
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        sess = Session(form.user.username)
        db.session.add(sess)
        db.session.commit()
        resp = make_response(redirect(url_for('profile') + '?blue_message=Now+you+logged+in'))
        resp.set_cookie('sess_id', sess.cookie_session_id)
        return resp
    return render_template('login.html', user = user, form = form)


@app.route('/profile')
@log_exceptions
@req_login
def profile(user):
    return render_template('profile.html', user = user)

@app.route('/gen_new_e')
@log_exceptions
@req_login
@check_csrf_token(True)
def gen_new_e(user):
    user.new_e()
    db.session.commit()
    return redirect(url_for('profile') + '?blue_message=RSA+E+changed')


@app.route('/gen_new_n')
@log_exceptions
@req_login
@check_csrf_token(True)
def gen_new_n(user):
    user.new_n()
    db.session.commit()
    return redirect(url_for('profile') + '?blue_message=RSA+N+changed')

@app.route('/send')
@log_exceptions
@req_login
@check_csrf_token(False)
def send_message(user):
    form = SendForm(request.args)
    form.user_to.choices = [(u.username, ) * 2 for u in User.query.order_by(User.id).all()]

    if request.args.get('submit') and form.validate():
        mess = Message(user.username, form.user_to.data, form.encrypt.data, form.text.data)
        db.session.add(mess)
        db.session.commit()
        return redirect(url_for('send_message') + '?blue_message=Message+sent')
    return render_template('send_message.html', user = user, form = form)

@app.route('/send_secret')
@log_exceptions
@req_login
@check_csrf_token(False)
def send_secret_message(user):
    form = SendSecretForm(request.args)
    form.user_to.choices = [(u.username, ) * 2 for u in User.query.order_by(User.id).all()]
    if request.args.get('submit') and form.validate():
        mess = Message(user.username, form.user_to.data, True, user.secret, "Crypted supersecret")
        db.session.add(mess)
        db.session.commit()
        return redirect(url_for('send_secret_message') + '?blue_message=Message+sent')
    return render_template('send_secret_message.html', user = user, form = form)


@app.route('/inbox')
@log_exceptions
@req_login
def inbox(user):
    messages = Message.query.filter_by(to_id = user.id).order_by(Message.date_created.desc()).all()
    return render_template('inbox.html', user = user, messages = messages)

@app.route('/inbox_json')
@log_exceptions
@req_login
def inbox_json(user):
    last_id = int(request.args['last_id'])
    messages = Message.query.filter_by(to_id = user.id).filter(Message.id > last_id).all()
    messages_json = []
    for m in messages:
        d = {}
        for x in m.__dict__:
            if x and x[0] != '_':
                if type(getattr(m, x)) in [int, str, unicode, long, bool]:
                    d[x] = getattr(m, x)
        messages_json.append(d)
    return json.dumps(messages_json)


@app.route('/password_recovery', methods = ['GET', 'POST'])
@log_exceptions
def password_recovery():
    user = get_user_if_not_pseudo()
    form = PasswordRecoveryForm(request.form)
    if request.method == 'POST' and form.validate():
        sess = Session(form.username.data, True)
        db.session.add(sess)
        db.session.commit()
        resp = make_response(redirect(url_for('password_recovery_question')))
        resp.set_cookie('sess_id', sess.cookie_session_id)
        return resp
    return render_template('password_recovery.html', user = user, form = form)


@app.route('/password_recovery_question', methods = ['GET', 'POST'])
@log_exceptions
@req_pseudo_login
@check_csrf_token(False)
def password_recovery_question(user):
    form = PasswordRecoveryAnswerForm(request.form)
    if request.method == 'POST' and form.validate():
        if user.recovery_answer != form.recovery_answer.data:
            form.recovery_answer.errors.append("Answer is incorrect")
        else:
            sess = get_session()
            sess.pseudo_session = False
            logger.debug('User %s correctly answered question, pseudosession -> session', user.username)
            db.session.commit()
            resp = make_response(redirect(url_for('profile') + '?blue_message=Answer+is+correct'))
            return resp
    return render_template('password_recovery_question.html', user = user, noreport_login = True, form = form)

if __name__ == "__main__":
    app.run()

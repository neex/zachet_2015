from flask import request, redirect, url_for
from models import *
from functools import wraps

def get_session():
    sess = None
    sess_id = request.cookies.get("sess_id")    
    if sess_id:
        sess = Session.query.filter_by(cookie_session_id = sess_id).first()
    return sess

    
def get_login():
    user = None
    is_pseudo_session = True
    sess = get_session()
    if sess:
        user = User.query.filter_by(id = sess.user_id).first()
        if user:
            is_pseudo_session = sess.pseudo_session
    return (user, is_pseudo_session)


def req_login(f):
    @wraps(f)
    def fs(*args, **kwargs):
        user, is_pseudo_session = get_login()
        if not user or is_pseudo_session:
            return redirect(url_for('login') + '?red_message=Login+required')
        return f(user, *args, **kwargs)
    return fs

    
def req_pseudo_login(f):
    @wraps(f)
    def fs(*args, **kwargs):
        user, is_pseudo_session = get_login()
        if not user or not is_pseudo_session:
            return redirect(url_for('login') + '?red_message=Login+required')
        return f(user, *args, **kwargs)
    return fs

def get_user_if_not_pseudo():
    user, is_pseudo_session = get_login()
    if not is_pseudo_session:
        return user
    return None


def check_csrf_token(force):
    def gener(f):
        @wraps(f)
        def ff(user, *args, **kwargs):
            if force or request.method == 'POST' or request.args.get('submit'):
                if user.big_fat_csrf_token not in [request.args.get('big_fat_csrf_token'), request.form.get('big_fat_csrf_token')]:
                    return redirect(url_for('index') + '?red_message=Bad+csrf+token')
            return f(user, *args, **kwargs)
        return ff
    return gener

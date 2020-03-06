import sqlite3
from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/form/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message):
    return render_template("apology.html", message=message)

def check_if_available(username):
    cur = get_cursor()
    cur.execute("SELECT username FROM users WHERE username = :username;", {"username":username})
    unavailable = cur.fetchall()
    if unavailable != []:
        return False

def get_db():
    db = sqlite3.connect("countdown.db")
    cur = db.cursor()
    return db


def get_cursor():
    db = sqlite3.connect("countdown.db")
    cur = db.cursor()
    return cur
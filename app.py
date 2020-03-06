from flask import Flask, escape, request, session
import sqlite3
from sqlite3 import Error
from flask.templating import render_template
from werkzeug.utils import redirect
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps


app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

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

def create_database(db_file):
    # create a database connection to a SQLite database
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        db = conn.cursor()
        db.execute("CREATE TABLE IF NOT EXISTS events (person_id INTEGER NOT NULL, event_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, title TEXT NOT NULL, message TEXT, date TEXT NOT NULL, location TEXT, theme TEXT NOT NULL, FOREIGN KEY(person_id) REFERENCES users(id));")
        db.execute("CREATE TABLE IF NOT EXISTS themes (theme_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT NOT NULL, link TEXT NOT NULL);")
        db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);")
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

create_database("countdown.db")

def get_db():
    db = sqlite3.connect("countdown.db")
    cur = db.cursor()
    return db


def get_cursor():
    db = sqlite3.connect("countdown.db")
    cur = db.cursor()
    return cur

@app.route("/form/register", methods=["GET"])
def render_register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    user_name = request.form.get("username")
    # check if username is available
    if check_if_available(user_name) == False:
        return apology(message = "Username is already taken")

    password = request.form.get("password")

    confirmation = request.form.get("confirmation")
    # check if passwords match
    if confirmation != password:
            return apology(message = "Passwords don't match")

    # if everything was ok, insert new user in DB
    db = get_db()
    db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash);", {
               "username": user_name, "hash": generate_password_hash(password)})
    db.commit()
    return redirect("/")


@app.route("/form/add-event", methods=["GET"])
@login_required
def render_add_event():
    cur = get_cursor()
    cur.execute("SELECT theme_id, name FROM themes;")
    themes_DB = cur.fetchall()
    return render_template("add_event.html", themes=themes_DB)


@app.route("/add-event", methods=["POST"])
@login_required
def add_event():
    # add new event that you want to count
    person_id = session["user_id"]
    title = request.form.get("title")
    message = request.form.get("message")
    event_date = request.form.get("date")
    location = request.form.get("location")
    theme = request.form.get("theme")
    print(theme)
    db = get_db()
    db.execute("INSERT INTO events (person_id, title, message, date, location, theme) VALUES (:person_id, :title, :message, :date, :location, :theme);", {
               "person_id": person_id, "title": title.upper(), "message": message, "date": event_date, "location": location.upper(), "theme": theme})

    db.commit()
    return redirect("/")


@app.route("/", methods=["GET"])
@login_required
def home_page():
    person_id = session["user_id"]
    db = get_db()
    cur = get_cursor()
    today = date.today()
    cur.execute("SELECT title, message, date, location, link FROM events JOIN themes ON events.theme = themes.theme_id WHERE events.date > :today AND events.person_id = :person_id ORDER BY date", {"today": today, "person_id":person_id})

    rows = cur.fetchall()
    return render_template("home_page.html", rows=rows)

@app.route("/layout")
def layout_page():
    return render_template("layout.html")

@app.route("/history")
@login_required
def history_page():
    person_id = session["user_id"]
    cur = get_cursor()
    today = date.today()
    # today = "1993-11-30"
    cur.execute("SELECT title, message, date, location, link FROM events JOIN themes ON events.theme = themes.theme_id WHERE events.date < :today ORDER BY date", {"today": today, "person_id":person_id})
    rows = cur.fetchall()
    return render_template("history.html", rows=rows)


@app.route("/form/login", methods=["GET"])
def render_log_in():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    # Forget any user_id
    session.clear()

    cur = get_cursor()
    username = request.form.get("username")
    password = request.form.get("password")
    cur.execute("SELECT * FROM users WHERE username = :username", {"username": username})
    rows =cur.fetchall()
    if len(rows) != 1 or not check_password_hash(rows[0][2], password):
        return apology(message = "invalid username and/or password")

    # Remember which user has logged in
    session["user_id"] = rows[0][0]

    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# HELPER FUNCTIONS
def apology(message):
    return render_template("apology.html", message=message)

def check_if_available(username):
    cur = get_cursor()
    cur.execute("SELECT username FROM users WHERE username = :username;", {"username":username})
    unavailable = cur.fetchall()
    if unavailable != []:
        return False


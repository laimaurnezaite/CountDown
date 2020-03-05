from flask import Flask, escape, request
import sqlite3
from sqlite3 import Error
from flask.templating import render_template
from werkzeug.utils import redirect
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)


def create_database(db_file):
    # create a database connection to a SQLite database
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        db = conn.cursor()
        db.execute("CREATE TABLE IF NOT EXISTS events (person_id INTEGER NOT NULL, event_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, title TEXT NOT NULL, message TEXT, date TEXT NOT NULL, location TEXT, theme TEXT NOT NULL);")
        db.execute("CREATE TABLE IF NOT EXISTS themes (theme_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT NOT NULL, link TEXT NOT NULL);")
        db.execute("CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL);")
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
    if checkifavailable(user_name) == False:
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
def render_add_event():
    cur = get_cursor()
    cur.execute("SELECT theme_id, name FROM themes;")
    themes_DB = cur.fetchall()
    return render_template("add_event.html", themes=themes_DB)


@app.route("/add-event", methods=["POST"])
def add_event():
    # add new event that you want to count
    person_id = request.form.get("id")
    title = request.form.get("title")
    message = request.form.get("message")
    event_date = request.form.get("date")
    location = request.form.get("location")
    theme = request.form.get("theme")
    db = get_db()
    db.execute("INSERT INTO events (person_id, title, message, date, location, theme) VALUES (:person_id, :title, :message, :date, :location, :theme);", {
               "person_id": person_id, "title": title.upper(), "message": message, "date": event_date, "location": location.upper(), "theme": theme})
    db.commit()
    return redirect("/")


@app.route("/", methods=["GET"])
def home_page():
    db = get_db()
    cur = get_cursor()
    today = date.today()
    # today = "2030-11-30"
    cur.execute("SELECT title, message, date, location, link FROM events JOIN themes ON events.theme = themes.theme_id WHERE events.date > :today ORDER BY date", {"today": today})
    rows = cur.fetchall()
    return render_template("home_page.html", rows=rows)

@app.route("/layout")
def layout_page():
    return render_template("layout.html")

@app.route("/history")
def history_page():
    cur = get_cursor()
    today = date.today()
    # today = "1993-11-30"
    cur.execute("SELECT title, message, date, location, link FROM events JOIN themes ON events.theme = themes.theme_id WHERE events.date < :today ORDER BY date", {"today": today})
    # cur.execute("SELECT * FROM users WHERE username = :username", {"username": "laima"})
    rows = cur.fetchall()
    # print(rows)
    # print("LEN of rows:", len(rows))
    return render_template("history.html", rows=rows)


@app.route("/form/login", methods=["GET"])
def render_log_in():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    cur = get_cursor()
    username = request.form.get("username")
    password = request.form.get("password")
    cur.execute("SELECT * FROM users WHERE username = :username", {"username": username})
    rows =cur.fetchall()
    if len(rows) != 1 or not check_password_hash(rows[0][2], password):
        return apology(message = "invalid username and/or password")
    return redirect("/")


# HELPER FUNCTIONS
def apology(message):
    return render_template("apology.html", message=message)

def checkifavailable(username):
    cur = get_cursor()
    cur.execute("SELECT username FROM users WHERE username = :username;", {"username":username})
    unavailable = cur.fetchall()
    if unavailable != []:
        return False
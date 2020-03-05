from flask import Flask, escape, request
import sqlite3
from sqlite3 import Error
from flask.templating import render_template
from werkzeug.utils import redirect
from datetime import date


app = Flask(__name__)


def create_database(db_file):
    # create a database connection to a SQLite database
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        db = conn.cursor()
        db.execute("CREATE TABLE IF NOT EXISTS events (person_id INTEGER NOT NULL, event_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, title TEXT NOT NULL, message TEXT, date TEXT NOT NULL, location TEXT, theme TEXT NOT NULL);")
        db.execute("CREATE TABLE IF NOT EXISTS themes (theme_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT NOT NULL, link TEXT NOT NULL);")
        # print(sqlite3.version)
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

# to print results from database
# cur.execute("SELECT * FROM events;")
# rows = cur.fetchall()

# for row in rows:
#     print(row)


@app.route("/form/add-event", methods=["GET"])
def render_add_event():
    return render_template("add_event.html")


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
               "person_id": person_id, "title": title, "message": message, "date": event_date, "location": location, "theme": theme})
    db.commit()
    return redirect("/")

# @app.route("/", methods=["GET"])
# def render_home_page():
#     return render_template("home_page.html")


@app.route("/", methods=["GET"])
def home_page():
    db = get_db()
    cur = get_cursor()
    today = date.today()
    cur.execute("SELECT * FROM events where date > :today;", {"today": today})
    rows = cur.fetchall()
    return render_template("home_page.html", rows=rows)

@app.route("/layout")
def layout_page():
    return render_template("layout.html")

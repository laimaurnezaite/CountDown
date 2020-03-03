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
        db.execute("CREATE TABLE IF NOT EXISTS events2 (id INTEGER NOT NULL, title TEXT NOT NULL, message TEXT, year TEXT NOT NULL, month TEXT NOT NULL, day TEXT NOT NULL, location TEXT, theme TEXT NOT NULL); ")
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
    id = request.form.get("id")
    title = request.form.get("title")
    message = request.form.get("message")
    year = request.form.get("year")
    month = request.form.get("month")
    day = request.form.get("day")
    location = request.form.get("location")
    theme = request.form.get("theme")
    db = get_db()
    db.execute("INSERT INTO events2 (id, title, message, year, month, day, location, theme) VALUES (:id, :title, :message, :year, :month, :day, :location, :theme);", {"id":id, "title":title, "message":message, "year":year, "month":month, "day":day, "location":location, "theme":theme})
    db.commit()
    return redirect("/")

# @app.route("/", methods=["GET"])
# def render_home_page():
#     render_template("homepage.html")

@app.route("/")
def home_page():
    db = get_db()
    today = date.today()
    # db.execute("INSERT INTO events (id, title, message, date, location, theme) VALUES (:id, :title, :message, :date, :location, :theme);", {"id":id, "title":title, "message":message, "date":date, "location":location, "theme":theme})
    rows = db.execute("SELECT title, message, date, location FROM events WHERE date < ;")
    db.commit()
    return render_template("home_page.html", rows=rows)
from flask import Flask, escape, request
import sqlite3
from sqlite3 import Error
from flask.templating import render_template
from werkzeug.utils import redirect

app = Flask(__name__)

def create_database(db_file):
    # create a database connection to a SQLite database
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        db = conn.cursor()
        db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER NOT NULL, title TEXT NOT NULL, message TEXT, date TEXT NOT NULL, location TEXT, theme TEXT NOT NULL); ")
        # print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

create_database("countdown.db")
db = sqlite3.connect("countdown.db")
cur = db.cursor()

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
    title = request.form.get("title")
    message = request.form.get("message")
    date = request.form.get("date")
    location = request.form.get("location")
    theme = request.form.get("theme")
    cur.execute("INSERT INTO events (id, title, message, date, location, theme) VALUES (:id, :title, :message, :date, :location, :theme);", {"id":id, "title":title, "message":message, "date":date, "location":location, "theme":theme})
    cur.commit()
    return redirect("/")
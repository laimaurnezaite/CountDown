import sqlite3
from flask import Flask, escape, request, session
from sqlite3 import Error
# from werkzeug.utils import redirect
# from datetime import date
# from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from flask_session import Session
from tempfile import mkdtemp


# from helpers import login_required, apology, check_if_available, get_db, get_cursor
app = Flask(__name__)
import countdown.routes

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


from flask.templating import render_template
from flask import Flask, escape, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect
from datetime import date

from countdown.app import app
from countdown.helpers import login_required, apology, check_if_available, get_db, get_cursor

@app.route("/form/register", methods=["GET"])
def render_register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    # check if username is available
    if check_if_available(username) == False:
        return apology(message = "Username is already taken")

    password = request.form.get("password")

    confirmation = request.form.get("confirmation")
    # check if passwords match
    if confirmation != password:
            return apology(message = "Passwords don't match")

    # if everything was ok, insert new user in DB
    db = get_db()
    db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash);", {
               "username": username, "hash": generate_password_hash(password)})
    db.commit()
    return redirect("/")


@app.route("/form/add-event", methods=["GET"])
@login_required
def render_add_event():
    cur = get_cursor()
    cur.execute("SELECT theme_id, name FROM themes;")
    themes = cur.fetchall()
    return render_template("add_event.html", themes=themes)


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
    db = get_db()
    db.execute("INSERT INTO events (person_id, title, message, date, location, theme) VALUES (:person_id, :title, :message, :date, :location, :theme);", {
               "person_id": person_id, "title": title.upper(), "message": message, "date": event_date, "location": location.upper(), "theme": theme})
    db.commit()
    return redirect("/")


@app.route("/", methods=["GET"])
@login_required
def homepage():
    person_id = session["user_id"]
    db = get_db()
    cur = get_cursor()
    today = date.today()
    cur.execute("SELECT title, message, date, location, link FROM events JOIN themes ON events.theme = themes.theme_id WHERE events.date > :today AND events.person_id = :person_id ORDER BY date", {"today": today, "person_id":person_id})
    rows = cur.fetchall()
    return render_template("homepage.html", rows=rows)

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
    rows = cur.fetchall()
    if len(rows) != 1 or not check_password_hash(rows[0][2], password):
        return apology(message = "invalid username and/or password")

    # Remember which user has logged in
    session["user_id"] = rows[0][0]
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

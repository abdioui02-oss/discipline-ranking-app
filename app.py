from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

tasks = {
    "study": 10,
    "gym": 10,
    "wake up": 5
}
@app.route("/")
def home():
    return render_template("index.html")

def get_all_users():
    connection = get_db_connection()
    users = connection.execute("SELECT * FROM users ORDER BY points DESC").fetchall()
    connection.close()
    return users

def get_task_history():
    connection = get_db_connection()
    history = connection.execute(
        "SELECT * FROM tasks_history ORDER BY id DESC"
    ).fetchall()
    connection.close()
    return history

@app.route("/history")
def history():
    history = get_task_history()
    return render_template("history.html", history=history)

@app.route("/leaderboard")
def leaderboard():
    users = get_all_users()
    return render_template("leaderboard.html", users=users)
def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection

def create_users_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            points INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()
def create_tasks_history_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            task_name TEXT NOT NULL,
            points INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()

create_users_table()
create_tasks_history_table()
@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    message = ""

    if request.method == "POST":
        name = request.form["username"].strip()

        if name == "":
            message = "Username cannot be empty"
        else:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
            existing_user = cursor.fetchone()

            if existing_user:
                message = "Username already exists"
            else:
                cursor.execute(
                    "INSERT INTO users (name, points) VALUES (?, ?)",
                    (name, 0)
                )
                connection.commit()
                message = f"User {name} added successfully"

            connection.close()

    return render_template("add_user.html", message=message)
@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    message = ""
    users = get_all_users()

    if len(users) == 0:
        message = "You need to add a user first"
        return render_template("add_task.html", users=users, tasks=tasks, message=message)

    if request.method == "POST":
        username = request.form["username"]
        task = request.form["task"]

        if task not in tasks:
            message = "Invalid task selected"
        else:
            points = tasks[task]

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "UPDATE users SET points = points + ? WHERE name = ?",
                (points, username))
            cursor.execute(
                "INSERT INTO tasks_history (username, task_name, points) VALUES (?, ?, ?)",
                (username, task, points))
            connection.commit()
            connection.close()

            message = f"Task added for {username}. +{points} points"

    users = get_all_users()
    return render_template("add_task.html", users=users, tasks=tasks, message=message)
if __name__ == "__main__":
    app.run(debug=True)
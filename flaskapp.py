import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__, static_folder="static")
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize database
DATABASE = "users.db"

def init_db():
    """Initialize the database and create the users table if it doesn't exist."""
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                email TEXT NOT NULL,
                file_path TEXT,
                word_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()

init_db()  # Run the database initialization

@app.route("/")
def home():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")

    # Handle file upload
    file = request.files.get("file")
    file_path = None
    word_count = 0

    if file and file.filename:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # Count words in the uploaded file
        with open(file_path, "r") as f:
            word_count = len(f.read().split())

    # Insert user data into database
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (username, password, firstname, lastname, email, file_path, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, password, firstname, lastname, email, file_path, word_count))
        conn.commit()

    return redirect(url_for("profile", username=username))

@app.route("/profile/<username>")
def profile(username):
    """Fetch and display user profile information."""
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

    if user:
        return render_template("profile.html", user=user)
    else:
        return "User not found", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from cryptography.fernet import Fernet
import os
import random
from datetime import datetime

app = Flask(__name__)

# Generate in bytes so Flask can handle it directly
# Secret key for maintaining security of sessions
app.secret_key = b'\x05\xf1\xcc\x14\xed\xfcs\x99\x86\xa71\xc2\x95Z\xef\x8a\xd5g\x17\xfc\x99\xea\x85\xe7\xfaM\xe7!\x9d\xe4i]'

# Load key from environment variable
key = os.environ.get('FLASK_ENCRYPTION_KEY').encode()
cipher = Fernet(key)

@app.route('/')
def index():
    return render_template("intro.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        repass = request.form.get("repass")

        # Input validation :)
        # Length check
        if len(password) < 8:
            return render_template("signup.html", error = "Password should be more than 8 characters)")

        # Check if retyped password matches
        if password != repass:
            return render_template("signup.html", error="Password does not match re-entered password")

        # Encrypt the password
        encrypted_password = cipher.encrypt(password.encode())
        conn = sqlite3.connect('account.db')
        cursor = conn.cursor()

        # Checks if user creates email with existing email
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        # If email already exists prompts an error
        if existing_user:
            return render_template("signup.html", error="An account with this email already exists.")

        # If not account gets created
        else:
            cursor.execute(
                "INSERT INTO users (username, user_password, email) VALUES (?, ?, ?)", 
                (username, encrypted_password, email))
        conn.commit()
        # Store the username of the user in this session to be used later
        session['username'] = username
        conn.close()
        return redirect(url_for('account_success'))
    return render_template("signup.html")

@app.route("/accountsuccess")
def account_success():
    return render_template("accountsuccess.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_email= request.form.get("loginemail")
        entered_password = request.form.get("loginpassword")

        # We validatin' inputs people :(
        
        # Check if email and password are provided
        if not entered_email or not entered_password:
            return render_template("login.html", error="Please enter both email and password.")
        
        # Check if user entered correct info
        conn = sqlite3.connect("account.db")
        c = conn.cursor()
        c.execute("SELECT username, user_password FROM users WHERE email = ?",
                (entered_email,))
        result = c.fetchone()
        conn.close()

        # Check email
        if result is None:
            return render_template("login.html", error_email = "Wrong email entered try again")

        # From result (extracted table line) since result is in a tuple
        username = result[0]

        # Check password
        # Decrypts encrypted stored password in db
        db_encrypted_password = result[1]
        decrypted_password = cipher.decrypt(db_encrypted_password).decode()
        
        if entered_password == decrypted_password:
            # Store the username in session
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error_password = "Wrong password entered. Try again")

    return render_template("login.html")




@app.route("/home", methods=["GET", "POST"])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session.get('username', '')

    # Prevent quote from refreshing
    if 'random_quote' not in session:
        quotes = ["We cannot solve problems with the kind of thinking we employed when we came up with them.",
                  "Learn as if you will live forever, live like you will die tomorrow.",
                  "Stay away from those people who try to disparage your ambitions. Small minds will always do that, but great minds will give you a feeling that you can become great too.",
                  "When you give joy to other people, you get more joy in return. You should give a good thought to the happiness that you can give out.",
                  "When you change your thoughts, remember to also change your world.",
                  "It is only when we take chances that our lives improve. The initial and the most difficult risk we need to take is to become honest.",
                  "Success is not final; failure is not fatal: It is the courage to continue that counts.",
                  "It is better to fail in originality than to succeed in imitation."
                  ]
        random_quote = random.choice(quotes)
        session['random_quote'] = random_quote
    else:
        random_quote = session['random_quote']

    if request.method == "POST":
        blog_input = request.form.get("text")
        if blog_input:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # yes cambridge my file closes after with block
            with open("blogs.txt","a") as file:
                file.write(f"{current_time}:\n{blog_input}\n")
    
    # Check if txt file exists
    if os.path.exists("blogs.txt"):
        if 'clear_all' in request.form:
            # once again cambridge/ mr lam my file closes after with block
            with open("blogs.txt", "w") as file:
                    file.write("")
        elif 'clear_last' in request.form:
            # once again cambridge/ mr lam my file closes after with block
            with open("blogs.txt", "r") as file:
                lines = file.readlines()

                if len(lines) > 1:
                    lines = lines[:-2]
            # once again cambridge/ mr lam my file closes after with block
            with open("blogs.txt", "w") as file:
                file.writelines(lines)

    all_blog = []
    one_line = []
    # Check if txt file exists
    if os.path.exists("blogs.txt"):
        # once again cambridge/ mr lam my file closes after with block
        with open("blogs.txt", "r") as file:
            for line in file:
                line = line.rstrip()
                if len(one_line) == 2:
                    all_blog.append(one_line)
                    one_line = []
                one_line.append(line)
                    
        
    return render_template("index.html", random_quote=random_quote, username=username, all_blog=all_blog)

if __name__ == '__main__':
    app.run(debug=True, port=10000)


#===========================================================
# PROJECT NAME HERE
# By YOUR NAME HERE
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *


# Create the app
app = Flask(__name__)
logged_in = False


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Home page - Show all notes
#-----------------------------------------------------------
@app.get("/")
def show_studios():
    with connect_db() as db:
        sql = """
            SELECT name
            FROM studios
        """
        params = ()
        studios = db.execute(sql, params).fetchall()

        flash("Test message")
        flash("Test SUCCESS message", "success")
        flash("Test INFO message", "info")
        flash("Test WARNING message", "warning")
        flash("Test ERROR message", "error")

        return render_template("pages/home.jinja", studios=studios)

#-----------------------------------------------------------
# Login page - Sign the user in
#-----------------------------------------------------------
@app.get("/login")
def login_info():
    with connect_db() as db:
        sql = """
            SELECT username, password
            FROM users
        """
        params = ()
        users = db.execute(sql, params).fetchall()

        return render_template("pages/login.jinja", users=users)
    
#-----------------------------------------------------------
# Sign up page - Create an account 
#-----------------------------------------------------------
@app.get("/signup")

@app.post("/signup")
def add_user():
    username = request.form.get('username', '').strip().lower()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    if "@waimea.school.nz" not in email:
        flash(f"Email must be a valid waimea email adress", "error")
        return redirect("/signup")

    with connect_db() as db:
        sql = "SELECT id FROM users WHERE username=?"
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/signup")

        pass_hash = generate_password_hash(password)

        sql = """
            INSERT INTO users (username, email, pass_hash)
            VALUES (?, ?, ?, ?)
        """
        params = (username, email, pass_hash)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
        return redirect("/login")
    
#-----------------------------------------------------------
# Help page - Useful information based on user state
#-----------------------------------------------------------
@app.get("/help")
def get():
    with connect_db() as db:
        sql = """
            SELECT staff
            FROM users
        """
        params = ()
        staff = db.execute(sql, params).fetchall()
        
        return render_template("pages/help.jinja", logged_in=logged_in, staff=staff)    
    
#-----------------------------------------------------------
# Studio page - display requested studio
#-----------------------------------------------------------
# @app.get("/studio/<int:id>")
# def get():
#     with connect_db() as db:
#         sql = """
#             SELECT staff
#             FROM users
#         """
#         params = ()
#         staff = db.execute(sql, params).fetchall()
        
#         return render_template("pages/help.jinja", logged_in=logged_in, staff=staff)  
    
    
#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)


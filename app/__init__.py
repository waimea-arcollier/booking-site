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
from datetime import date, timedelta


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
            SELECT username, pass_hash
            FROM users
        """
        params = ()
        users = db.execute(sql, params).fetchall()

        return render_template("pages/login.jinja", users=users)
    
@app.post("/login")
def login_user():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = """
            SELECT id, username, email, pass_hash, staff
            FROM users
            WHERE username=?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash(f"Unknown user", "error")
            return redirect("/login")

        if not check_password_hash(user["pass_hash"], password):
            flash(f"Incorrect password", "error")
            return redirect("/login")

        session["logged_in"] = True
        session["user"] = {
            "id":       user["id"],
            "username": user["username"],
            "email": user["email"],
            "staff":  user["staff"],
        }

        flash("Login successful", "success")
        return redirect("/")
#-----------------------------------------------------------
# Sign up page - Create an account 
#-----------------------------------------------------------
@app.get("/signup")
def show_signup():
    return render_template("pages/signup.jinja")

@app.post("/signup")
def add_user():
    username = request.form.get('username', '').strip().lower()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    
    if "@waimea.school.nz" in email:
        with connect_db() as db:
            sql = "SELECT id FROM users WHERE username=?"
            params = (username,)
            user = db.execute(sql, params).fetchone()

            if user:
                flash(f"Username '{username}' already exists", "error")
                return redirect("/signup")

            pass_hash = generate_password_hash(password)

            sql = """
                INSERT INTO users (username, email, pass_hash, staff)
                VALUES (?, ?, ?, 0)
            """
            params = (username, email, pass_hash)
            db.execute(sql, params)

            flash("Account created. Please login", "success")
            return redirect("/login")
    else:
        flash(f"Please use a valid Waimea College email adress", "error")
        return redirect("/signup")
    
#-----------------------------------------------------------
# Help page - Useful information based on user state
#-----------------------------------------------------------
@app.get("/help")
def show_help():
        return render_template("pages/help.jinja")    
    
#-----------------------------------------------------------
# Account page - Edit account info, logout, delete account
#-----------------------------------------------------------
@app.get("/account")
@login_required
def show_account():
    #use the session info? remember how to edit. another form so more routes.
        return render_template("pages/account.jinja")
    
@app.post("/edit/<int:id>")
def edit_info_post(id):
    # Get the data from the form
    username = request.form.get('username', '').strip().lower()
    email = request.form.get('email', '').strip().lower()

    if "@waimea.school.nz" in email:
        with connect_db() as client:
            # Add the thing to the DB
            sql ="""UPDATE users
                    SET username = ?, email = ?
                    WHERE id = ?
                """
            params = [username, email, id,]
            client.execute(sql, params)
        

            session["user"]["email"] = email
            session["user"]["username"] = username
            session.modified = True
            
            flash("Account info updated sucessfully", "success")
            
            # Go back
            return redirect("/account")
    else:
        flash(f"Please use a valid Waimea College email adress", "error")
        return redirect("/account")

#-----------------------------------------------------------
# Book page - Book a studio for a timeslot 
#-----------------------------------------------------------
@app.get("/book")
@login_required
def show_book():
    #form so will need a post route too. select name, id from studios
        return render_template("pages/book.jinja")
   
#-----------------------------------------------------------
# Bookings page - Displays the users bookings for the week
#-----------------------------------------------------------
@app.get("/bookings")
@login_required
def show_bookings():
    #something like select studio_booked, day_booked, time,booked where user.id = user_booked ??
        return render_template("pages/bookings.jinja")
       
#-----------------------------------------------------------
# Studio page - display requested studio (idk wtf is going on)
#-----------------------------------------------------------
# @app.get("/studio/<int:id>")
# def get():
#     with connect_db() as client:
#         # Get the workout details from the DB
#         sql = "SELECT id, name FROM studios WHERE id=?"
#         params = [id]
#         result = client.execute(sql, params)
        
#         # Did we get a result?
#         if result.rows:
#             # yes, so show it on the page
#             studio = result.rows[0]
            
#             user_id = session["user"]["id"]
            
#             # Get the workout details from the DB
#             sql = "SELECT studio_booked, day_booked, time_booked FROM sessions WHERE studio_booked=? WHERE user_booked=? ORDER BY date DESC"
#             params = [id, user_id]
#             result = client.execute(sql, params)
#             sessions = result.rows

#             return render_template("pages/workout.jinja", studio=studio, sessions=sessions)

#         else:
#             # No, so show error
#             return not_found_error() 
    
#-----------------------------------------------------------
# Logout - clear the session
#-----------------------------------------------------------
@app.get("/logout")
def logout_user():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/")

#-----------------------------------------------------------
# Delete account
#-----------------------------------------------------------
@app.get("/temp")
@login_required
def temp():
        return render_template("pages/temp.jinja")
    
@app.get("/delete")
def delete_user():
    id = session["user"]["id"]
    with connect_db() as db:
        sql = "DELETE FROM users WHERE id = ?"
        params = (id,)
        db.execute(sql, params)
        session.clear()
        flash(f"Your account has been deleted.", "success")
        return redirect("/")
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


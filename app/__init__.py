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
            SELECT name, id
            FROM studios
        """
        params = ()
        studios = db.execute(sql, params).fetchall()
        
        flash("Test message")

        time = timedelta()
        weekday = date.today().isoweekday()
        
        
        print("============================================")
        print(time)
        print(weekday)

        return render_template("pages/home.jinja", studios=studios, time=time, weekday = weekday)

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
@login_required
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
# Bookings page - Displays the users bookings for the week
#-----------------------------------------------------------
@app.get("/bookings")
@login_required
def show_bookings():
    id = session["user"]["id"]
    with connect_db() as db:
        sql = """SELECT 
                    bookings.id,
                    bookings.studio_booked, 
                    bookings.day_booked, 
                    bookings.time_booked,
                    bookings.note,
                    studios.name,
                    timeslots.display_name

                FROM bookings 
                JOIN studios ON studios.id = bookings.studio_booked
                JOIN timeslots ON timeslots.id = bookings.time_booked

                WHERE bookings.user_booked=?
                ORDER by bookings.time_booked asc
                """
        params = (id,)
        bookings = db.execute(sql, params).fetchall()
        print("============================================")
        print(bookings)
        return render_template("pages/bookings.jinja", bookings=bookings)
       
#-----------------------------------------------------------
# Studio page - display requested studio (idk wtf is going on)
#-----------------------------------------------------------
@app.get("/studio/<int:id>")
def get(id):
    with connect_db() as db:
        # Get the studio details from the DB
        sql = "SELECT id, name FROM studios WHERE id=?"
        params = (id,)
        studio = db.execute(sql, params).fetchone()
            
        # Get the studio details from the DB
        sql = "SELECT id, display_name, staff_only FROM timeslots"
        params = ()
        slots = db.execute(sql, params).fetchall()
        
        # List of days
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        
        # Get the workout details from the DB
        sql = """
            SELECT 
                bookings.studio_booked, 
                bookings.day_booked, 
                bookings.time_booked,
                bookings.user_booked,
                bookings.note
                
            FROM bookings 
            JOIN users ON users.id = bookings.user_booked
            
            WHERE bookings.studio_booked=?
        """
        params = (id,)
        bookings = db.execute(sql, params).fetchall()   

        return render_template("pages/studio.jinja", studio=studio, slots=slots, days=days, bookings=bookings)
    
#-----------------------------------------------------------
# Make booking
#-----------------------------------------------------------
@app.post("/booking")
@login_required
def booking_new():
    # Get the data from the form
    studio = request.form.get('studio', '')
    day = request.form.get('day', '')
    slot = request.form.get('slot', '')

    print("============================================")
    print(studio)
    print(slot)
    print(day)
    
    with connect_db() as db:
        sql ="""
            SELECT
                 name
            FROM studios
            
            WHERE id = ?
            
            """
        params = [studio]
        studio_name = db.execute(sql, params).fetchone()

    with connect_db() as db:
        sql =""" 
            SELECT 
                timeslots.display_name
            FROM timeslots
            
            WHERE timeslots.id = ?
            """
        params = [slot]
        slot_name = db.execute(sql, params).fetchone()
        
    print("============================================")
    print(studio_name)
    print(slot_name)
        
    return render_template("pages/booking.jinja", studio=studio, day=day, slot=slot, studio_name=studio_name, slot_name=slot_name)
    
@app.post("/booking/new")
@login_required
def booking_new_post():
    # Get the data from the form
    studio = request.form.get('studio', '')
    day = request.form.get('day', '')
    slot = request.form.get('slot', '')
    note = request.form.get('note', '')
    id = session["user"]["id"]
    staff = session["user"]["staff"]
    
    with connect_db() as db:
        sql="""
            SELECT 
                id 
            FROM bookings

            WHERE user_booked = ?
        """
        params = [id]
        user_bookings = db.execute(sql, params).fetchall()
        user_bookings = len(user_bookings)
        
        if (user_bookings < 3) or (staff):
            with connect_db() as client:
                # Add the thing to the DB
                sql ="""  
                        INSERT INTO bookings (studio_booked, user_booked, day_booked, time_booked, note)
                        VALUES (?, ?, ?, ?, ?)
                    """
                params = [studio, id, day, slot, note]
                client.execute(sql, params)
                
                flash("Slot sucessfully booked", "success")
                
                # Go back
                return redirect("/bookings")
        else:
            flash("You have reached this weeks booking limit.", "error")
            return redirect("/")
          
#-----------------------------------------------------------
# Delete booking
#-----------------------------------------------------------
@app.get("/delete/booking/<int:id>")
@login_required
def delete_account(id):
    with connect_db() as db:
        sql = """
            SELECT 
                bookings.studio_booked, 
                bookings.day_booked, 
                bookings.time_booked,
                studios.name,
                timeslots.display_name

                FROM bookings 
                JOIN studios ON studios.id = bookings.studio_booked
                JOIN timeslots ON timeslots.id = bookings.time_booked

                WHERE bookings.id=?
        """
        params = (id,)
        db.execute(sql, params)
        booking = db.execute(sql, params).fetchone() 
        
        sql = " DELETE FROM bookings WHERE id = ?"
        params = (id,)
        db.execute(sql, params)
        flash(f"Booking for {booking["display_name"]} on {booking["day_booked"]} for {booking["name"]} cancelled sucessfully", "success")
        return redirect("/bookings")
#-----------------------------------------------------------
# Logout - clear the session
#-----------------------------------------------------------
@app.get("/logout")
@login_required
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
@login_required
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


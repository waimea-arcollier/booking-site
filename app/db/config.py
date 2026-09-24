#============================================================================
# Database schema and seed data configuration
#============================================================================


#----------------------------------------------------------------------------
# Table definitions
#----------------------------------------------------------------------------
# Define your tables with a name, a schema and optional seed/sample data,
# using this format, and then add the tables to the Table Registry below:
#
# class TableName:
#     NAME      = "name"
#     SCHEMA    = "CREATE TABLE name (...)"
#     SEED_DATA = "INSERT INTO name (...)" or None
#----------------------------------------------------------------------------


class UsersTable:

    NAME = "users"

    SCHEMA = """
        CREATE TABLE users (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            email   TEXT NOT NULL   ,
            password  TEXT NOT NULL,
            staff BOOLEAN NOT NULL
        )
    """
    SEED_DATA = """
    INSERT INTO users (username, email, pass_hash, staff)
    VALUES
        ("test", "test.school.nz", ""scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252"", false)
    """

class StudiosTable:

    NAME = "studios"

    SCHEMA = """
        CREATE TABLE studios (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name   TEXT NOT NULL,
            image_file   TEXT    
        )
    """

    SEED_DATA = """
        INSERT INTO studios (name)
        VALUES
            ("Studio 3"),
            ("Studio 4"),
            ("Studio 5"),
            ("Band Room")
    """

class TimeslotsTable:

    NAME = "timeslots"

    SCHEMA = """
        CREATE TABLE timeslots (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name  TEXT NOT NULL,
            staff_only BOOLEAN, 
            time_start  TEXT,
            time_end  TEXT 
        )
    """

    SEED_DATA = """
        INSERT INTO timeslots (display_name, staff_only, time_start, time_end)
        VALUES
            ("Before School", false, "0:00", "9:00"),
            ("Period 1", true, "9:01", "10:00"),
            ("Period 2", true, "10:01", "11:00"),
            ("Break 1", false, "11:01", "11:25"),
            ("Period 3", true, "11:26", "12:25"),
            ("Period 4", true, "12:26", "13:25"),
            ("Break 2", false, "13:26", "14:10"),
            ("Period 5", true, "14:11", "15:10"),
            ("After School", false, "15:11", "23:59")
            
    """

class BookingsTable:

    NAME = "bookings"

    SCHEMA = """
        CREATE TABLE bookings (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            studio_booked   INTEGER,
            user_booked   INTEGER,
            admin_booked, BOOLEAN
            day_booked  TEXT NOT NULL,
            time_booked  INTEGER 
        )
    """
    SEED_DATA = """
    INSERT INTO bookings (studio_booked, user_booked, admin_booked, day_booked, time_booked)
    VALUES
        (1, 1, 1, "Mon", 4)
        (2, 2, 0, "Wed", 4)
        (4, 2, 0, "Thu", 4)
        (3, 2, 0, "Tue", 4)
    """
# Add more table classes here...



#----------------------------------------------------------------------------
# Table registry
#----------------------------------------------------------------------------
# Register all of your tables by adding them to the TABLES list here:
#
# TABLES = [
#     Table1Name,
#     Table2Name,
#     etc.
# ]
#
# Note: The table order is important - Create the tables that have
# foreign keys *after* the tables they link to have been created
#----------------------------------------------------------------------------

TABLES = [
    BookingsTable,
    UsersTable,
    StudiosTable,
    TimeslotsTable
    # Add more tables here...
]


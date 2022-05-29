import sqlite3 as sql

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

DATABASE_PATH = os.environ.get("DATABASE_PATH")

# ---------------------------------------------------------------------------- #
#                              Database functions                              #
# ---------------------------------------------------------------------------- #

# ------------------------------- Create tables ------------------------------ #
def create_users_table():
    """Create a users table if it doesn't exist, will also create database.db if it doesn't exist"""
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            username TEXT,
            password TEXT,
            base_url TEXT
        );
        """)

def create_classes_table():
    """Create a classes table if it doesn't exist, will also create database.db if it doesn't exist"""
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            email TEXT,
            class TEXT,
            synonym TEXT
        );
        """)

def create_terms_table():
    """Create a terms table if it doesn't exist, will also create database.db if it doesn't exist"""
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            email TEXT,
            term TEXT
        );
        """)

def create_recovery_table():
    """Create a recovery codes table if it doesn't exist, will also create database.db if it doesn't exist"""
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS recovery (
            email TEXT,
            recovery_code TEXT
        );
        """)

def create_tables():
    """Create tables for users, classes, and terms table if they don't exist"""
    create_users_table()
    create_classes_table()
    create_terms_table()
    create_recovery_table()

# -------------------------------- User table -------------------------------- #
def add_user_to_database(email, username, password, base_url):
    con = sql.connect(DATABASE_PATH)
    # Add user to database
    with con:
        con.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (email, username, password, base_url))

def get_user_from_database(email):
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM users WHERE email = ?", (email,))
        for row in data: return row[1], row[2], row[3] # Hopefully there is just one email
    return None, None, None # If there is no user, return None, None, None which should ask the user to create an account

def set_user_info(email, username, base_url):
    """Sets the username and base url for the user with the given email

    Args:
        email (str): Email address of the user
        username (str): Username of the user
        base_url (str): Base url of the user
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("UPDATE users SET username = ?, base_url = ? WHERE email = ?", (username, base_url, email))

def change_password(email, new_password):
    """Changes the password of the user with the given email

    Args:
        email (str): Email of the user
        new_password (str): New password of the user
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))

def delete_user_from_database(email):
    con = sql.connect(DATABASE_PATH)
    # Password must also be provided to delete a user
    with con:
        con.execute("DELETE FROM users WHERE email = ?", (email,))

def check_user_exists(email):
    """Checks if the user with the given email exists in the database

    Args:
        email (str): Email address of the user to check

    Returns:
        bool: Whether the user exists
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM users WHERE email = ?", (email,))
        for row in data: return True
    return False

# Email and password verification function
def verify_email_and_password(email, password):
    """Checks the email against the password in the database to ensure that the user is allowed to perform an action

    Args:
        email (str): Email address of the user trying to perform an action
        password (str): Password of the user trying to perform an action

    Returns:
        bool: Whether the user is allowed to perform an action
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        for row in data: return True # If a row exists where the email and password match, return True
    return False # If no row exists, return False

# -------------------------------- Term table -------------------------------- #
def add_term_to_database(email, term):
    """Adds a term to the terms database for the user with the given email

    Args:
        email (str): Email address of the user
        term (str): Term from the form
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("INSERT INTO terms VALUES (?, ?)", (email, term))

def delete_term_from_database(email):
    """Removes any terms from the terms database if they exist for the user with the given email

    Args:
        email (str): Email to delete terms for
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("DELETE FROM terms WHERE email = ?", (email,))

def get_term_from_database(email):
    """Returns the term set for the user with the given email

    Args:
        email (str): Email address of the user

    Returns:
        str: Term set for the user
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM terms WHERE email = ?", (email,))
        for row in data: return row[1]

# ------------------------------- Classes table ------------------------------ #
def add_classes_to_database(email, classes):
    """Adds classes and synonyms to the classes database for the user with the given email

    Args:
        email (str): Email address of the user to add classes to
        classes (dict): Classes to be added to the user
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        for class_name in classes:
            for synonym in classes[class_name]:
                con.execute("INSERT INTO classes VALUES (?, ?, ?)", (email, class_name, synonym))

def remove_classes_from_database(email):
    """Removes all classes and synonyms from the classes database for the user with the given email

    Args:
        email (str): Email address of the user to remove classes from
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("DELETE FROM classes WHERE email = ?", (email,))

def evaluate_class_from_synonym(email, synonym):
    """Returns the user's class name as it appears in PowerSchool for the given synonym

    Args:
        email (str): Email address of the user
        synonym (str): Class name synonym to evaluate

    Returns:
        str: Class name as it appears in PowerSchool
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM classes WHERE email = ? AND synonym = ?", (email, synonym))
        for row in data: return row[1] # If a row exists where the email and synonym match, return the class

# ------------------------------ Recovery table ------------------------------ #
def add_recovery_to_database(email, recovery_code):
    """Adds a term to the terms database for the user with the given email

    Args:
        email (str): Email address of the user
        recovery_code (int): Term from the form
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("INSERT INTO recovery VALUES (?, ?)", (email, recovery_code))

def delete_recovery_from_database(email):
    """Removes any recovery codes from the terms database if they exist for the user with the given email

    Args:
        email (str): Email to delete terms for
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        con.execute("DELETE FROM recovery WHERE email = ?", (email,))

def get_code_from_database(email):
    """Returns the recovery code for the user with the given email

    Args:
        email (str): Email address of the user

    Returns:
        int: Recovery code for the user
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM recovery WHERE email = ?", (email,))
        for row in data: return row[1]

def verify_recovery(email, code):
    """Checks the recovery code for the user with the given email against the given code

    Args:
        email (str): Email address of the user
    """    
    con = sql.connect(DATABASE_PATH)
    with con:
        data = con.execute("SELECT * FROM recovery WHERE email = ? AND recovery_code = ?", (email, code))
        for row in data: return True # If a row exists where the email and recovery code match, return True

# -------------------------------- Delete user ------------------------------- #
def delete_user(email):
    """Removes all data from the database for the user with the given email

    Args:
        email (str): Email address of the user
    """    
    delete_user_from_database(email)
    delete_term_from_database(email)
    remove_classes_from_database(email)
    delete_recovery_from_database(email)
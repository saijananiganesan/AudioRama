import sqlite3
import time
import datetime
import random

conn = sqlite3.connect('user_database.db')
c=conn.cursor()

def create_users_table():
    conn = sqlite3.connect('user_database.db')
    c=conn.cursor()
    print ("Opened database successfully")
    c.execute('CREATE TABLE IF NOT EXISTS users (date TEXT, login TEXT, email TEXT)')
    date=datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y')
    return date,c,conn    

def create_login_table():
    conn = sqlite3.connect('user_database.db')
    c=conn.cursor()
    print ("Opened database successfully")
    c.execute('CREATE TABLE IF NOT EXISTS login (date TEXT, login TEXT, email TEXT)')
    date=datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y')
    return date,c,conn

def create_feedback_table():
    conn = sqlite3.connect('user_database.db')
    c=conn.cursor()
    print ("Opened database successfully")
    c.execute('CREATE TABLE IF NOT EXISTS feedback (date TEXT, login TEXT, email TEXT, useful TEXT, subject TEXT)')
    date=datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y')
    return date,c,conn


def read_from_db():
    c.execute('SELECT * FROM feedback')
    data=c.fetchall()
    print (data)

#create_feedback_table()
#conn.close()
read_from_db()

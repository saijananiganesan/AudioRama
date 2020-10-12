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

def read_from_db():
    c.execute('SELECT * FROM login')
    data=c.fetchall()
    print (data)

#conn.close()
read_from_db()

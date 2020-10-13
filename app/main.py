from flask import Flask, flash, render_template, request, url_for, redirect
import jinja2
import os,sys
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import numpy as np
import sqlite3 as sql
from dbconnect import create_users_table,create_login_table
import gensim
import pickle

#############
#JINJA
#############
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)

def write_html(Template_Dict, template_file,output_file):
    template = templateEnv.get_template('templates/'+template_file)
    outputText=template.render(Template_Dict)
    with open(os.path.join('templates/',output_file),"w") as fh:
        fh.write(outputText)
#############

#############
#FLASK
#############
app = Flask(__name__)        
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route("/")
@app.route("/home/")
def home():
    return render_template("home.html")

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/exp1/")
def exp1():
    return render_template("exp1.html")

@app.route("/exp2/")
def exp2():
    return render_template("exp2.html")

@app.route("/application/")
def application():
    if name and email:
        return render_template("application.html")
    else:
        return "<h1>Please fill your details to proceed.</h1>"

@app.route('/exp1/info/')
@app.route('/info/')
def info():
    return render_template('final_summary_set_cathist.html')

@app.route('/exp1/nar/')
@app.route('/nar/')
def nar():
    return render_template('final_summary_set_narhist.html')

@app.route('/exp1/narcat/')
@app.route('/narcat/')
def narcat():
    return render_template('final_summary_set_narcathist.html')

@app.route('/exp1/catclus/')
@app.route('/catclus/')
def catclus():
    return render_template('final_summary_set_cat.html')

@app.route('/exp1/narclus/')
@app.route('/narclus/')
def narclus():
    return render_template('final_summary_set_nar.html')

@app.route('/exp2/usr/')
@app.route('/usr/')
def usr():
    return render_template('users.html')


@app.route('/form/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        global name
        name=request.form['Name']
        global email
        email=request.form['Email']
        if name and email:
            date,c, conn = create_users_table()
            entry_exists=c.execute("SELECT EXISTS (SELECT 1 FROM users WHERE login=?) AND (SELECT 1 FROM users WHERE email=?)",(name,email)).fetchall()[0][0]
            if entry_exists==0:
                c.execute('INSERT INTO users (date, login, email) VALUES (?,?,?)',(date, name, email))
                conn.commit()
            date,c1, conn1 = create_login_table()
            c1.execute('INSERT INTO login (date, login, email) VALUES (?,?,?)',(date, name, email))
            conn1.commit()
            return redirect(url_for('application'))
        else:
            return "<h1>Please fill your details to proceed.</h1>"

    return render_template('form.html')

if __name__ == "__main__":
    app.run(debug=True)

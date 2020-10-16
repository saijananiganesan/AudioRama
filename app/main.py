from flask import Flask, flash, render_template, request, url_for, redirect
import jinja2
import os,sys
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('mode.chained_assignment', None)
import numpy as np
import sqlite3 as sql
from dbconnect import create_users_table,create_login_table,create_feedback_table
import gensim
import pickle
from gensim.parsing.preprocessing import stem,strip_numeric,strip_punctuation,strip_short
from gensim.parsing.preprocessing import remove_stopwords
import gensim.downloader as api
import networkx as nx
import numpy as np
from bs4 import BeautifulSoup
import requests
import pickle
from re import search
from time import sleep
import pandas as pd
import sys

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
#PYTHON FUNCTIONS
#############

def clean_summary_text(var):
    try:
        m=re.search(r"[©®™]", var)
        val=var[:m.start()]
    except:
        val=var
    return val

def cosine_sim(target,query):
    cosine_similarity = round(np.dot(query, target)/(np.linalg.norm(query)* np.linalg.norm(target)),2)
    return cosine_similarity

def bookL(target):
    book='https://www.audible.com'+target
    return book


def get_summary_data(book_link):
    try:
        page=requests.get(book_link)
    except:
        try:
            time.sleep(0.5)
            page=requests.get(book_link)
        except:
            summary='None'
    page_details= BeautifulSoup(page.content, 'html.parser')
    summary=[p.get_text().replace('\n','') for p in page_details.findAll('div',{'class':'bc-section bc-spacing-medium'})]
    return summary

#############
#FLASK INPUT
#############

#glove_model = api.load("glove-wiki-gigaword-300")
#final_df=pd.read_pickle("data/final_summary_set.pkl")
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

@app.route("/Results/")
def Results():
    return render_template("Results.html")


@app.route("/application/",methods=['GET','POST'])
def application():
    if request.method=='POST':
        book_link=request.form['list']
        book_name=' '.join(book_link.split('/')[4].split('-')[:-1])
        summary=get_summary_data(book_link)
        text1=clean_summary_text(' '.join(summary).replace('\xa0','').replace('\xad',''))
        text2=list(set((strip_short(strip_punctuation(strip_numeric(remove_stopwords(text1))))).split()))
        glove_model = api.load("glove-wiki-gigaword-300")
        text3=[i for i in text2 if i in glove_model.vocab]
        query=np.mean(glove_model[text3],axis=0)
        final_df=pd.read_pickle("../../data/final_summary_mv.pkl")
        final_df['comparison']=final_df['mean_vector'].apply(cosine_sim,query=query) 
        final_df['Book_Link']=final_df['Book Link'].apply(bookL)
        final_df=final_df[~final_df['Book Name'].isin([book_name])]
        final=final_df.sort_values('comparison',ascending=False).iloc[:15,:][['Book Name','Author Names','Narrator Names','Book_Link']]
        final_print=final.drop_duplicates().iloc[1:11,:].values.tolist()
        final_print.insert(0,['Book Name','Author Name','Narrator Name','Book Link'])
        Template_Dict={}
        Template_Dict['book_name']=book_name
        Template_Dict['results_table']=final_print
        write_html(Template_Dict,"temp.html","Results.html")
        print ("written template")
        return redirect(url_for('Results'))


    return render_template("application.html")

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
        name=request.form['Name']
        email=request.form['Email']
        useful=request.form['useful']
        subject=request.form['subject']
        if not name: name='UNK'
        if not email: email='UNK'
        if not useful: useful='UNK'
        if not subject: subject='UNK'
        date,c, conn = create_feedback_table()
        c.execute('INSERT INTO feedback (date, login, email, useful, subject) VALUES (?,?,?,?,?)',(date, name, email, useful, subject))
        conn.commit()
        return redirect(url_for('home'))
    return render_template('form.html')

if __name__ == "__main__":
    app.run(debug=True)

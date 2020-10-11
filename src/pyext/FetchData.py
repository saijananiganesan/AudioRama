from bs4 import BeautifulSoup
import requests
import pickle
from re import search
from time import sleep
import pandas as pd
import sys
path='../../data/'

def fetch_and_clean_data(fname='Audible_metadata.csv'):
    df=pd.read_csv(fname)
    cleaned=df.drop('Unnamed: 0',1)
    cleaned=cleaned[cleaned['Category']!='Category']
    cleaned= cleaned.astype(str)
    cleaned['Release Date'] = pd.to_datetime(cleaned['Release Date'],errors='coerce')
    cleaned['Runtime']=cleaned.Runtime.apply(convert_runtime)
    cleaned['Ratings']=cleaned.Ratings.apply(convert_ratings)
    cleaned['Reviewers']=cleaned.Reviewers.apply(convert_reviewers)
    return cleaned

def convert_runtime(length):
    if 'min' in length and 'hr' in length:
        hrs = int(length.split(' hr')[0].replace(' ',''))
        mins = int(length.split('min')[0].split('and ')[1].replace(' ',''))
        total = hrs + mins/60
    elif 'min' in length:
        total = int(length.split('min')[0].replace(' ',''))/60
    elif 'hr' in length:
        total = int(length.split('hr')[0].replace(' ',''))
    else:
        total = 0
    return total

def convert_ratings(rate):
    if 'None' in rate:
        rate_=0
    else:
        rate_=int(rate)
    return rate_

def convert_reviewers(rev):
    if 'None' in rev:
        rev_=0
    elif ',' in rev:
        rev_=int(rev.replace(',',''))
    else:
        rev_=int(rev)
    return rev_

def mute_colors(axis):
    for patch in axis.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, .3))
def save_data_by_cat(book_dict,category):
    '''
    get data for each catehory and save to csv
    '''
    lst=[];link_head='https://www.audible.com'
    for key,val in book_dict.items():
        weblink=link_head+val
        try:
            syn_page=requests.get(weblink)
        except:
            try:
                time.sleep(0.5)
                syn_page=requests.get(weblink)
            except:
                pass
        syn_page_details= BeautifulSoup(syn_page.content, 'html.parser')
        final_text=get_information_from_a_page(syn_page_details)
        #print ("got information from %s"%key)
        lst.append([category,key,final_text])       
    final_df=pd.DataFrame(lst, columns=['Category','Book Name',\
                              'Book Synopsis'])
    #final_df.drop_duplicates(inplace=True) #.reset_index(inplace=True)
    final_df.to_csv(category.replace(" ", "")+'_synopsis_df.csv')

def get_information_from_a_page(page_info):
    '''
    given a link, get all relevant metadata from a page
    '''
    mydivs_page = [b.get_text() for a in page_info.findAll("span",{"class":"bc-text bc-color-secondary"}) 
                          for b in a.findAll("p") ]             
    final_text="".join(mydivs_page).replace(u'\xa0', u' ')
    return final_text

def get_dict_by_cat(df):
    for i in df['Category'].unique()[1:3]:
        df_short=df[df['Category']==i]
        Book_link_dict = dict(zip(df_short['Book Name'], df_short['Book Link']))
        save_data_by_cat(Book_link_dict,i)
        print ("Just saved %s category"%i)
        
def get_review(df,m,n):
    revs=dict()
    for i in df['Book Link'].unique()[m:n]:
        weblink='https://www.audible.com'+i
        try:
            page=requests.get(weblink)
        except:
            try:
                time.sleep(0.5)
                page=requests.get(weblink)
            except:
                pass
        #page=requests.get(weblink)
        page_details= BeautifulSoup(page.content, 'html.parser')
        rev=[p.get_text() for p in page_details.findAll('p',{"class":"bc-text bc-spacing-small bc-spacing-top-none bc-size-body bc-color-secondary"})]
        revs[i]=rev 
        #print (revs)
    rev_df=pd.DataFrame(revs.items(), columns=['Book Link', 'Reviews'])
    rev_df.to_csv('Book_Review_df_'+str(m)+'_'+str(n)+'.csv')
    return rev_df

def get_user_data_from_revs(df,m,n):
    users=[]
    for i in df['Book Link'].unique()[m:n]:
        weblink='https://www.audible.com'+i
        try:
            page=requests.get(weblink)
        except:
            try:
                time.sleep(0.5)
                page=requests.get(weblink)
            except:
                pass
        #page=requests.get(weblink)
        page_details= BeautifulSoup(page.content, 'html.parser')
        users.append([(p.get_text(),AUD+p['href']) for p in page_details.findAll('a',{"class":"bc-link bc-color-link"})
                    if 'listener' in p['href'] and '\n' not in p.get_text()])
    with open('users_'+str(m)+'_'+str(n)+'.pkl', 'wb') as f:
        pickle.dump(users, f)

def get_user_data(tuple_list,no):
    users={}
    for item in tuple_list:
        try:
            rev_page=requests.get(item[1])
        except:
            try:
                time.sleep(0.5)
                rev_page=requests.get(item[1])
            except:
                pass
        rev_page_details= BeautifulSoup(rev_page.content, 'html.parser')
        rev_check=[p.get_text().replace('\n','') for p in rev_page_details.findAll('span',{"class":"bc-text bc-size-large bc-text-bold"}) ]
        try:
            if int(rev_check[0]) >1 :
                temp=[p.get_text() for p in rev_page_details.findAll('a',{"class":"bc-link bc-color-link"})]
                users[item[0]]=[temp[i+2] for i,j in enumerate(temp[1:]) if '\n' in j]
        except:
            pass
    with open('usersF_'+str(no)+'.pkl', 'wb') as f:
        pickle.dump(users, f)

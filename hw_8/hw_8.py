import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
from pybtex.database import parse_file
from pybtex.richtext import String
import sqlite3
import os.path
from bib2db import bib_to_db #bib2py is a set of functions I wrote to convert the .bib file to a .db

#setting up flask
app = Flask(__name__)
#this section sets up all the directories for file upload
if os.path.isdir('uploads'):
    UPLOAD_FOLDER = 'uploads'
else:
    os.mkdir('uploads')
    UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['bib'])
DB_NAME = 'uploads/uploaded_citations.db'
TBL_NAME = 'query_table'

def clear_db():
    """"This function clears the database on startup in order to make sure
    tests of the website do not end up filling the database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cmd1 = """DROP TABLE IF EXISTS {}""".format(TBL_NAME)
    cursor.execute(cmd1)
    sql_cmd = """CREATE TABLE {} (id INTEGER PRIMARY KEY AUTOINCREMENT, cit_key TEXT, author_list TEXT, journal TEXT, volume INT, pages TEXT, year INT, title TEXT, collection TEXT)""".format(TBL_NAME)
    cursor.execute(sql_cmd)
    conn.commit()
    conn.close()
clear_db()


#function for homepage
@app.route('/', methods=['GET'])
def home_page():
    """This function renders the homepage and lists the current collections held."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT collection FROM {} ".format(TBL_NAME))
    collects_present = [clct[0] for clct in cursor.fetchall()]
    conn.commit()
    conn.close()
    return render_template('index.html', collects_present = collects_present)

# All the functions for .bib file upload and file upload page
def allowed_file(filename):
    """This function is called by upload file to make sure only
     .bib files are uploaded."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/insert', methods=['GET', 'POST'])
def upload_file():
    """This function renders the insertion page and does the insertion of bib data
    to the database."""
    print(request.files)
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files['file']
        print(request.files)
        if 'file' not in request.files:
            return render_template('insert.html')
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return render_template('insert.html')
        if file and allowed_file(file.filename):
            collection_name = request.form['collection_name']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            fname = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            bib_to_db(fname,collection_name,DB_NAME, TBL_NAME)
            return redirect(url_for('home_page'))
    return render_template('insert.html')

#Function for querying
@app.route('/search', methods=['GET', 'POST'])
def search_stuff():
    """"This function first queries the database and then taking the results from that
    query parses them to be displayed on the /search page"""
    col_names = ['Citation Key','Author List','Journal','Volume','Pages','Year','Title','Collection']
    print(request.form)
    results = []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT collection FROM {};".format(TBL_NAME))
    collects_present = [clct[0] for clct in cursor.fetchall()]
    if len(collects_present) == 0:
        collects_present = False
    else:
        collects_present = True
        if request.method == 'POST':
            query_str = request.form['query_str']
            search = "SELECT * FROM {} WHERE ".format(TBL_NAME) + query_str + ';'
            cursor.execute(search)
            query_out = cursor.fetchall()
            citation = ""
            for cite in query_out:
                for idx, item in enumerate(cite[1:]):
                    citation += col_names[idx] + ': '+ str(item) + '<br>'
                results.append(citation)
                citation = ""
            return render_template('query.html', collects_present=collects_present, results = results)
    return render_template('query.html', collects_present=collects_present, results = results)

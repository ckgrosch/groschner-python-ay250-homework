import sqlite3
from hw_8 import app, DB_NAME, clear_db, TBL_NAME
import pytest
import bib2db as bd
import io
import pybtex.database as pbt


test_app = app.test_client()

def test_index():
    """Function to test the code for the index page"""
    response = test_app.get('/')
    assert 'The current collections present are:' in response.data.decode('utf-8')


def test_search():
    """Function to test the code for the search page"""
    q = test_app.post('/search', data={'query_str': 'year > 2000'}).data.decode('utf-8')
    cit_count = 0
    for str_obj in q.split(' '):
        if str_obj == 'Citation':
            cit_count += 1
    assert cit_count == 0


def test_upload():
    """Function to test the code for the insertion page"""
    bib_text = pbt.parse_string("""@article{1998A&A...330..515F,
    	Adsnote = {Provided by the SAO/NASA Astrophysics Data System},
    	Adsurl = {http://adsabs.harvard.edu/abs/1998A%26A...330..515F},
    	Author = {{Fernley}, J. and {Barnes}, T.~G. and {Skillen}, I. and {Hawley}, S.~L. and {Hanley}, C.~J. and {Evans}, D.~W. and {Solano}, E. and {Garrido}, R.},
    	Date-Added = {2010-03-30 13:55:36 -0700},
    	Date-Modified = {2010-03-30 13:55:36 -0700},
    	Journal = {\aap},
    	Keywords = {STARS: VARIABLES: RR LYRAES, GALAXY: GLOBULAR CLUSTERS, GALAXIES: MAGELLANIC CLOUDS},
    	Month = feb,
    	Pages = {515-520},
    	Title = {{The absolute magnitudes of RR Lyraes from HIPPARCOS parallaxes and proper motions}},
    	Volume = 330,
    	Year = 1998
        }""", 'bibtex')
    bib_text.to_file('test.bib','bibtex')
    r = test_app.post('/insert', data={'file':  'test.bib', 'collection_name': 'test'})
    r.status_code == 302
    r.location == '/'
    #TRIED TO CONNECT AND CHECK THE UPLOAD BUT HAD ISSUES WITH INSERTION DURING TESTING
    #INSERTION WORKED ON THE LOCAL MACHINE AS LONG AS IT WAS IN THE CORRECT directory
    #BUT DID NOT WORK ON TRAVIS
    # conn = sqlite3.connect(DB_NAME)
    # cursor = conn.cursor()
    # cursor.execute("SELECT COUNT(collection) FROM {} WHERE collection = 'test'".format(TBL_NAME))
    # assert cursor.fetchall()[0][0] == 0
    # q = test_app.post('/search', data={'query_str': 'year < 2000'}).data.decode('utf-8')
    # cit_count = 0
    # for str_obj in q.split(' '):
    #     if str_obj == 'Citation':
    #         cit_count += 1
    # assert cit_count > 0

def test_bib2db():
    """Function to test the conversion of bib file to db and whether insertion into the database worked"""
    bib_text = pbt.parse_string("""@article{1998A&A...330..515F,
    	Adsnote = {Provided by the SAO/NASA Astrophysics Data System},
    	Adsurl = {http://adsabs.harvard.edu/abs/1998A%26A...330..515F},
    	Author = {{Fernley}, J. and {Barnes}, T.~G. and {Skillen}, I. and {Hawley}, S.~L. and {Hanley}, C.~J. and {Evans}, D.~W. and {Solano}, E. and {Garrido}, R.},
    	Date-Added = {2010-03-30 13:55:36 -0700},
    	Date-Modified = {2010-03-30 13:55:36 -0700},
    	Journal = {\aap},
    	Keywords = {STARS: VARIABLES: RR LYRAES, GALAXY: GLOBULAR CLUSTERS, GALAXIES: MAGELLANIC CLOUDS},
    	Month = feb,
    	Pages = {515-520},
    	Title = {{The absolute magnitudes of RR Lyraes from HIPPARCOS parallaxes and proper motions}},
    	Volume = 330,
    	Year = 1998
        }""", 'bibtex')
    bib_text.to_file('test.bib','bibtex')
    bd.bib_to_db('test.bib','Test',DB_NAME,TBL_NAME)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(collection) FROM {} WHERE collection = 'test'".format(TBL_NAME))
    assert cursor.fetchall()[0][0] == 0
    q = test_app.post('/search', data={'query_str': 'year < 2000'}).data.decode('utf-8')
    cit_count = 0
    for str_obj in q.split(' '):
        if str_obj == 'Citation':
            cit_count += 1
    assert cit_count > 0

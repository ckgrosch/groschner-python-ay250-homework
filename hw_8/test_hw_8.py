import sqlite3
from hw_8 import app, DB_NAME, clear_db, TBL_NAME

test_app = app.test_client()

def test_index():
    response = test_app.get('/')
    assert 'The current collections present are:' in response.data.decode('utf-8')

# def test_parse():
#     parse()....
#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()
#     assert cursor.execute("SELECT COUNT(*)") == 10

def test_search():
    clear_db()
    q = test_app.post('/search', data={'query_str': 'year > 2000'}).data.decode('utf-8')
    cit_count = 0
    for str_obj in q.split(' '):
        if str_obj == 'Citation':
            cit_count += 1
    assert cit_count == 0


def test_upload():
    clear_db()
    r = test_app.post('/insert', data={'file': open('hw_8_data/homework_8_refs.bib', 'rb'), 'collection_name': 'test'})
    r.status_code == 302
    r.location == '/'
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(collection) FROM {} WHERE collection = 'test'".format(TBL_NAME))
    assert cursor.fetchall()[0][0] == 46
    q = test_app.post('/search', data={'query_str': 'year > 2000'}).data.decode('utf-8')
    cit_count = 0
    for str_obj in q.split(' '):
        if str_obj == 'Citation':
            cit_count += 1
    assert cit_count > 0

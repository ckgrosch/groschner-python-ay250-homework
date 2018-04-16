from pybtex.database import parse_file
from pybtex.richtext import String
import sqlite3

def citation_key(file):
    """Takes in the collection, called file, after the pybtex function parse_file has already been called on it
    and returns the citation keys for that collection"""
    citation_keys = []
    for entry in file.entries:
        citation_keys.append(entry)
    return citation_keys

def author_list(file,citation_keys):
    """Takes in the collection, called file, after the pybtex function parse_file has already been called on it
    and returns the authors for that collection"""
    authors = []
    for entry in citation_keys:
        auth_list = file.entries[entry].persons.get('author',[])
        author_str = ""
        for auth in auth_list:
            author_str += str(auth).replace('{','').replace('}','')+" "
        if author_str != "":
            authors.append(author_str)
        else:
            authors.append("None")
    return authors

def volume_list(file,citation_keys):
    """Takes in the collection, called file, after the pybtex function parse_file has already been called on it
    and returns the volume numbers for that collection"""
    volumes = []
    for entry in citation_keys:
        vol = file.entries[entry].fields.get('Volume',[])
        if vol == []:
            vol = 'None'
        volumes.append(vol)
    return volumes

def title_list(file,citation_keys):
    """Takes in the collection, called file, after the pybtex function parse_file has already been called on it
    and returns the titles for that collection"""
    volumes = []
    for entry in citation_keys:
        vol = file.entries[entry].fields.get('Title',[])
        if vol == []:
            vol = 'None'
        else:
            vol = vol.replace('{','').replace('}','')
        volumes.append(vol)
    return volumes

def year_list(file,citation_keys):
    """Takes in the collection, called file, after the pybtex function parse_file has already been called on it
    and returns the years for that collection"""
    volumes = []
    for entry in citation_keys:
        vol = file.entries[entry].fields.get('Year',[])
        if vol == []:
            vol = 'None'
        volumes.append(vol)
    return volumes

def page_list(file,citation_keys):
    """Takes in the collection, called file, after the pybtex function parse_file has already been called on it
    and returns the pages for that collection"""
    volumes = []
    for entry in citation_keys:
        vol = file.entries[entry].fields.get('Pages',[])
        if vol == []:
            vol = 'None'
        volumes.append(vol)
    return volumes

def journal_list(file,citation_keys):
    """Takes in the collection, called file, after the pybtex function parse_file has already been called on it
    and returns the pages for that collection"""
    volumes = []
    for entry in citation_keys:
        vol = file.entries[entry].fields.get('Journal',[])
        if vol == []:
            vol = 'None'
        volumes.append(vol)
    return volumes

def bib_to_db(fname, collection_name, db_name,tbl_name):
    """Takes in a .bib file and returns a sql database with the citation tag, author list, volume, journal,pages, year
    and title"""
    file = parse_file(fname)
    citation_keys = citation_key(file)
    authors = author_list(file,citation_keys)
    volumes = volume_list(file,citation_keys)
    journals = journal_list(file,citation_keys)
    pages = page_list(file,citation_keys)
    titles = title_list(file,citation_keys)
    years = year_list(file,citation_keys)
    clctn_list = [collection_name]*len(citation_keys)
    rows = list(zip(citation_keys,authors,journals,volumes,pages,years,titles,clctn_list))
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executemany('insert into {} (cit_key,author_list,journal,volume,pages,year,title,collection) values (?,?,?,?,?,?,?,?)'.format(tbl_name), rows)
    conn.commit()
    conn.close()

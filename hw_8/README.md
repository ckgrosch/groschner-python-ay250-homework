# README for Bibtex Viewer

For the bibtex viewer I decided to make three separate html files for the
three separate pages of the website. These html files are kept in the templates
folder. I decided to include a function which will clear the database each time
the website is restarted so that test insertions wouldn't build up etc.
The python files to control the website are in hw_8.py. They reference a
module called bib2db which I wrote to manage all the transfer of the .bib file
to the database. In constructing the database I decided to create one table
which is referenced with the global variable TBL_NAME as opposed to creating
a separate table for each collection so that the querying would be simpler.
The database and a copy of the .bib file uploaded is kept in the uploads folder.
For testing I wrote a test for each of the pages and the bib2db module.
I tried to write the upload test such that I would search the database once the
upload happened to make sure it was done right but this led to MANY problems
with pytest being able to find the proper files etc. I tried to implement some
pytest fixtures to fix this but that failed. Sorry! The website worked for me
though and my most recent testing case gave 89% coverage so WOOO! To run the
website just call the run.sh file.

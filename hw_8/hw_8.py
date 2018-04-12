from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def butt_maker():
    return render_template('index.html')

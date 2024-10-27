from flask import render_template
from . import app

# movies routes
@app.route('/')
def index():
    return render_template('index.html')
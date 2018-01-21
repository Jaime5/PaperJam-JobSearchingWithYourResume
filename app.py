#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
from logging import Formatter, FileHandler
from os import path

from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for
from forms import *
import requests
# from flask.ext.sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename

from procs.metrics import ScoreDoc
from procs.textio import dump_data

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
BASE_PATH = path.dirname(path.abspath(__file__))
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/process_job_info', methods=["POST"])
def process_job_info():

    submitted = request.form
    job_link = submitted["JobLink"] + ".json"
    file = request.files['file']

    # ALLOWED_EXTENSIONS = set(['pdf'])

    response = json.loads(requests.get(job_link).text)
    soup = BeautifulSoup(response["description"], "html.parser")
    doc_path = path.join(BASE_PATH, "uploads", file.filename)
    file.save(doc_path)

    corpora_path = "job_desc.txt"

    with open(corpora_path, "w") as dump_file:
        dump_file.write(soup.get_text().encode("utf-8"))

    obj = ScoreDoc(doc_path, [corpora_path], BASE_PATH)
    obj.generate_tfidf()
    tfidf_data = obj.get_score()

    # MAKE SURE TO CREATE UPLOADS FOLDER

    # return render_template('results.html', results=tfidf_data)
    return json.dumps(tfidf_data)


# @app.route('/about')
# def about():
#     return render_template('how.html')


# @app.route('/login')
# def login():
#     form = LoginForm(request.form)
#     return render_template('forms/login.html', form=form)


# @app.route('/register')
# def register():
#     form = RegisterForm(request.form)
#     return render_template('forms/register.html', form=form)


# @app.route('/forgot')
# def forgot():
#     form = ForgotForm(request.form)
#     return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    # db_session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

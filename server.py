"""FitBit Project."""

from jinja2 import StrictUndefined
import os
from pprint import pformat

import requests
from flask import Flask, render_template, request, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "SECRET"

FITBIT_TOKEN = os.environ.get('TOKEN')
FITBIT_URL = 'https://api.fitbit.com/1/user/-/'
USER_ID = '6RJR2N'

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    email = request.forms.get('email')
    password = request.forms.get('password')
    
    return render_template('login.html')


@app.route('/fitbitdata', methods = ['GET'])
def export_fitbitdata():
    date1 = request.args.get('date1')
    date2 = request.args.get('date2') #Will get date for fitbit data request
    type_of_data = request.args.get('type') #Will get whether user wants hr, sleep, or activity data
    
    if date1 and type_of_data:
        payload = {'activity': type_of_data,
                    'date1': date1,
                    'date2': date2,}

        headers = {'Authorization': 'Bearer ' + TOKEN}
        response = requests.get(FITBIT_URL, params = payload, headers = headers)
        data = response.json()

        if response.ok:
            # data = data
            pass #figure out what to parse in data/response from FitBit API

        else:
            flash('Sorry, we could not access your FitBit data.')

            return render_template('fitbitdata.html', data = pformat(data), results = results)

    else:
        flash('Please provide all of the required information')
        return redirect('/fitbitdata')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
"""FitBit Project."""

from jinja2 import StrictUndefined
import os
from pprint import pformat
import json

import requests
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, MetricType, DailyEntry, PHQ, GAD, Sleep


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "SECRET"

FITBIT_TOKEN = os.environ.get('FITBIT_TOKEN')
USER_ID = os.environ.get('USER_ID')

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')

@app.route('/register', methods = ['GET'])
def register_form():
    """Register new users"""
    return render_template('register.html')

@app.route('/register', methods = ['POST'])
def process_registration():
    """Process new user registration"""
    email = request.form.get('email')
    password = request.form.get('password')

    new_user = User(email = email, password = password)
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.user_id

    flash('Welcome!')

    return render_template('/hipaa.html')

@app.route('/hipaa', methods = ['POST'])
def hipaa_form():
    if request.form.getlist('acknowledged-hipaa'):
        user = User.query.filter(User.user_id == session['user_id']).first()
        user.has_signed_hipaa = True
        db.session.commit()
        return redirect('/user_profile')
    else:
        flash('You must acknowledge HIPAA Privacy Practices.')
        return render_template('/hipaa.html')



@app.route('/login', methods = ['GET'])
def login_form():
    """Sends user to login form to fill out"""
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():
    """Sends user to user profile once correct email and password combo entered"""
    email = request.form.get('email')
    password = request.form.get('password')


    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Incorrect email. Please try again.")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password. Please try again.")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return render_template('user_profile.html', user = user)

@app.route('/logout', methods = ['POST'])
def logout():
    """Logs user out."""

    if (session.get('user_id', False)) != False:
        del session['user_id']
        flash("You have successfully logged out.")
        return redirect ('/')
    else:
        flash('You have already logged out.')

@app.route('/user_profile')
def user_profile():
    user_id = session.get('user_id')
    user = User.query.options(db.joinedload('dailymetrics')).get(user_id)
    return render_template("user_profile.html", user=user)

@app.route('/getfit')
def show_fitbit_form():
    return render_template('fitbitdata.html')

@app.route('/fitbitdata', methods = ['GET'])
def export_fitbitdata():
    date1 = request.args.get('date1') 
    date2 = request.args.get('date2') #Will get date for fitbit data request
    type_of_data = request.args.get('type')
    type_of_activity = request.args.get('activitytype')
    #Will get whether user wants hr, sleep, or activity data
    activity_type_dict = {"activities-heart": f"https://api.fitbit.com/1/user/-/activities/heart/date/{date1}/{date2}.json", 
                    "activities-steps": f"https://api.fitbit.com/1/user/-/activities/steps/date/{date1}/{date2}.json",
                    "activities-minutesSedentary": f"https://api.fitbit.com/1/user/-/activities/minutesSedentary/date/{date1}/{date2}.json",
                    "activities-minutesFairlyActive": f"https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/{date1}/{date2}.json",
                    "activities-minutesLightlyActive": f"https://api.fitbit.com/1/user/-/activities/minutesLightlyActive/date/{date1}/{date2}.json",
                    "activities-minutesVeryActive": f"https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/{date1}/{date2}.json"}

    if date1 and date2 and type_of_data:
        if session['user_id'] == 1:
            headers = {'Authorization': 'Bearer ' + FITBIT_TOKEN}
            if type_of_data != 'steps':
                response = requests.get(activity_type_dict[type_of_data], headers=headers)
            else:
                response = requests.get(activity_type_dict[type_of_activity], headers=headers)

            data = (response).json()
            if type_of_data != 'steps':
                rendered_data = data[type_of_data]
            else:
                rendered_data = data[type_of_activity]

        # START EDITING HERE!
            for i in rendered_data: 
                if type_of_data == 'sleep':
                    new_entry = DailyMetric.query.filter(DailyMetric.user_id == session['user_id'], DailyMetric.date == i['dateOfSleep']).first()
                    if new_entry:
                        new_entry.mins_slept = (i['minutesAsleep'])
                    else:
                        new_entry = DailyMetric(user_id = session['user_id'], mins_slept = (i['minutesAsleep']), date = i['dateOfSleep'])
                elif type_of_data == 'activities-heart':
                    new_entry = DailyMetric.query.filter(DailyMetric.user_id == session['user_id'], DailyMetric.date == i['dateTime']).first()
                    if new_entry:
                        new_entry.resting_hr = (i['value']['restingHeartRate'])
                    else:
                        new_entry = DailyMetric(user_id = session['user_id'], date = i['dateTime'], resting_hr = (i['value']['restingHeartRate']))
                else:
                    new_entry = DailyMetric.query.filter(DailyMetric.user_id == session['user_id'], DailyMetric.date == i['dateTime']).first()
                    if type_of_activity == 'activities-steps':
                        if new_entry:
                            new_entry.steps_walked = (i['value'])
                        else:
                            new_entry = DailyMetric(user_id = session['user_id'], date = i['dateTime'], steps_walked = i['value'])
                    elif type_of_activity ==  'activities-minutesSedentary':
                        if new_entry:
                            new_entry.mins_sedentary = (i['value'])
                        else:
                            new_entry = DailyMetric(user_id = session['user_id'], date = i['dateTime'], mins_sedentary = i['value'])
                    # elif type_of_activity == 'activities-minutesFairlyActive':
                    #     if new_entry:
                    #         new_entry.mins_exercise += (int(i['value']))
                    #     else:
                    #         new_entry = DailyMetric(user_id = session['user_id'], date = i['dateTime'], mins_exercise = i['value'] )
                    # elif type_of_activity == 'activities-minutesLightlyActive':
                    #     new_entry = DailyMetric(user_id = session['user_id'], date = i['dateTime'], mins_lightly_active = i['value'] )
                    # else:
                    #     new_entry = DailyMetric(user_id = session['user_id'], date = i['dateTime'], mins_very_active = i['value'] )
                db.session.add(new_entry)
            db.session.commit()

            return render_template('showfitbitdata.html', data = rendered_data, type_of_data = type_of_data, type_of_activity = type_of_activity)

        else:
            print('ERROR')
            flash('ERROR FOR RN')
            return redirect ('/getfit')
            
                #weather sunlight correlation to mental health
                #endpoint that returns dynamic image of chart to front end
                #function to retrieve daily data and range data, initial load, can be same function with optional parameter
                #Write code that populates the table; function can be run as a python script, not a Flask endpoint; ETL, add to db
                #transform to integer, load into database. Manually run it and load database. Could add to flask endpoint
                #start by creating python script to continuously grab the data, transform it, load it to db instaed of reloading browser
                #implement print messages; import requests, import psql/SQLA, and tables; script lives in same directory as models
                #Use sql to get aggregate data SQLA
            # else:
            #     flash('Sorry, we could not access your FitBit data.')

            #     return render_template('fitbitdata.html', data = pformat(data), results = results)

    else:
        flash('Please provide all of the required information')
        return redirect('/getfit')


def create_seed_file(rendered_data):
    print(rendered_data)

@app.route('/newtest', methods = ['GET'])
def navigate_to_tests():
    return render_template('newtest.html')

@app.route('/newtest', methods = ['POST'])
def insert_answers_into_db():
    return redirect ('/user_profile')

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
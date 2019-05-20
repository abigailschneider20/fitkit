"""FitBit Project."""

from jinja2 import StrictUndefined
import os
from pprint import pformat
import json
import random
from random_user import Anxiety, Depression, Insomnia, UnaffectedUser
import numpy
from datetime import date, timedelta, datetime
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
    activity_type_dict = {"sleep": f"https://api.fitbit.com/1.2/user/-/sleep/date/{date1}/{date2}.json",
                    "activities-heart": f"https://api.fitbit.com/1/user/-/activities/heart/date/{date1}/{date2}.json", 
                    "steps": {"activities-steps": f"https://api.fitbit.com/1/user/-/activities/steps/date/{date1}/{date2}.json",
                    "activities-minutesSedentary": f"https://api.fitbit.com/1/user/-/activities/minutesSedentary/date/{date1}/{date2}.json",
                    "activities-minutesFairlyActive": f"https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/{date1}/{date2}.json",
                    "activities-minutesLightlyActive": f"https://api.fitbit.com/1/user/-/activities/minutesLightlyActive/date/{date1}/{date2}.json",
                    "activities-minutesVeryActive": f"https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/{date1}/{date2}.json"}}

    activity_typeid_dict = {'activities-steps': 1, 'sleep': 2, 'activities-minutesFairlyActive': 3, 'activities-minutesLightlyActive': 3, 
                            'activities-minutesVeryActive': 3,'activities-minutesSedentary': 4, 'activities-heart': 5 }

    if date1 and date2 and type_of_data:
        if session['user_id'] == 1:
            headers = {'Authorization': 'Bearer ' + FITBIT_TOKEN}
            if type_of_data != 'steps':
                response = requests.get(activity_type_dict[type_of_data], headers=headers)
            else:
                response = requests.get(activity_type_dict["steps"][type_of_activity], headers=headers)


            data = (response).json()
            print(data)
            print(type_of_data)

            show_fitbit_data_lst = []

            if type_of_data != 'steps':
                rendered_data = data[type_of_data]
            else:
                rendered_data = data[type_of_activity]
        
           
            for i in rendered_data:
                if type_of_data == 'sleep':
                    existing_entry = DailyEntry.query.filter(DailyEntry.date == i['dateOfSleep'], DailyEntry.type_id == (activity_typeid_dict[type_of_data])).first()
                    if existing_entry:
                        existing_entry = existing_entry
                        show_fitbit_data_lst.append(existing_entry)
                    else: 
                        new_entry = DailyEntry(user_id = session['user_id'], type_id = activity_typeid_dict[type_of_data], val = i['minutesAsleep'], date = i['dateOfSleep'])  
                        db.session.add(new_entry)
                elif type_of_data == 'activities-heart':
                    existing_entry = DailyEntry.query.filter(DailyEntry.date == i['dateTime'], DailyEntry.type_id == (activity_typeid_dict[type_of_data])).first()
                    if existing_entry:
                        existing_entry = existing_entry
                        show_fitbit_data_lst.append(existing_entry)
                    else:
                        new_entry = DailyEntry(user_id = session['user_id'], type_id = activity_typeid_dict[type_of_data], val = i['value']['restingHeartRate'], date = i['dateTime'])
                        db.session.add(new_entry)
                else:
                    if type_of_activity == 'activities-minutesSedentary':
                        existing_entry = DailyEntry.query.filter(DailyEntry.date == i['dateTime'], DailyEntry.type_id == (activity_typeid_dict[type_of_data])).first()
                        if existing_entry:
                            existing_entry = existing_entry
                            show_fitbit_data_lst.append(existing_entry)
                        else:
                            new_entry = DailyEntry(user_id = session['user_id'], type_id = activity_typeid_dict[type_of_activity], val = i['value'], date = i['dateTime'])
                            db.session.add(new_entry)
                    else:
                        new_entry = DailyEntry.query.filter(DailyEntry.date == (i['dateTime']), DailyEntry.type_id == (activity_typeid_dict[type_of_activity])).first()
                        if new_entry:
                            new_entry.val += (int(i['value']))
                        else:
                            new_entry = DailyEntry(user_id = session['user_id'], type_id = activity_typeid_dict[type_of_activity], val = i['value'], date = i['dateTime'])
                        db.session.add(new_entry)
                        show_fitbit_data_lst.append(new_entry)
                print(show_fitbit_data_lst)
                # if existing_entry:
                #     show_fitbit_data_lst.append(existing_entry)
                # else:
                #     show_fitbit_data_lst.append(new_entry)

            db.session.commit()

            return render_template('showfitbitdata.html', show_fitbit_data_lst=show_fitbit_data_lst)
        else:
            date1 = datetime.strptime(date1,'%Y-%m-%d' )
            date2 = datetime.strptime(date2, '%Y-%m-%d')
            day = timedelta(days=1)
            show_fitbit_data_lst = []
            classes = (Anxiety, Depression, Insomnia, UnaffectedUser)
            probs = (0.18, 0.08, 0.25, 0.49)
            new_user_list = []
            new_user_class= numpy.random.choice((classes), p=probs)
            for i in range((date2-date1).days + 1):
                new_user_data = new_user_class(session['user_id'])
                if type_of_data == "activities-heart":
                    new_user = DailyEntry(user_id = new_user_data.user_id, type_id = 5, val = new_user_data.resting_hr, date = (date1 + timedelta(days=i)))
                    db.session.add(new_user)
                    show_fitbit_data_lst.append(new_user)
                elif type_of_data == "sleep":
                    new_user = DailyEntry(user_id = new_user_data.user_id, type_id = 2, val = new_user_data.mins_sleep, date = (date1+timedelta(days=i)))
                    db.session.add(new_user)
                    show_fitbit_data_lst.append(new_user)
                elif type_of_data == "steps":
                    if type_of_activity == "minutesSedentary":
                        new_user = DailyEntry(user_id = new_user_data.user_id, type_id = 4, val = new_user_data.mins_sedentary, date =(date1+timedelta(days=1)))
                        db.session.add(new_user)
                        show_fitbit_data_lst.append(new_user)
                    elif type_of_activity == "activities-steps":
                        new_user = DailyEntry(user_id = new_user_data.user_id, type_id = 1, val = new_user_data.steps, date = (date1+timedelta(days=1)))
                        db.session.add(new_user)
                        show_fitbit_data_lst.append(new_user)
                    else:
                        new_user = DailyEntry(user_id = new_user_data.user_id, type_id = 3, val = new_user_data.mins_exercise, date = (date1+timedelta(days=1)))
                        db.session.add(new_user)
                        show_fitbit_data_lst.append(new_user)

            db.session.add(new_user)
            db.session.commit()
            return render_template('showfitbitdata.html', show_fitbit_data_lst=show_fitbit_data_lst)
            
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

# @app.route('/showfitbitdata')
# def show_fitbit_data():
    
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
"""FitBit Project."""

from jinja2 import StrictUndefined
import os
from pprint import pformat
import json
import random
from gen_user_data_assess_test import Anxiety, Depression, Insomnia, UnaffectedUser, assess_phq, assess_gad, assess_sleep
import numpy
from datetime import date, timedelta, datetime
import requests
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, DailyEntry, PHQ, GAD, Sleep


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
    f_name = request.form.get('f_name')
    l_name = request.form.get('l_name')
    age = request.form.get('age')
    sex = request.form.get('sex')

    new_user = User(email = email, password = password, f_name = f_name,
        l_name = l_name, age = age, sex = sex)
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.user_id


    flash('Welcome!')

    return render_template('/hipaa.html')

@app.route('/hipaa', methods = ['POST'])
def hipaa_form():
    """Redirects user to mandatory HIPAA Acknowledgement form"""
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
    """Shows user profile for signed in user"""
    user_id = session.get('user_id')
    user = User.query.options(db.joinedload('dailymetrics')).get(user_id)
    return render_template("user_profile.html", user=user)

@app.route('/getfit')
def show_fitbit_form():
    """Redirects user to form to access more FitBit data.
    For user with id 1, can directly access FitBit API and add new data to db.
    For other users, new data will be randomly assigned based on incidences of 
    various mental health conditions and the data will be instantiated for each
    of the days specified in the desired target date range. """
    return render_template('fitbitdata.html')

def download_fitbitdata(date1, date2):
    #downloads all types of fitbit data for date range

    activity_type_dict = {"sleep": (f"https://api.fitbit.com/1.2/user/-/sleep/date/{date1}/{date2}.json"),
                    "activities-heart": (f"https://api.fitbit.com/1/user/-/activities/heart/date/{date1}/{date2}.json"), 
                    "activities-steps": (f"https://api.fitbit.com/1/user/-/activities/steps/date/{date1}/{date2}.json"),
                    "activities-minutesSedentary": (f"https://api.fitbit.com/1/user/-/activities/minutesSedentary/date/{date1}/{date2}.json"),
                    "activities-minutesFairlyActive": (f"https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/{date1}/{date2}.json"),
                    "activities-minutesLightlyActive": (f"https://api.fitbit.com/1/user/-/activities/minutesLightlyActive/date/{date1}/{date2}.json"),
                    "activities-minutesVeryActive": (f"https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/{date1}/{date2}.json")}

    headers = {'Authorization': 'Bearer ' + FITBIT_TOKEN}

    raw_data = {}

    for k in activity_type_dict:
        response = requests.get(activity_type_dict[k], headers = headers)
        data = response.json()
        rendered_data = data[k]
        raw_data[k] = rendered_data
    return raw_data

def create_newuser_data(date1, date2):
    #creates new user data to mock import of FitBit data
    show_fitbit_data_lst = []
    classes = (Anxiety, Depression, Insomnia, UnaffectedUser)
    probs = (0.18, 0.08, 0.25, 0.49)
    existing_entry = DailyEntry.query.filter(DailyEntry.date == date1).first()
    if existing_entry == None:
        new_user_class= numpy.random.choice((classes), p=probs)
        print(new_user_class)
        curr_user = User.query.filter(User.user_id == session['user_id']).first()
        curr_user.class_type = new_user_class.class_type
        new_user = ""
        for i in range((date2-date1).days + 1):
            new_user_data = new_user_class(session['user_id'])
            new_user = DailyEntry(user_id = new_user_data.user_id, date = (date1 + timedelta(days=i)), steps = new_user_data.steps, sleep = new_user_data.mins_sleep, mins_sedentary = new_user_data.mins_sedentary, mins_exercise = new_user_data.mins_exercise, resting_hr = new_user_data.resting_hr)
            db.session.add(new_user)
            show_fitbit_data_lst.append(new_user)
            db.session.commit()
    else:
        show_fitbit_data_lst.append(existing_entry)



    return show_fitbit_data_lst

def parse_rawfitbitdata(raw_data, i):
    #parse raw fitbit data

    new_entry = DailyEntry(user_id = session['user_id'], date = raw_data['sleep'][i]['dateOfSleep'], sleep = raw_data['sleep'][i]['minutesAsleep'])
    new_entry.mins_exercise = 0
    new_entry.resting_hr = raw_data['activities-heart'][i]['value']['restingHeartRate']
    new_entry.steps = raw_data['activities-steps'][i]['value']
    new_entry.mins_sedentary = raw_data['activities-minutesSedentary'][i]['value']
    new_entry.mins_exercise += int(raw_data['activities-minutesLightlyActive'][i]['value'])
    new_entry.mins_exercise += int(raw_data['activities-minutesFairlyActive'][i]['value'])
    new_entry.mins_exercise += int(raw_data['activities-minutesVeryActive'][i]['value'])

    db.session.add(new_entry)

    db.session.commit()

    return new_entry

def check_existing_entries(date1, date2):
    show_fitbit_data_lst = []
    raw_data = download_fitbitdata(date1, date2)
    for i in range(0, (date2-date1).days+1) :
        existing_entry = DailyEntry.query.filter(DailyEntry.date == (date2 - timedelta(days = i))).first()
        if existing_entry == None:
            new_entry = parse_rawfitbitdata(raw_data, i)
            show_fitbit_data_lst.append(new_entry)
        else:
            show_fitbit_data_lst.append(existing_entry)

    return show_fitbit_data_lst


@app.route('/fitbitdata', methods = ['GET'])
def fitbitdata():
    date1 = request.args.get('date1') 
    date2 = request.args.get('date2')
    date1 = datetime.strptime(date1, '%Y-%m-%d').date()
    date2 = datetime.strptime(date2, '%Y-%m-%d').date()

    show_fitbit_data_lst = []
    if date1 and date2:
        if session['user_id'] == 1:
            show_fitbit_data_lst = check_existing_entries(date1, date2)
        else:
            show_fitbit_data_lst = create_newuser_data(date1, date2)

        return render_template('showfitbitdata.html', show_fitbit_data_lst = show_fitbit_data_lst)

    else:
        flash('Please provide all of the required information')
        return redirect('/getfit')

@app.route('/ehrtemplate', methods = ['GET'])
def show_ehr_template():
    return render_template('ehrtemplate.html')


@app.route('/chartdata.json')
def chart_data():
    """Return biometric data and personal test
     scores to be displayed on a chart"""
     # user.phq.score = data for line graph but only for specific user and time specified. 
     # Add date1 and date2 values to form. Use dates to query for data. FitBit data: be
     # able to see steps, sedentary mins, exercise, sleep; user.dailymetrics where type_id is 
     # for specific value and specific time.
    user = User.query.filter(User.user_id == session['user_id']).first()
    print(user)
    chart_type = request.args.get('chart_type')
    print(chart_type)
    data_dict = {}
    if chart_type == 'PHQ9':
        for i in user.phq:
            data_dict[str(i.date)] = (int(i.score))

    elif chart_type == 'GAD7':
        for j in user.gad:
            data_dict[str(j.date)] = (int(j.score))


    elif chart_type == 'Insomnia Index':
        for k in user.sleep:
            data_dict[str(k.date)] = (int(k.score))

    elif chart_type == 'Resting Heart Rate':
        for m in user.dailymetrics:
            data_dict[str(m.date)] = (m.resting_hr)
    elif chart_type == 'Steps':
        for n in user.dailymetrics:
            data_dict[str(n.date)] = (n.steps)
    elif chart_type == 'Mins Slept':
        for r in user.dailymetrics:
            data_dict[str(r.date)] = (r.sleep)
    elif chart_type == 'Mins Exercise':
        for x in user.dailymetrics:
            data_dict[str(x.date)] = (x.mins_exercise)
    else:
        for y in user.dailymetrics:
            data_dict[str(y.date)] = (y.mins_sedentary)
    data_lst = sorted(data_dict.items())
    date_labels = [x[0] for x in data_lst]
    selected_data = [x[1] for x in data_lst]
    data_dict = {
        "labels": date_labels,

        "datasets": [
                {
                    "label": chart_type,
                    "fill": True,
                    "lineTension": 0.5,
                    "backgroundColor": "rgba(151,187,205,0.2)",
                    "borderColor": "rgba(151,187,205,1)",
                    "borderCapStyle": 'butt',
                    "borderDash": [],
                    "borderDashOffset": 0.0,
                    "borderJoinStyle": 'miter',
                    "pointBorderColor": "rgba(151,187,205,1)",
                    "pointBackgroundColor": "#fff",
                    "pointBorderWidth": 1,
                    "pointHoverRadius": 5,
                    "pointHoverBackgroundColor": "#fff",
                    "pointHoverBorderColor": "rgba(151,187,205,1)",
                    "pointHoverBorderWidth": 2,
                    "pointHitRadius": 10,
                    "data": selected_data,
                    "spanGaps": False}]
                    }
   
    return jsonify(data_dict)

@app.route('/chart', methods = ['GET'])
def show_chart():
    return render_template('chart.html')


@app.route('/newtest', methods = ['GET'])
def navigate_to_tests():
    return render_template('newtest.html')

@app.route('/newtest', methods = ['POST'])
def insert_answers_into_db():
    test_type = request.form.get('testtype')

    if test_type == 'phq':
        q1_answer = int(request.form.get('q1phq'))
        q2_answer = int(request.form.get('q2phq'))
        q3_answer = int(request.form.get('q3phq'))
        q4_answer = int(request.form.get('q4phq'))
        q5_answer = int(request.form.get('q5phq'))
        q6_answer = int(request.form.get('q6phq'))
        q7_answer = int(request.form.get('q7phq'))
        q8_answer = int(request.form.get('q8phq'))
        q9_answer = int(request.form.get('q9phq'))
        score = (q1_answer+q2_answer+q3_answer+q4_answer+q5_answer+q6_answer+q7_answer+q8_answer+q9_answer)
        print(score)
        dep_severity = assess_phq(score)
        print(dep_severity)
        new_test = PHQ(user_id = session['user_id'], date = date.today().strftime('%Y-%m-%d'), 
            q1_answer = q1_answer,
            q2_answer = q2_answer,
            q3_answer = q3_answer,
            q4_answer = q4_answer,
            q5_answer = q5_answer,
            q6_answer = q6_answer,
            q7_answer = q7_answer,
            q8_answer = q8_answer,
            q9_answer = q9_answer,
            score = score, 
            dep_severity = dep_severity)
        db.session.add(new_test)
        db.session.commit()

        flash('You successfully submitted your PHQ9 results.')
        return redirect ('/user_profile')
    elif test_type == 'gad':
        q1_answer = int(request.form.get('q1gad'))
        q2_answer = int(request.form.get('q2gad'))
        q3_answer = int(request.form.get('q3gad'))
        q4_answer = int(request.form.get('q4gad'))
        q5_answer = int(request.form.get('q5gad'))
        q6_answer = int(request.form.get('q6gad'))
        q7_answer = int(request.form.get('q7gad'))
        score = (q1_answer+q2_answer+q3_answer+q4_answer+q5_answer+q6_answer+q7_answer)
        anx_severity = assess_gad(score)
        new_test = GAD(user_id = session['user_id'], date = date.today().strftime('%Y-%m-%d'), 
            q1_answer = q1_answer,
            q2_answer = q2_answer,
            q3_answer = q3_answer,
            q4_answer = q4_answer,
            q5_answer = q5_answer,
            q6_answer = q6_answer,
            q7_answer = q7_answer,
            score = score, 
            anx_severity = anx_severity)
        db.session.add(new_test)
        db.session.commit()

        flash('You successfully submitted your GAD7 results.')
        return redirect ('/user_profile')
    elif test_type == 'sleep':
        q1_answer = int(request.form.get('q1'))
        q2_answer = int(request.form.get('q2'))
        q3_answer = int(request.form.get('q3'))
        q4_answer = int(request.form.get('q4'))
        q5_answer = int(request.form.get('q5'))
        q6_answer = int(request.form.get('q6'))
        q7_answer = int(request.form.get('q7'))
        score = (q1_answer+q2_answer+q3_answer+q4_answer+q5_answer+q6_answer+q7_answer)
        insomnia_severity = assess_sleep(score)
        new_test = Sleep(user_id = session['user_id'], date = date.today().strftime('%Y-%m-%d'), 
            q1_answer = q1_answer,
            q2_answer = q2_answer,
            q3_answer = q3_answer,
            q4_answer = q4_answer,
            q5_answer = q5_answer,
            q6_answer = q6_answer,
            q7_answer = q7_answer,
            score = score, 
            insomnia_severity = insomnia_severity)
        db.session.add(new_test)
        db.session.commit()

        flash('You successfully submitted your Sleep Questionnaire results.')
        return redirect ('/user_profile')
    else: 
        flash('Please select a type of test to take.')
        return redirect('/newtest')

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
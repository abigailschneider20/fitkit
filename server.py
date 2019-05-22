"""FitBit Project."""

from jinja2 import StrictUndefined
import os
from pprint import pformat
import json
import random
from random_user import Anxiety, Depression, Insomnia, UnaffectedUser, assess_phq, assess_gad, assess_sleep
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
                        show_fitbit_data_lst.append(new_entry)
                elif type_of_data == 'activities-heart':
                    existing_entry = DailyEntry.query.filter(DailyEntry.date == i['dateTime'], DailyEntry.type_id == (activity_typeid_dict[type_of_data])).first()
                    if existing_entry:
                        existing_entry = existing_entry
                        show_fitbit_data_lst.append(existing_entry)
                    else:
                        new_entry = DailyEntry(user_id = session['user_id'], type_id = activity_typeid_dict[type_of_data], val = i['value']['restingHeartRate'], date = i['dateTime'])
                        db.session.add(new_entry)
                        show_fitbit_data_lst.append(new_entry)
                else:
                    if type_of_activity == 'activities-minutesSedentary':
                        existing_entry = DailyEntry.query.filter(DailyEntry.date == i['dateTime'], DailyEntry.type_id == (activity_typeid_dict[type_of_data])).first()
                        if existing_entry:
                            existing_entry = existing_entry
                            show_fitbit_data_lst.append(existing_entry)
                        else:
                            new_entry = DailyEntry(user_id = session['user_id'], type_id = activity_typeid_dict[type_of_activity], val = i['value'], date = i['dateTime'])
                            db.session.add(new_entry)
                            show_fitbit_data_lst.append(new_entry)
                    else:
                        new_entry = DailyEntry.query.filter(DailyEntry.date == (i['dateTime']), DailyEntry.type_id == (activity_typeid_dict[type_of_activity])).first()
                        if new_entry:
                            new_entry.val += (int(i['value']))
                        else:
                            new_entry = DailyEntry(user_id = session['user_id'], type_id = activity_typeid_dict[type_of_activity], val = i['value'], date = i['dateTime'])
                        db.session.add(new_entry)
                        show_fitbit_data_lst.append(new_entry)
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
    data_dict = {
    "labels": ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    "datasets": [
            {
                "label": "FitBit Data",
                "fill": True,
                "lineTension": 0.5,
                "backgroundColor": "rgba(220,220,220,0.2)",
                "borderColor": "rgba(220,220,220,1)",
                "borderCapStyle": 'butt',
                "borderDash": [],
                "borderDashOffset": 0.0,
                "borderJoinStyle": 'miter',
                "pointBorderColor": "rgba(220,220,220,1)",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(220,220,220,1)",
                "pointHoverBorderWidth": 2,
                "pointRadius": 3,
                "pointHitRadius": 10,
                "data": fitbitdata,
                "spanGaps": False},
            {
                "label": "PHQ scores",
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
                "data": data,
                "spanGaps": False}
                ]
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
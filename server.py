"""FitBit Project."""

from jinja2 import StrictUndefined
import os
from pprint import pformat
import json
import random
from gen_user_data_assess_test import Anxiety, Depression, Insomnia, UnaffectedUser, assess_phq, assess_gad, assess_sleep, add_stats
import numpy
from datetime import date, timedelta, datetime
import requests
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
import pandas

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

def assess_new_testscores():
    curr_user = User.query.filter(User.user_id == session['user_id']).first()
    class_type = curr_user.class_type
    if class_type == 'Depression':
        incomplete_PHQ = PHQ.query.filter(PHQ.user_id == session['user_id'], PHQ.score == None).all()
        for entry in incomplete_PHQ:
            entry.score =(entry.q1_answer + entry.q2_answer + entry.q3_answer + entry.q4_answer + entry.q5_answer + entry.q6_answer + entry.q7_answer + entry.q8_answer + entry.q9_answer)
            entry.dep_severity = assess_phq(entry.score)
    elif class_type == 'Anxiety':
        incomplete_GAD = GAD.query.filter(GAD.user_id == session['user_id'], GAD.score == None).all()
        for entry in incomplete_GAD:
            entry.score =(entry.q1_answer + entry.q2_answer + entry.q3_answer + entry.q4_answer + entry.q5_answer + entry.q6_answer + entry.q7_answer)
            entry.anx_severity = assess_gad(entry.score)
    elif class_type == 'Insomnia':
        incomplete_ISI = Sleep.query.filter(Sleep.user_id == session['user_id'], Sleep.score == None).all()
        for entry in incomplete_ISI:
            entry.score =(entry.q1_answer + entry.q2_answer + entry.q3_answer + entry.q4_answer + entry.q5_answer + entry.q6_answer + entry.q7_answer)
            entry.insomnia_severity = assess_sleep(entry.score)
    elif class_type == 'Unaffected':
        incomplete_PHQ = PHQ.query.filter(PHQ.user_id == session['user_id'], PHQ.score == None).all()
        for entry in incomplete_PHQ:
            entry.score =(entry.q1_answer + entry.q2_answer + entry.q3_answer + entry.q4_answer + entry.q5_answer + entry.q6_answer + entry.q7_answer + entry.q8_answer + entry.q9_answer)
            entry.dep_severity = assess_phq(entry.score)
        incomplete_GAD = GAD.query.filter(GAD.user_id == session['user_id'], GAD.score == None).all()
        for entry in incomplete_GAD:
            entry.score =(entry.q1_answer + entry.q2_answer + entry.q3_answer + entry.q4_answer + entry.q5_answer + entry.q6_answer + entry.q7_answer)
            entry.anx_severity = assess_gad(entry.score)
        incomplete_ISI = Sleep.query.filter(Sleep.user_id == session['user_id'], Sleep.score == None).all()
        for entry in incomplete_ISI:
            entry.score =(entry.q1_answer + entry.q2_answer + entry.q3_answer + entry.q4_answer + entry.q5_answer + entry.q6_answer + entry.q7_answer)
            entry.insomnia_severity = assess_sleep(entry.score)
    else:
        return 'Error'
    db.session.commit()

def create_new_testscores(curr_user, new_user_data, date):
    #creates new test scores for specified date range based off of user's class type (Depression, Anxiety, Insomnia, UnaffectedUser)
    if curr_user.class_type == 'Depression':
        new_PHQ = PHQ(user_id = session['user_id'], date = date, q1_answer = new_user_data.phq1, q2_answer = new_user_data.phq2, q3_answer = new_user_data.phq3, q4_answer = new_user_data.phq4, 
                    q5_answer = new_user_data.phq5, q6_answer = new_user_data.phq6, q7_answer = new_user_data.phq7, q8_answer = new_user_data.phq8, q9_answer=new_user_data.phq9)
        db.session.add(new_PHQ)
        db.session.commit()
        return new_PHQ
    elif curr_user.class_type == 'Anxiety':
        new_GAD = GAD(user_id = session['user_id'], date = date, q1_answer = new_user_data.gad1, q2_answer = new_user_data.gad2, q3_answer = new_user_data.gad3, q4_answer = new_user_data.gad4, 
                    q5_answer = new_user_data.gad5, q6_answer = new_user_data.gad6, q7_answer = new_user_data.gad7)
        db.session.add(new_GAD)
        db.session.commit()
        return new_GAD
    elif curr_user.class_type == 'Insomnia':
        new_ISI = Sleep(user_id = session['user_id'], date = date, q1_answer = new_user_data.isi1, q2_answer = new_user_data.isi2, q3_answer = new_user_data.isi3, q4_answer = new_user_data.isi4, 
                    q5_answer = new_user_data.isi5, q6_answer = new_user_data.isi6, q7_answer = new_user_data.isi7)
        db.session.add(new_ISI)
        db.session.commit()
        return new_ISI
    else:
        new_PHQ = PHQ(user_id = session['user_id'], date = date, q1_answer = new_user_data.phq1, q2_answer = new_user_data.phq2, q3_answer = new_user_data.phq3, q4_answer = new_user_data.phq4, 
                    q5_answer = new_user_data.phq5, q6_answer = new_user_data.phq6, q7_answer = new_user_data.phq7, q8_answer = new_user_data.phq8, q9_answer=new_user_data.phq9)
        new_GAD = GAD(user_id = session['user_id'], date = date, q1_answer = new_user_data.gad1, q2_answer = new_user_data.gad2, q3_answer = new_user_data.gad3, q4_answer = new_user_data.gad4, 
                    q5_answer = new_user_data.gad5, q6_answer = new_user_data.gad6, q7_answer = new_user_data.gad7)
        new_ISI = Sleep(user_id = session['user_id'], date = date, q1_answer = new_user_data.isi1, q2_answer = new_user_data.isi2, q3_answer = new_user_data.isi3, q4_answer = new_user_data.isi4, 
                    q5_answer = new_user_data.isi5, q6_answer = new_user_data.isi6, q7_answer = new_user_data.isi7)
        db.session.add(new_PHQ)
        db.session.add(new_GAD)
        db.session.add(new_ISI)
        db.session.commit()
        return new_PHQ, new_GAD, new_ISI

def create_newuser_data(date1, date2):
    #creates new user data to mock import of FitBit data
    show_fitbit_data_lst = []
    classes = (Anxiety, Depression, Insomnia, UnaffectedUser)
    probs = (0.18, 0.08, 0.25, 0.49)
    existing_entry = DailyEntry.query.filter(DailyEntry.user_id == session['user_id'], DailyEntry.date == date1).first()
    if existing_entry == None:
        new_user_class= numpy.random.choice((classes), p=probs)
        curr_user = User.query.filter(User.user_id == session['user_id']).first()
        curr_user.class_type = new_user_class.class_type
        print(curr_user.class_type)
        new_user = ""
        for i in range((date2-date1).days + 1):
            date = (date1+timedelta(days=i))
            new_user_data = new_user_class(session['user_id'])
            new_user = DailyEntry(user_id = new_user_data.user_id, date = date, steps = new_user_data.steps, sleep = new_user_data.mins_sleep, mins_sedentary = new_user_data.mins_sedentary, mins_exercise = new_user_data.mins_exercise, resting_hr = new_user_data.resting_hr)
            show_fitbit_data_lst.append(new_user)
            new_scores = create_new_testscores(curr_user, new_user_data, date)
            db.session.add(new_user)
    
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
            prediction=predict(date1, date2)
        else:
            show_fitbit_data_lst = create_newuser_data(date1, date2)
            assess_new_testscores()
            prediction=predict(date1, date2)
        return render_template('showfitbitdata.html', show_fitbit_data_lst = show_fitbit_data_lst, date1 = date1, date2=date2, prediction = prediction)

    else:
        flash('Please provide all of the required information')
        return redirect('/getfit')

@app.route('/ehrtemplate', methods = ['GET'])
def show_ehr_template():
    return render_template('ehrtemplate.html')

def predict(date1, date2):
    #uses logistic regression models to predict mental health test scores based on biometric data
    recent1 = DailyEntry.query.filter(DailyEntry.user_id == session['user_id'], DailyEntry.date>=date1).all()
    recent2 = DailyEntry.query.filter(DailyEntry.user_id ==session['user_id'], DailyEntry.date<=date2).all()
    recent_entries = set(recent1+recent2)
    steps, sleep, mins_exercise, mins_sedentary, resting_hr = [], [], [], [], []
    for entry in recent_entries:
        steps.append(entry.steps)
        sleep.append(entry.sleep)
        mins_exercise.append(entry.mins_exercise)
        mins_sedentary.append(entry.mins_sedentary)
        resting_hr.append(entry.resting_hr)

    steps = numpy.mean(steps)
    sleep= numpy.mean(sleep)
    mins_exercise = numpy.mean(mins_exercise)
    mins_sedentary = numpy.mean(mins_sedentary)
    resting_hr = numpy.mean(resting_hr)
    print(steps, sleep, mins_sedentary, mins_exercise, resting_hr)
    recs = []
    if steps < 10000:
        recs.append(f'Try walking {int(10000-steps)} more steps daily')
    if sleep < 420:
        recs.append(f'Try going to sleep {int(420-sleep)} minutes earlier each night')
    if mins_exercise < 40:
        recs.append(f'Try adding in {int(40-mins_exercise)} more minutes of exercise daily')
    if resting_hr > 100:
        recs.append(f'Consider speaking to your doctor about your elevated resting heart rate and ways to improve your overall cardiovascuclar health')
    user_id = session['user_id']
    data = [user_id, user_id, steps, sleep, mins_sedentary, mins_exercise, resting_hr]
    phq_prediction = phq_model.predict([data])
    phq_output = phq_prediction[0]
    print(phq_output)
    gad_prediction = gad_model.predict([data])
    gad_output = gad_prediction[0]
    print(gad_output)
    isi_prediction= isi_model.predict([data])
    isi_output = isi_prediction[0]
    print(isi_output)

    prediction = {'phq': phq_output,
                'gad': gad_output,
                'isi': isi_output, 
                'recs': recs}
    return prediction


@app.route('/chartdata')
def chart_data():
    """Return biometric data and personal test
     scores to be displayed on a chart"""
    
    user = User.query.filter(User.user_id == session['user_id']).first()
    firstchart_type = request.args.get('firstchart_type')
    secchart_type = request.args.get('secchart_type')
    formatType = request.args.get('format')

    data_dict = {}
    first_dict = {}
    second_dict = {}

    if firstchart_type == 'PHQ9':
        for i in user.phq:
            first_dict[str(i.date)] = (int(i.score))
    elif firstchart_type == 'GAD7':
        for i in user.gad:
            first_dict[str(i.date)] = (int(i.score))
    else:
        for i in user.sleep:
            first_dict[str(i.date)] = (int(i.score))

    if secchart_type =='Resting Heart Rate':
        for j in user.dailymetrics:
            second_dict[str(j.date)] = (int(j.resting_hr))
    elif secchart_type == 'Steps':
        for j in user.dailymetrics:
            second_dict[str(j.date)] = (int(j.steps))
    elif secchart_type == 'Mins Slept':
        for j in user.dailymetrics:
            second_dict[str(j.date)] = (int(j.sleep))
    elif secchart_type == 'Mins Exercise':
        for j in user.dailymetrics:
            second_dict[str(j.date)] = (int(j.mins_exercise))
    else:
        for j in user.dailymetrics:
            second_dict[str(j.date)] = (int(j.mins_sedentary))
  
    data_dict['data1'] = first_dict
    data_dict['data2'] = second_dict
    secdata_lst = sorted(data_dict['data2'].items())
    date_labels = [x[0] for x in secdata_lst] #second dataset will always have more dates
    for date in date_labels:
        value = data_dict['data1'].get(date, None)
        data_dict['data1'][date] = value
    firstdata_lst = sorted(data_dict['data1'].items())
    first_data = [x[1] for x in firstdata_lst]
    sec_data = [x[1] for x in secdata_lst]
    stats1 = [x for x in first_data if x != None]
    stats2 = [x for x in sec_data if x != None]
    stats = add_stats(stats1, stats2)

    if formatType == 'json':
        return jsonify({
            "labels": date_labels,
            "datasets": [
                {
                    "label": firstchart_type,
                    "data": first_data,
                    "colorOpts": {}
                },
                {
                    "label": secchart_type,
                    "data": sec_data,
                    "colorOpts": {                    
              "backgroundColor": "rgb(232, 129, 109)",
              "borderColor": "rgb(109, 232, 129)",
              "pointHoverBackgroundColor": "rgb(150, 75, 220)",
              "pointHoverBorderColor": "rgb(75, 218, 220)",
            }
                }
            ],
            "stats":stats
            })


    return render_template('chartdata.html', labels = date_labels, data1 = first_data, data2 = sec_data, stats = stats)



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
        dep_severity = assess_phq(score)
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
        print(new_test.dep_severity)
        flash('You successfully submitted your PHQ9 results. ')
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
    phq_model = pickle.load(open('phq.pkl', 'rb'))
    gad_model = pickle.load(open('gad.pkl', 'rb'))
    isi_model = pickle.load(open('isi.pkl', 'rb'))
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
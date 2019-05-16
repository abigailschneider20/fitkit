"""FitBit Project."""

from jinja2 import StrictUndefined
import os
from pprint import pformat


import requests
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, DailyMetric, PHQ, GAD, Sleep


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
    print (new_user)
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
    return redirect('/user_profile')

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

    print(type_of_data) #Will get whether user wants hr, sleep, or activity data
    
    if session['user_id'] == 1:
        if date1 and date2 and type_of_data:
            headers = {'Authorization': 'Bearer ' + FITBIT_TOKEN}
            if type_of_data == 'heart':
                url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date1}/{date2}.json"
                response = requests.get(url, headers = headers)
            elif type_of_data == 'activities':
                url1 = f"https://api.fitbit.com/1/user/-/activities/steps/date/{date1}/{date2}.json"
                url2= f"https://api.fitbit.com/1/user/-/activities/minutesSedentary/date/{date1}/{date2}.json"
                url3= f"https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/{date1}/{date2}.json"
                url4= f"https://api.fitbit.com/1/user/-/activities/minutesLightlyActive/date/{date1}/{date2}.json"
                url5= f"https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/{date1}/{date2}.json"
                response = requests.get(url1, headers = headers)
                response = response.append(requests.get(url2, headers = headers))
                response = response.append(requests.get(url3, headers = headers))
                response = response.append(requests.get(url4, headers = headers))
                response = response.append(requests.get(url5, headers = headers))
            else:
                url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date1}/{date2}.json"
                response = requests.get(url, headers = headers)

            print(url)
            print(response)
            data = response.json()
            print(data)
            data = pformat(data)
            print('WOOOOOOOOOOOOOO')
            return redirect('/')
    else:
        print('ERROR')

            # if response.ok:
            #     print(data)
            #     
                # data = data
                 #figure out what to parse in data/response from FitBit API
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

        # else:
        #     flash('Please provide all of the required information')
        #     return redirect('/fitbitdata')

#     else:
#         #use Mockaroo to generate random entries depending on condition assigned
#         #Anxiety = 0.18, Depression = 0.08, Insomnia = 0.25

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
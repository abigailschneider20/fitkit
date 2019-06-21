"""FitBit Project."""

from jinja2 import StrictUndefined
import os
from pprint import pformat
import json
import random
from gen_user_data_assess_test import (
    Anxiety,
    Depression,
    Insomnia,
    UnaffectedUser,
    assess_phq,
    assess_gad,
    assess_sleep,
    add_stats,
)
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

FITBIT_TOKEN = os.environ.get("FITBIT_TOKEN")
USER_ID = os.environ.get("USER_ID")

app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Renders homepage."""
    return render_template("homepage.html")


@app.route("/register", methods=["GET"])
def register_form():
    """Register new users if user_id is not already in session"""
    if session.get("user_id") != None:
        flash("You have already logged in.")
        return redirect("/dashboard")
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def process_registration():
    """Process new user registration for users who are not already logged in"""
    if session.get("user_id") != None:
        flash("You have already logged in.")
        return redirect("/dashboard")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        age = request.form.get("age")
        sex = request.form.get("sex")

        # inputs new user data into database
        new_user = User(
            email=email,
            password=password,
            f_name=f_name,
            l_name=l_name,
            age=age,
            sex=sex,
        )
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.user_id

        flash("Welcome!")

        # redirects newly registered user to HIPAA form for acknowledgement
        return render_template("/hipaa.html")


@app.route("/hipaa", methods=["POST"])
def hipaa_form():
    """Redirects user to mandatory HIPAA Acknowledgement form and 
    changes boolean in database to True once acknowledged"""
    if request.form.getlist("acknowledged-hipaa"):
        user = User.query.filter(User.user_id == session["user_id"]).first()
        user.has_signed_hipaa = True
        db.session.commit()
        return redirect("/dashboard")
    else:
        flash("You must acknowledge HIPAA Privacy Practices.")
        return render_template("/hipaa.html")


@app.route("/login", methods=["GET"])
def login_form():
    """Sends user to login form to fill out if not already logged in"""
    if session.get("user_id") != None:
        flash("You have already logged in.")
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    """Sends user to user profile once correct email and password combo entered"""
    email = request.form.get("email")
    password = request.form.get("password")

    # users will have unique emails
    user = User.query.filter_by(email=email).first()

    # checks to see if email entered matches one in database
    if not user:
        flash("Incorrect email. Please try again.")
        return redirect("/login")

    # checks to see if password entered matches one affiliated with user email in database
    if user.password != password:
        flash("Incorrect password. Please try again.")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return render_template("dashboard.html", user=user)


@app.route("/logout", methods=["POST"])
def logout():
    """Logs user out unless already logged out/not signed in."""

    if (session.get("user_id", False)) != False:
        del session["user_id"]
        flash("You have successfully logged out.")
        return redirect("/")
    else:
        flash("You have already logged out.")


@app.route("/dashboard")
def dashboard():
    """Shows signed in user dashboard"""
    if session.get("user_id") != None:
        user_id = session.get(
            "user_id"
        )  # query of dailymetrics and user information for table display on dashboard
        user = User.query.options(db.joinedload("dailymetrics")).get(user_id)

        return render_template("dashboard.html", user=user)
    else:
        # redirects users who have not yet logged in
        flash("You must log in in order to view your dashboard.")
        return redirect("/login")


@app.route("/profile")
def show_user_profile():
    """Shows signed in user profile"""
    if session.get("user_id") != None:
        user = User.query.filter_by(user_id=session["user_id"]).one()
        return render_template("user_profile.html", user=user)
    else:
        flash("You must log in in order to view your profile.")
        return redirect("/login")


@app.route("/editprofile", methods=["GET"])
def edit_profile():
    """Shows signed-in user their modifiable profile"""
    if session.get("user_id") != None:
        user = User.query.filter(User.user_id == session["user_id"]).one()
        return render_template("editprofile.html", user=user)
    else:
        flash("You must log in in order to edit your profile.")
        return redirect("/login")


@app.route("/editprofile", methods=["POST"])
def change_profile():
    """Allows user to modify elements of their profile and post changes to database"""
    user = User.query.filter(User.user_id == session["user_id"]).one()
    f_name = request.form.get("f_name")
    l_name = request.form.get("l_name")
    email = request.form.get("email")
    password = request.form.get("password")
    feet = int(request.form.get("feet"))
    inches = int(request.form.get("inches"))
    weight = int(request.form.get("weight"))
    weight = int(
        weight / 2.205
    )  # stores weight input as kg for easier calculation of BMI
    height = round(
        ((feet * 12) + (inches)) * 0.0254, 2
    )  # stores height input as m for easier calculation of BMI
    user.f_name = f_name
    user.l_name = l_name
    user.email = email
    user.password = password
    user.height = height
    user.weight = weight
    db.session.commit()
    flash("You have successfully updated your profile.")
    return redirect("/dashboard")


@app.route("/getfit")
def show_fitbit_form():
    """Redirects user to form to access more FitBit data.
    For user with id 1, can directly access FitBit API and add new data to db.
    For other users, new data will be randomly assigned based on incidences of 
    various mental health conditions and the data will be instantiated for each
    of the days specified in the desired target date range. """
    if session.get("user_id") != None:
        return render_template("fitbitdata.html")
    else:
        flash("You must log in in order to access your FitBit data.")
        return redirect("/login")


def download_fitbitdata(date1, date2):
    # downloads FitBit data for date range for user with user_id 1 (which is accessible via FitBit API).

    activity_type_dict = {
        "sleep": (f"https://api.fitbit.com/1.2/user/-/sleep/date/{date1}/{date2}.json"),
        "activities-heart": (
            f"https://api.fitbit.com/1/user/-/activities/heart/date/{date1}/{date2}.json"
        ),
        "activities-steps": (
            f"https://api.fitbit.com/1/user/-/activities/steps/date/{date1}/{date2}.json"
        ),
        "activities-minutesSedentary": (
            f"https://api.fitbit.com/1/user/-/activities/minutesSedentary/date/{date1}/{date2}.json"
        ),
        "activities-minutesFairlyActive": (
            f"https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/{date1}/{date2}.json"
        ),
        "activities-minutesLightlyActive": (
            f"https://api.fitbit.com/1/user/-/activities/minutesLightlyActive/date/{date1}/{date2}.json"
        ),
        "activities-minutesVeryActive": (
            f"https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/{date1}/{date2}.json"
        ),
    }

    headers = {"Authorization": "Bearer " + FITBIT_TOKEN}

    raw_data = {}
    # compiles responses for each of the separate requests into one dictionary for easier access/parsing
    for k in activity_type_dict:
        response = requests.get(activity_type_dict[k], headers=headers)
        data = response.json()
        rendered_data = data[k]
        raw_data[k] = rendered_data
    return raw_data


def assess_new_testscores():
    """Takes randomly-generated PHQ, GAD, and/or ISI test answers of instances for user's specific class and computes
    score and severity of mental health condition"""
    curr_user = User.query.filter(User.user_id == session["user_id"]).first()
    class_type = curr_user.class_type
    # uses class_type affiliated with new users to calculate scores and assesses severity
    if class_type == "Depression":
        incomplete_PHQ = PHQ.query.filter(
            PHQ.user_id == session["user_id"], PHQ.score == None
        ).all()
        for entry in incomplete_PHQ:
            entry.score = (
                entry.q1_answer
                + entry.q2_answer
                + entry.q3_answer
                + entry.q4_answer
                + entry.q5_answer
                + entry.q6_answer
                + entry.q7_answer
                + entry.q8_answer
                + entry.q9_answer
            )
            entry.dep_severity = assess_phq(entry.score)
    elif class_type == "Anxiety":
        incomplete_GAD = GAD.query.filter(
            GAD.user_id == session["user_id"], GAD.score == None
        ).all()
        for entry in incomplete_GAD:
            entry.score = (
                entry.q1_answer
                + entry.q2_answer
                + entry.q3_answer
                + entry.q4_answer
                + entry.q5_answer
                + entry.q6_answer
                + entry.q7_answer
            )
            entry.anx_severity = assess_gad(entry.score)
    elif class_type == "Insomnia":
        incomplete_ISI = Sleep.query.filter(
            Sleep.user_id == session["user_id"], Sleep.score == None
        ).all()
        for entry in incomplete_ISI:
            entry.score = (
                entry.q1_answer
                + entry.q2_answer
                + entry.q3_answer
                + entry.q4_answer
                + entry.q5_answer
                + entry.q6_answer
                + entry.q7_answer
            )
            entry.insomnia_severity = assess_sleep(entry.score)
    elif class_type == "Unaffected":
        # Unaffected users have PHQ, GAD, and ISIs automatically synthesized upon instantiation
        incomplete_PHQ = PHQ.query.filter(
            PHQ.user_id == session["user_id"], PHQ.score == None
        ).all()
        for entry in incomplete_PHQ:
            entry.score = (
                entry.q1_answer
                + entry.q2_answer
                + entry.q3_answer
                + entry.q4_answer
                + entry.q5_answer
                + entry.q6_answer
                + entry.q7_answer
                + entry.q8_answer
                + entry.q9_answer
            )
            entry.dep_severity = assess_phq(entry.score)
        incomplete_GAD = GAD.query.filter(
            GAD.user_id == session["user_id"], GAD.score == None
        ).all()
        for entry in incomplete_GAD:
            entry.score = (
                entry.q1_answer
                + entry.q2_answer
                + entry.q3_answer
                + entry.q4_answer
                + entry.q5_answer
                + entry.q6_answer
                + entry.q7_answer
            )
            entry.anx_severity = assess_gad(entry.score)
        incomplete_ISI = Sleep.query.filter(
            Sleep.user_id == session["user_id"], Sleep.score == None
        ).all()
        for entry in incomplete_ISI:
            entry.score = (
                entry.q1_answer
                + entry.q2_answer
                + entry.q3_answer
                + entry.q4_answer
                + entry.q5_answer
                + entry.q6_answer
                + entry.q7_answer
            )
            entry.insomnia_severity = assess_sleep(entry.score)
    else:
        return "Error"
    db.session.commit()


def create_new_testscores(curr_user, new_user_data, date):
    # creates new test scores for specified date range based off of user's class type (Depression, Anxiety, Insomnia, UnaffectedUser)
    if curr_user.class_type == "Depression":
        new_PHQ = PHQ(
            user_id=session["user_id"],
            date=date,
            q1_answer=new_user_data.phq1,
            q2_answer=new_user_data.phq2,
            q3_answer=new_user_data.phq3,
            q4_answer=new_user_data.phq4,
            q5_answer=new_user_data.phq5,
            q6_answer=new_user_data.phq6,
            q7_answer=new_user_data.phq7,
            q8_answer=new_user_data.phq8,
            q9_answer=new_user_data.phq9,
        )
        db.session.add(new_PHQ)
        db.session.commit()
        return new_PHQ
    elif curr_user.class_type == "Anxiety":
        new_GAD = GAD(
            user_id=session["user_id"],
            date=date,
            q1_answer=new_user_data.gad1,
            q2_answer=new_user_data.gad2,
            q3_answer=new_user_data.gad3,
            q4_answer=new_user_data.gad4,
            q5_answer=new_user_data.gad5,
            q6_answer=new_user_data.gad6,
            q7_answer=new_user_data.gad7,
        )
        db.session.add(new_GAD)
        db.session.commit()
        return new_GAD
    elif curr_user.class_type == "Insomnia":
        new_ISI = Sleep(
            user_id=session["user_id"],
            date=date,
            q1_answer=new_user_data.isi1,
            q2_answer=new_user_data.isi2,
            q3_answer=new_user_data.isi3,
            q4_answer=new_user_data.isi4,
            q5_answer=new_user_data.isi5,
            q6_answer=new_user_data.isi6,
            q7_answer=new_user_data.isi7,
        )
        db.session.add(new_ISI)
        db.session.commit()
        return new_ISI
    else:
        new_PHQ = PHQ(
            user_id=session["user_id"],
            date=date,
            q1_answer=new_user_data.phq1,
            q2_answer=new_user_data.phq2,
            q3_answer=new_user_data.phq3,
            q4_answer=new_user_data.phq4,
            q5_answer=new_user_data.phq5,
            q6_answer=new_user_data.phq6,
            q7_answer=new_user_data.phq7,
            q8_answer=new_user_data.phq8,
            q9_answer=new_user_data.phq9,
        )
        new_GAD = GAD(
            user_id=session["user_id"],
            date=date,
            q1_answer=new_user_data.gad1,
            q2_answer=new_user_data.gad2,
            q3_answer=new_user_data.gad3,
            q4_answer=new_user_data.gad4,
            q5_answer=new_user_data.gad5,
            q6_answer=new_user_data.gad6,
            q7_answer=new_user_data.gad7,
        )
        new_ISI = Sleep(
            user_id=session["user_id"],
            date=date,
            q1_answer=new_user_data.isi1,
            q2_answer=new_user_data.isi2,
            q3_answer=new_user_data.isi3,
            q4_answer=new_user_data.isi4,
            q5_answer=new_user_data.isi5,
            q6_answer=new_user_data.isi6,
            q7_answer=new_user_data.isi7,
        )
        db.session.add(new_PHQ)
        db.session.add(new_GAD)
        db.session.add(new_ISI)
        db.session.commit()
        return new_PHQ, new_GAD, new_ISI


def create_newuser_data(date1, date2):
    # Synthesizes new user data (either a user of class Anxiety, Depression, Insomnia, or Unaffected) to mock import of FitBit data
    show_fitbit_data_lst = []
    classes = (Anxiety, Depression, Insomnia, UnaffectedUser)
    probs = (
        0.18,
        0.08,
        0.25,
        0.49,
    )  # incidence of Anxiety in US is 18%, Depression is 8%, Insomnia is 25%
    existing_entry = DailyEntry.query.filter(
        DailyEntry.user_id == session["user_id"], DailyEntry.date == date1
    ).first()  # checks for existing entry
    if existing_entry == None:
        new_user_class = numpy.random.choice(
            (classes), p=probs
        )  # randomly assigns class type to new user
        curr_user = User.query.filter(User.user_id == session["user_id"]).first()
        curr_user.class_type = new_user_class.class_type
        new_user = ""
        for i in range((date2 - date1).days + 1):
            date = date1 + timedelta(days=i)
            new_user_data = new_user_class(session["user_id"])
            new_user = DailyEntry(
                user_id=new_user_data.user_id,
                date=date,
                steps=new_user_data.steps,
                sleep=new_user_data.mins_sleep,
                mins_sedentary=new_user_data.mins_sedentary,
                mins_exercise=new_user_data.mins_exercise,
                resting_hr=new_user_data.resting_hr,
            )
            show_fitbit_data_lst.append(new_user)
            new_scores = create_new_testscores(curr_user, new_user_data, date)
            db.session.add(new_user)

        db.session.commit()
    else:
        show_fitbit_data_lst.append(existing_entry)

    return show_fitbit_data_lst


def parse_rawfitbitdata(raw_data, i):
    # Parses raw JSON data from FitBit API with user with user_id 1.
    # Adds new entry for user
    new_entry = DailyEntry(
        user_id=session["user_id"],
        date=raw_data["sleep"][i]["dateOfSleep"],
        sleep=raw_data["sleep"][i]["minutesAsleep"],
    )
    new_entry.mins_exercise = (
        0
    )  # sets mins_exercise to 0 (lightly, fairly, and very active minutes added later on)
    new_entry.resting_hr = raw_data["activities-heart"][i]["value"]["restingHeartRate"]
    new_entry.steps = raw_data["activities-steps"][i]["value"]
    new_entry.mins_sedentary = raw_data["activities-minutesSedentary"][i]["value"]
    new_entry.mins_exercise += int(
        raw_data["activities-minutesLightlyActive"][i]["value"]
    )
    new_entry.mins_exercise += int(
        raw_data["activities-minutesFairlyActive"][i]["value"]
    )
    new_entry.mins_exercise += int(raw_data["activities-minutesVeryActive"][i]["value"])

    db.session.add(new_entry)

    db.session.commit()

    return new_entry


def check_existing_entries(date1, date2, class_type):
    """Checks database for existing FitKit entries for user with user_id 1 (which is accessible via FitBit API) and all
    other new users"""
    show_fitbit_data_lst = []
    if session["user_id"] == 1:
        raw_data = download_fitbitdata(date1, date2)
        for i in range(0, (date2 - date1).days + 1):
            existing_entry = DailyEntry.query.filter(
                DailyEntry.user_id == session["user_id"],
                DailyEntry.date == (date2 - timedelta(days=i)),
            ).first()
            if existing_entry == None:
                new_entry = parse_rawfitbitdata(raw_data, i)
                show_fitbit_data_lst.append(new_entry)
            else:
                show_fitbit_data_lst.append(existing_entry)
    else:
        for i in range(0, (date2 - date1).days + 1):
            existing_entry = DailyEntry.query.filter(
                DailyEntry.user_id == session["user_id"],
                DailyEntry.date == (date2 - timedelta(days=i)),
            ).first()
            if existing_entry == None:
                classes_dict = {
                    "Anxiety": Anxiety,
                    "Depression": Depression,
                    "Insomnia": Insomnia,
                    "UnaffectedUser": UnaffectedUser,
                }
                cls_type = classes_dict[class_type]
                cls_entry = cls_type(session["user_id"])
                new_entry = DailyEntry(
                    user_id=session["user_id"],
                    date=(date2 - timedelta(days=i)),
                    sleep=cls_entry.mins_sleep,
                    steps=cls_entry.steps,
                    mins_exercise=cls_entry.mins_exercise,
                    mins_sedentary=cls_entry.mins_sedentary,
                    resting_hr=cls_entry.resting_hr,
                )
                show_fitbit_data_lst.append(new_entry)
            else:
                show_fitbit_data_lst.append(existing_entry)

    return show_fitbit_data_lst


@app.route("/fitbitdata", methods=["GET"])
def fitbitdata():
    """Processes request of specific biometric data for date range"""
    date1 = request.args.get("date1")
    date2 = request.args.get("date2")
    date1 = datetime.strptime(
        date1, "%Y-%m-%d"
    ).date()  # converts inputs to date format
    date2 = datetime.strptime(date2, "%Y-%m-%d").date()
    user = User.query.filter(User.user_id == session["user_id"]).first()
    class_type = (
        user.class_type
    )  # takes into consideration class type for users with user_id != 1 and adds appropriate data
    prediction = ""

    show_fitbit_data_lst = []
    if date1 and date2:
        if session["user_id"] == 1:
            show_fitbit_data_lst = check_existing_entries(
                date1, date2, class_type
            )  # checks for existing entries of user with id #1
            prediction = predict(
                date1, date2
            )  # uses logistic regression model to predict PHQ, GAD, ISI scores (therefore, likelihood of exhibiting symptoms of Depression, Insomnia, Anxiety)
        else:
            if class_type == None:
                show_fitbit_data_lst = create_newuser_data(
                    date1, date2
                )  # newly-registered users will not have a class assigned yet and will have new data generated
                assess_new_testscores()  # will also have test scores added and assessed
                prediction = predict(
                    date1, date2
                )  # uses logistic regression model to predict PHQ, GAD, ISI scores
            else:
                show_fitbit_data_lst = check_existing_entries(
                    date1, date2, class_type
                )  # other uses who have previously accessed data will check for existing entries and return those
                prediction = predict(
                    date1, date2
                )  # use logistic regression model to predict PHQ, GAD, ISI scores

        return render_template(
            "showfitbitdata.html",
            show_fitbit_data_lst=show_fitbit_data_lst,
            date1=date1,
            date2=date2,
            prediction=prediction,
        )

    else:
        flash("Please provide all of the required information")
        return redirect("/getfit")


def predict(date1, date2):
    # uses logistic regression models to predict mental health test scores based on biometric data (resting heart rate, steps, mins sedentary, mins exercise, sleep)
    recent1 = DailyEntry.query.filter(
        DailyEntry.user_id == session["user_id"], DailyEntry.date >= date1
    ).all()  # checks for metric entries for specified dates
    recent2 = DailyEntry.query.filter(
        DailyEntry.user_id == session["user_id"], DailyEntry.date <= date2
    ).all()
    recent_entries = set(recent1 + recent2)  # ensures no repeat of dates
    steps, sleep, mins_exercise, mins_sedentary, resting_hr = [], [], [], [], []
    for entry in recent_entries:
        steps.append(entry.steps)
        sleep.append(entry.sleep)
        mins_exercise.append(entry.mins_exercise)
        mins_sedentary.append(entry.mins_sedentary)
        resting_hr.append(entry.resting_hr)

    steps = numpy.mean(steps)  # takes means of metrics for predictions
    sleep = numpy.mean(sleep)
    mins_exercise = numpy.mean(mins_exercise)
    mins_sedentary = numpy.mean(mins_sedentary)
    resting_hr = numpy.mean(resting_hr)
    recs = (
        []
    )  # initializes empty list for personalized recommendations based off of prediction and user's biometric data
    if steps < 10000:
        recs.append(f"Try walking {int(10000-steps)} more steps daily")
    if sleep < 420:
        recs.append(f"Try going to sleep {int(420-sleep)} minutes earlier each night")
    if mins_exercise < 40:
        recs.append(
            f"Try adding in {int(40-mins_exercise)} more minutes of exercise daily"
        )
    if resting_hr > 100:
        recs.append(
            f"Consider speaking to your doctor about your elevated resting heart rate and ways to improve your overall cardiovascuclar health"
        )
    user_id = session["user_id"]
    data = [user_id, user_id, steps, sleep, mins_sedentary, mins_exercise, resting_hr]
    phq_prediction = phq_model.predict(
        [data]
    )  # predicts PHQ score (affected or unaffected) based on biometric data
    phq_output = phq_prediction[0]
    gad_prediction = gad_model.predict(
        [data]
    )  # predicts GAD score (affected or unaffected) based on biometric data
    gad_output = gad_prediction[0]
    isi_prediction = isi_model.predict(
        [data]
    )  # predicts ISI score (affected or unaffected) based on biometric data
    isi_output = isi_prediction[0]

    prediction = {"phq": phq_output, "gad": gad_output, "isi": isi_output, "recs": recs}
    return prediction


@app.route("/chartdata")
def chart_data():
    """Return biometric data and personal test
     scores to be displayed on a chart (using ChartJS)"""
    if session.get("user_id") != None:
        if (
            DailyEntry.query.filter(DailyEntry.user_id == session["user_id"]).first()
            != None
        ):
            user = User.query.filter(User.user_id == session["user_id"]).first()
            firstchart_type = request.args.get("firstchart_type")
            secchart_type = request.args.get("secchart_type")
            formatType = request.args.get("format")

            data_dict = {}
            first_dict = {}
            second_dict = {}

            # adds appropriate data to respective dictionaries with dates as keys
            if firstchart_type == "PHQ9":
                for i in user.phq:
                    first_dict[str(i.date)] = int(i.score)
            elif firstchart_type == "GAD7":
                for i in user.gad:
                    first_dict[str(i.date)] = int(i.score)
            else:
                for i in user.sleep:
                    first_dict[str(i.date)] = int(i.score)

            if secchart_type == "Resting Heart Rate":
                for j in user.dailymetrics:
                    second_dict[str(j.date)] = int(j.resting_hr)
            elif secchart_type == "Steps":
                for j in user.dailymetrics:
                    second_dict[str(j.date)] = int(j.steps)
            elif secchart_type == "Mins Slept":
                for j in user.dailymetrics:
                    second_dict[str(j.date)] = int(j.sleep)
            elif secchart_type == "Mins Exercise":
                for j in user.dailymetrics:
                    second_dict[str(j.date)] = int(j.mins_exercise)
            else:
                for j in user.dailymetrics:
                    second_dict[str(j.date)] = int(j.mins_sedentary)
            # adds data1 (selected test type scores) and data2 (selected biometric data) to one dictionary for easier access
            data_dict["data1"] = first_dict
            data_dict["data2"] = second_dict
            secdata_lst = sorted(data_dict["data2"].items())
            date_labels = [
                x[0] for x in secdata_lst
            ]  # second dataset will always have more dates
            for date in date_labels:
                value = data_dict["data1"].get(date, None)
                data_dict["data1"][date] = value
            firstdata_lst = sorted(data_dict["data1"].items())  # sorts data by date
            first_data = [x[1] for x in firstdata_lst]
            sec_data = [x[1] for x in secdata_lst]
            stats1 = [x for x in first_data if x != None]
            if stats1:
                stats1 = add_stats(stats1)
            else:
                stats1 = None
            stats2 = [x for x in sec_data if x != None]
            stats2 = add_stats(stats2)

            if formatType == "json":
                return jsonify(
                    {
                        "labels": date_labels,
                        "datasets": [
                            {
                                "label": firstchart_type,
                                "data": first_data,
                                "colorOpts": {},
                            },
                            {
                                "label": secchart_type,
                                "data": sec_data,
                                "colorOpts": {
                                    "backgroundColor": "#99D3DF",
                                    "borderColor": "#99D3DF",
                                    "pointHoverBackgroundColor": "#99D3DF",
                                    "pointHoverBorderColor": "#99D3DF",
                                },
                            },
                        ],
                        "stats1": stats1,
                        "stats2": stats2,
                    }
                )

            return render_template(
                "chartdata.html",
                labels=date_labels,
                data1=first_data,
                data2=sec_data,
                stats1=stats1,
                stats2=stats2,
            )
        else:
            flash("You must first import FitBit data in order to view your charts.")
            return redirect("/getfit")
    else:
        flash("You must log in in order to access your data.")
        return redirect("/login")


@app.route("/newtest", methods=["GET"])
def navigate_to_tests():
    """Shows user PHQ9, GAD7, and ISI tests to take"""
    if session.get("user_id") != None:
        return render_template("newtest.html")
    else:
        flash("You must log in in order to take a test.")
        return redirect("/login")


@app.route("/newtest", methods=["POST"])
def insert_answers_into_db():
    """Inserts user answers, scores, and mental health severity from PHQ9, GAD7, ISI tests into database"""
    test_type = request.form.get("testtype")

    if test_type == "phq":
        q1_answer = int(request.form.get("q1phq"))
        q2_answer = int(request.form.get("q2phq"))
        q3_answer = int(request.form.get("q3phq"))
        q4_answer = int(request.form.get("q4phq"))
        q5_answer = int(request.form.get("q5phq"))
        q6_answer = int(request.form.get("q6phq"))
        q7_answer = int(request.form.get("q7phq"))
        q8_answer = int(request.form.get("q8phq"))
        q9_answer = int(request.form.get("q9phq"))
        score = (
            q1_answer
            + q2_answer
            + q3_answer
            + q4_answer
            + q5_answer
            + q6_answer
            + q7_answer
            + q8_answer
            + q9_answer
        )
        dep_severity = assess_phq(score)
        new_test = PHQ(
            user_id=session["user_id"],
            date=date.today().strftime("%Y-%m-%d"),
            q1_answer=q1_answer,
            q2_answer=q2_answer,
            q3_answer=q3_answer,
            q4_answer=q4_answer,
            q5_answer=q5_answer,
            q6_answer=q6_answer,
            q7_answer=q7_answer,
            q8_answer=q8_answer,
            q9_answer=q9_answer,
            score=score,
            dep_severity=dep_severity,
        )
        db.session.add(new_test)
        db.session.commit()
        flash(
            f'You successfully submitted your PHQ9 results. Your score is {score} which indicates a Depression severity of "{dep_severity}"'
        )
        return redirect("/dashboard")
    elif test_type == "gad":
        q1_answer = int(request.form.get("q1gad"))
        q2_answer = int(request.form.get("q2gad"))
        q3_answer = int(request.form.get("q3gad"))
        q4_answer = int(request.form.get("q4gad"))
        q5_answer = int(request.form.get("q5gad"))
        q6_answer = int(request.form.get("q6gad"))
        q7_answer = int(request.form.get("q7gad"))
        score = (
            q1_answer
            + q2_answer
            + q3_answer
            + q4_answer
            + q5_answer
            + q6_answer
            + q7_answer
        )
        anx_severity = assess_gad(score)
        new_test = GAD(
            user_id=session["user_id"],
            date=date.today().strftime("%Y-%m-%d"),
            q1_answer=q1_answer,
            q2_answer=q2_answer,
            q3_answer=q3_answer,
            q4_answer=q4_answer,
            q5_answer=q5_answer,
            q6_answer=q6_answer,
            q7_answer=q7_answer,
            score=score,
            anx_severity=anx_severity,
        )
        db.session.add(new_test)
        db.session.commit()

        flash(
            f'You successfully submitted your GAD7 results. Your score is {score} which indicates an Anxiety severity of "{anx_severity}"'
        )
        return redirect("/dashboard")
    elif test_type == "sleep":
        q1_answer = int(request.form.get("q1"))
        q2_answer = int(request.form.get("q2"))
        q3_answer = int(request.form.get("q3"))
        q4_answer = int(request.form.get("q4"))
        q5_answer = int(request.form.get("q5"))
        q6_answer = int(request.form.get("q6"))
        q7_answer = int(request.form.get("q7"))
        score = (
            q1_answer
            + q2_answer
            + q3_answer
            + q4_answer
            + q5_answer
            + q6_answer
            + q7_answer
        )
        insomnia_severity = assess_sleep(score)
        new_test = Sleep(
            user_id=session["user_id"],
            date=date.today().strftime("%Y-%m-%d"),
            q1_answer=q1_answer,
            q2_answer=q2_answer,
            q3_answer=q3_answer,
            q4_answer=q4_answer,
            q5_answer=q5_answer,
            q6_answer=q6_answer,
            q7_answer=q7_answer,
            score=score,
            insomnia_severity=insomnia_severity,
        )
        db.session.add(new_test)
        db.session.commit()

        flash(
            f'You successfully submitted your Sleep Questionnaire results. Your score is {score} which indicates an Insomnia severity of "{insomnia_severity}"'
        )
        return redirect("/dashboard")
    else:
        flash("Please select a type of test to take.")
        return redirect("/newtest")


def assess_bmi(bmi):
    """Categorizes user as Underweight, Normal, Overweight, or Obese based off of BMI calculation. Specified on BMI
    HTML form that user input must be an integer. 
    >>> assess_bmi(17)
    'Underweight'
    >>> assess_bmi(18.6)
    'Normal'
    >>> assess_bmi(20)
    'Normal'
    >>> assess_bmi(27)
    'Overweight'
    >>> assess_bmi(30)
    'Obese'
    """
    if bmi <= 18.5:
        return "Underweight"
    elif bmi > 18.5 and bmi <= 24.9:
        return "Normal"
    elif bmi >= 25 and bmi < 29.9:
        return "Overweight"
    elif bmi >= 30:
        return "Obese"
    else:
        return "Error"


@app.route("/bmi", methods=["GET"])
def calculate_bmi():
    """Calculates user's BMI using BMI formula and renders HTML page with recommendations based off of their biometric data"""
    if session.get("user_id") != None:
        user = User.query.filter_by(user_id=session["user_id"]).one()
        if user.weight and user.height:
            class_type = user.class_type
            bmi = round((user.weight / (user.height ** 2)), 1)
            assessment = assess_bmi(bmi)
            return render_template(
                "bmi.html", bmi=bmi, assessment=assessment, class_type=class_type
            )
        else:
            flash(
                "You must update your weight and height before accessing the BMI calculator."
            )
            return redirect("/editprofile")
    else:
        flash("You must be logged in to access the BMI calculator.")
        return redirect("/login")


if __name__ == "__main__":
    # loads logistic regression models into database for use in predicting mental health conditions based off of biometric data
    phq_model = pickle.load(open("phq.pkl", "rb"))
    gad_model = pickle.load(open("gad.pkl", "rb"))
    isi_model = pickle.load(open("isi.pkl", "rb"))
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar during development
    DebugToolbarExtension(app)

    import doctest

    result = doctest.testmod()

    app.run()

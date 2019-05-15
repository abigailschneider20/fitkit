from sqlalchemy import func

from model import connect_to_db, db, User, DailyMetric, GAD, PHQ, Sleep
from server import app


def load_users():
    """Load users from u.user into database."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, email, password = row.split("|")

        user = User(user_id=user_id,
                    email = email,
                    password = password)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_dailymetrics():
    """Load daily metrics from u.dailymetrics into database."""

    DailyMetric.query.delete()

    for row in open("seed_data/u.dailymetrics"):
        row = row.rstrip()
        (entry_id, user_id, steps_walked, mins_slept, mins_exercise, 
        mins_sedentary, resting_hr, date) = row.split("|")

        dailymetric = DailyMetric(entry_id = entry_id,
                                    user_id = user_id, 
                                    steps_walked = steps_walked,
                                    mins_slept = mins_slept,
                                    mins_exercise = mins_exercise,
                                    mins_sedentary = mins_sedentary,
                                    resting_hr = resting_hr, 
                                    date = date)

        db.session.add(dailymetric)

    db.session.commit()




# def load_weeklymetrics():
#     """Load weekly metrics from u.weeklymetric into database."""
#     WeeklyMetric.query.delete()

#     for row in open("seed_data/u.weeklymetrics"):
#         (entry_id, user_id, avg_steps_walked, 
#         avg_mins_slept, avg_mins_exercise,
#         avg_resting_hr, start_date, end_date) = row.split("|")

#         weeklymetric = WeeklyMetric(entry_id = entry_id,
#                                     user_id = user_id,
#                                     avg_steps_walked = avg_steps_walked,
#                                     avg_mins_slept = avg_mins_slept,
#                                     avg_mins_exercise = avg_mins_exercise,
#                                     avg_resting_hr = avg_resting_hr, 
#                                     start_date = start_date,
#                                     end_date = end_date)
#         db.session.add(weeklymetric)

#     db.session.commit()

# def load_monthlymetrics():
#     """Load monthly metrics from u.monthlymetric into database."""
#     MonthlyMetric.query.delete()

#     for row in open("seed_data/u.monthlymetrics"):
#         (entry_id, user_id, avg_steps_walked, 
#         avg_mins_slept, avg_mins_exercise,
#         avg_resting_hr, start_date, end_date) = row.split("|")

#         monthlymetric = MonthlyMetric(entry_id = entry_id,
#                                     user_id = user_id,
#                                     avg_steps_walked = avg_steps_walked,
#                                     avg_mins_slept = avg_mins_slept,
#                                     avg_mins_exercise = avg_mins_exercise,
#                                     avg_resting_hr = avg_resting_hr, 
#                                     start_date = start_date,
#                                     end_date = end_date)
#         db.session.add(monthlymetric)

#     db.session.commit()

def load_phq():
    """Load PHQ9 info from u.phq into database."""
    PHQ.query.delete()

    for row in open("seed_data/u.phq"):
        (phq_id, user_id, date, q1, q2, 
        q3, q4, q5, q6, q7, q8, q9, score,
        dep_severity) = row.split("|")

        phq = PHQ(phq_id = phq_id, 
                user_id = user_id,
                date = date, 
                q1_answer = q1, 
                q2_answer = q2, 
                q3_answer = q3, 
                q4_answer = q4, 
                q5_answer = q5,
                q6_answer = q6, 
                q7_answer = q7, 
                q8_answer = q8, 
                q9_answer = q9,
                score = score, 
                dep_severity = dep_severity)

        db.session.add(phq)

    db.session.commit()

def load_gad():
    """Load GAD7 info from u.gad into database."""
    GAD.query.delete()

    for row in open("seed_data/u.gad"):
        (gad_id, user_id, date, q1, q2, 
        q3, q4, q5, q6, q7, score,
        anx_severity)= row.split("|")

        gad = GAD(gad_id = gad_id, 
                user_id = user_id,
                date = date, 
                q1_answer = q1, 
                q2_answer = q2, 
                q3_answer = q3, 
                q4_answer = q4, 
                q5_answer = q5,
                q6_answer = q6, 
                q7_answer = q7,  
                score = score, 
                anx_severity = anx_severity)

        db.session.add(gad)
        
    db.session.commit()
def load_sleep():
    """Load sleep questionnaire info from u.sleep into database."""
    Sleep.query.delete()

    for row in open("seed_data/u.sleep"):
        (sleep_id, user_id, date, q1, q2, 
        q3, q4, q5, q6, q7, q8, q9, q10, score,
        insomnia_severity) = row.split("|")

        sleep = Sleep(sleep_id = sleep_id, 
                    user_id = user_id,
                    date = date, 
                    q1_answer = q1, 
                    q2_answer = q2, 
                    q3_answer = q3, 
                    q4_answer = q4, 
                    q5_answer = q5,
                    q6_answer = q6, 
                    q7_answer = q7,  
                    q8_answer= q8, 
                    q9_answer = q9,
                    q10_answer = q10, 
                    score = score, 
                    insomnia_severity = insomnia_severity)

        db.session.add(sleep)
        
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_dailymetrics()
    load_phq()
    load_gad()
    load_sleep()

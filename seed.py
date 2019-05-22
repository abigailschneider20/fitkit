from sqlalchemy import func

from model import connect_to_db, db, User, MetricType, DailyEntry, GAD, PHQ, Sleep
from server import app


def load_users():
    """Load users from u.user into database."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        (user_id, email, password, f_name, l_name,
            sex, age, weight, height) = row.split("|")

        user = User(user_id=user_id,
                    email = email,
                    password = password, 
                    f_name = f_name,
                    l_name = l_name, 
                    sex = sex, 
                    age = age,
                    weight = weight, 
                    height = height)

        db.session.add(user)

    db.session.commit()

def load_metrictypes():
    """Load metric types from u.metrictypes into database."""
    MetricType.query.delete()

    for row in open("seed_data/u.metrictypes"):
        row = row.rstrip()
        type_id, activity_name = row.split("|")

        metrictype = MetricType(type_id = type_id, activity_name = activity_name)

        db.session.add(metrictype)

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
        (sleep, user, date, q1, q2,
        q3, q4, q5, q6, q7, score,
        insomnia)= row.split("|")

        sleep = Sleep(sleep_id = sleep, 
                    user_id = user,
                    date = date, 
                    q1_answer = q1, 
                    q2_answer = q2, 
                    q3_answer = q3, 
                    q4_answer = q4, 
                    q5_answer = q5,
                    q6_answer = q6, 
                    q7_answer = q7,   
                    score = score, 
                    insomnia_severity = insomnia)

        db.session.add(sleep)
        
    db.session.commit()

def load_dailyentries():
    """Load daily metrics from u.dailymetrics into database."""

    DailyEntry.query.delete()

    for row in open("seed_data/u.dailymetrics"):
        entry, user, type_id, val, date = row.split("|")

        daily = DailyEntry(entry_id = entry,
                                user_id = user,
                                type_id = type_id,
                                val = val,
                                date = date)

        db.session.add(daily)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_metrictypes()
    load_dailyentries()
    load_phq()
    load_gad()
    load_sleep()

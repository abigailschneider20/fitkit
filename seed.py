from sqlalchemy import func

from model import connect_to_db, db, User, DailyEntry, GAD, PHQ, Sleep
from server import app


def load_users():
    """Load users from u.user into database."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        uid,email,pword,fn,ln,sx,a,w,h = row.split("|")

        user = User(user_id=uid,
                    email = email,
                    password = pword, 
                    f_name = fn,
                    l_name = ln, 
                    sex = sx, 
                    age = a,
                    weight = w, 
                    height = h)

        db.session.add(user)

    db.session.commit()



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
        entry, user, date, steps, sleep, mins_sedentary, mins_exercise, resting_hr = row.split("|")

        daily = DailyEntry(entry_id = entry,
                                user_id = user,
                                date = date,
                                steps = steps,
                                sleep = sleep,
                                mins_sedentary = mins_sedentary,
                                mins_exercise = mins_exercise,
                                resting_hr = resting_hr)

        db.session.add(daily)

    db.session.commit()

def set_val_user_id():
#     """Sets value for the next user_id after seeding database"""

    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_dailyentries()
    load_phq()
    load_gad()
    load_sleep()

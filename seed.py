from sqlalchemy import func
from model import User, DailyMetric, WeeklyMetric, MonthlyMetric, PHQ, GAD, Sleep


from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, email, password, has_signed_hipaa = row.split("|")

        user = User(user_id=user_id,
                    email = email,
                    password = password,
                    has_signed_hipaa = has_signed_hipaa)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_dailymetrics():
    """Load daily metrics from u.dailymetric into database."""
    DailyMetric.query.delete()

    for row in open("seed_data/u.dailymetric"):
        row = row.rstrip()
        entry_id, user_id, steps_walked, mins_slept, mins_exercise, 
        mins_sedentary, resting_hr, date = row.split("|")

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




def load_weeklymetrics():
    """Load weekly metrics from u.weeklymetric into database."""
    WeeklyMetric.query.delete()

    for row in open("seed_data/u.weeklymetric"):
        entry_id, user_id, avg_steps_walked, 
        avg_mins_slept, avg_mins_exercise,
        avg_resting_hr, start_date, end_date = row.split("|")

        weeklymetric = WeeklyMetric(entry_id = entry_id,
                                    user_id = user_id,
                                    avg_steps_walked = avg_steps_walked,
                                    avg_mins_slept = avg_mins_slept,
                                    avg_mins_exercise = avg_mins_exercise,
                                    avg_resting_hr = avg_resting_hr, 
                                    start_date = start_date,
                                    end_date = end_date)
        db.session.add(weeklymetric)

    db.session.commit()

def load_monthlymetrics():
    """Load monthly metrics from u.monthlymetric into database."""
    MonthlyMetric.query.delete()

    for row in open("seed_data/u.monthlymetric"):
        entry_id, user_id, avg_steps_walked, 
        avg_mins_slept, avg_mins_exercise,
        avg_resting_hr, start_date, end_date = row.split("|")

        monthlymetric = MonthlyMetric(entry_id = entry_id,
                                    user_id = user_id,
                                    avg_steps_walked = avg_steps_walked,
                                    avg_mins_slept = avg_mins_slept,
                                    avg_mins_exercise = avg_mins_exercise,
                                    avg_resting_hr = avg_resting_hr, 
                                    start_date = start_date,
                                    end_date = end_date)
        db.session.add(monthlymetric)

    db.session.commit()

def load_phq():
    """Load PHQ9 info from u.phq into database."""

def load_gad():
    """Load GAD7 info from u.gad into database."""

def load_sleep():
    """Load sleep questionnaire info from u.sleep into database."""


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_dailymetrics()
    load_weeklymetrics()
    load_monthlymetrics()
    load_phq()
    load_gad()
    load_sleep()
    set_val_user_id()

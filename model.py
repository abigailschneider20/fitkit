"""Models and database functions for Fitbit project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of FitKit web app."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(40), nullable=True)
    has_signed_hipaa = db.Column(db.Boolean, default = True)

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"

class DailyMetric(db.Model):
    """Daily metrics of users of app"""

    __tablename__ = "dailymetrics"

    entry_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    steps_walked = db.Column(db.Integer, nullable = True)
    mins_slept = db.Column(db.Integer, nullable = True)
    mins_exercise = db.Column(db.Integer, nullable = True)
    mins_sedentary = db.Column(db.Integer, nullable = True)
    resting_hr = db.Column(db.Integer, nullable = True)
    date = db.Column(db.DateTime)

    user = db.relationship('User', 
                            backref = db.backref('dailymetrics', 
                                order_by = user_id))
    def __repr__(self):
        return f"<Daily Metric user_id={self.user_id} entry_id={self.entry_id}>"

# class WeeklyMetric(db.Model):
#     """Weekly metrics of users of app"""
#     #randomg JSON file to load recent data; function; three profiles: mock data loaded into db
#     #

#     __tablename__ = "weeklymetrics"

#     entry_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#     avg_steps_walked = db.Column(db.Integer, nullable = True)
#     avg_mins_slept = db.Column(db.Integer, nullable = True)
#     avg_mins_exercise = db.Column(db.Integer, nullable = True)
#     avg_resting_hr = db.Column(db.Integer, nullable = True)
#     start_date = db.Column(db.DateTime)
#     end_date = db.Column(db.DateTime)

#     user = db.relationship('User', 
#                             backref = db.backref('weeklymetrics', 
#                                 order_by = user_id))
#     def __repr__(self):
#         return f"<Weekly Metric user_id={self.user_id} entry_id={self.entry_id}>"

# class MonthlyMetric(db.Model):
#     """Metrics of users of app"""

#     __tablename__ = "monthlymetrics"

#     entry_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#     avg_steps_walked = db.Column(db.Integer, nullable = True)
#     avg_mins_slept = db.Column(db.Integer, nullable = True)
#     avg_mins_exercise = db.Column(db.Integer, nullable = True)
#     avg_resting_hr = db.Column(db.Integer, nullable = True)
#     start_date = db.Column(db.DateTime)
#     end_date = db.Column(db.DateTime)

#     user = db.relationship('User', 
#                             backref = db.backref('monthlymetrics', 
#                                 order_by = user_id))

#     def __repr__(self):
#         return f"<Monthly Metric user_id={self.user_id} entry_id={self.entry_id}>"

class PHQ(db.Model):
    """User question values for PHQ9"""

    __tablename__ = "phq"

    phq_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date = db.Column(db.DateTime)
    q1_answer = db.Column(db.Integer, nullable = True)
    q2_answer = db.Column(db.Integer, nullable = True)
    q3_answer = db.Column(db.Integer, nullable = True)
    q4_answer = db.Column(db.Integer, nullable = True)
    q5_answer = db.Column(db.Integer, nullable = True)
    q6_answer = db.Column(db.Integer, nullable = True)
    q7_answer = db.Column(db.Integer, nullable = True)
    q8_answer = db.Column(db.Integer, nullable = True)
    q9_answer = db.Column(db.Integer, nullable = True)
    score = db.Column(db.Integer, nullable = True)
    dep_severity = db.Column(db.String(20), nullable = True)
    

    user = db.relationship('User', 
                            backref = db.backref('phq', 
                                order_by = user_id))

    def __repr__(self):
        return f"<PHQ user_id={self.user_id} PHQ_ID={self.phq_id}>"

class GAD(db.Model):
    """User question values for GAD7"""

    __tablename__ = "gad"

    gad_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date = db.Column(db.DateTime)
    q1_answer = db.Column(db.Integer, nullable = True)
    q2_answer = db.Column(db.Integer, nullable = True)
    q3_answer = db.Column(db.Integer, nullable = True)
    q4_answer = db.Column(db.Integer, nullable = True)
    q5_answer = db.Column(db.Integer, nullable = True)
    q6_answer = db.Column(db.Integer, nullable = True)
    q7_answer = db.Column(db.Integer, nullable = True)
    score = db.Column(db.Integer, nullable = True)
    anx_severity = db.Column(db.String(20), nullable = True)

    user = db.relationship('User', 
                            backref = db.backref('gad', 
                                order_by = user_id))
    def __repr__(self):
        return f"<GAD user_id={self.user_id} GAD ID ={self.gad_id}>"

class Sleep(db.Model):
    """User question values for Sleep Questionnaire"""

    __tablename__ = "sleep"

    sleep_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date = db.Column(db.DateTime)
    q1_answer = db.Column(db.Integer, nullable = True) 
    q2_answer = db.Column(db.Integer, nullable= True)
    q3_answer = db.Column(db.Integer, nullable = True)
    q4_answer = db.Column(db.Integer, nullable = True)
    q5_answer = db.Column(db.Integer, nullable = True)
    q6_answer = db.Column(db.Integer, nullable = True)
    q7_answer = db.Column(db.Integer, nullable = True)
    q8_answer = db.Column(db.Integer, nullable = True)
    q9_answer = db.Column(db.Integer, nullable = True)
    q10_answer = db.Column(db.Integer, nullable= True)
    score = db.Column(db.Integer, nullable = True)
    insomnia_severity = db.Column(db.String(20), nullable = True)


    user = db.relationship('User', 
                            backref = db.backref('sleep', 
                                order_by = user_id))

    def __repr__(self):
        return f"<Sleep user_id={self.user_id} Sleep ID={self.sleep_id}>"

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///fitbit'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print("Connected to DB.")

import random

# def generate_random_user_info():
# """
# need to assign random info to user: start with resting heart rate
# when new user enters database
# anxiety: 0.18
# depression: 0.08
# insomnia: 0.25
# populates table
# also need a function to add data to table, maybe in actual server.py

# """
#     random_gen=random.choice(['anxiety', 'depression', 'insomnia', 'not_affected'], 5, p = [0.18, 0.08, 0.25, 0.49])
#     print(random_gen)
    
class Anxiety(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 300))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))

class Depression(object):
    def__init_(self, email, password):
        self.email = email
        self.password = password
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 600))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))



class Insomnia(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 300))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))

class UnaffectedUser(object):

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.resting_hr = (random.randrange(50,100))
        self.mins_sleep = (random.randrange(420, 540))
        self.mins_exercise = (random.randrange(20, 300))
        self.mins_sedentary = (random.randrange(200, 600)) #avg. american sedentary for 4-6 hrs
        self.steps = (random.randrange(5000, 15000))




# def anxiety_user():

# def depression_user():

# def insomnia_user():

# def unaffected_user():
#     resting_hr = random.randrange(50,100)
#     mins_of_sleep = random.randrange(420, 540)
#     mins_of_exercise = random.randrange(20, 210)
#     mins_sedentary = random.randrange(200, 500)
#     steps = random.randrange(5000, 15000)

#     print(resting_hr)
#     print(mins_of_sleep)
#     print(mins_of_exercise)
#     print(mins_sedentary)
#     print(steps)


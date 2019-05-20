import numpy as np
import random



# anxiety: 0.18
# depression: 0.08
# insomnia: 0.25
# populates table
# also need a function to add data to table, maybe in actual server.py

# """



class Anxiety(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 300))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))

class Depression(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 600))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))



class Insomnia(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 300))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))

class UnaffectedUser(object):

    def __init__(self, user_id):
        self.user_id = user_id
        self.resting_hr = (random.randrange(50,100))
        self.mins_sleep = (random.randrange(420, 540))
        self.mins_exercise = (random.randrange(20, 300))
        self.mins_sedentary = (random.randrange(200, 600)) #avg. american sedentary for 4-6 hrs
        self.steps = (random.randrange(5000, 15000))


def generate_random(user_id):
    classes = (Anxiety, Depression, Insomnia, UnaffectedUser)
    probs = (0.18, 0.08, 0.25, 0.49)
    new_user = np.random.choice((classes), p=probs)(user_id)
    
    
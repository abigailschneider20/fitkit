import numpy as np
import random



# anxiety: 0.18
# depression: 0.08
# insomnia: 0.25
# populates table

# """



class Anxiety(object):
    class_type = 'Anxiety'
    def __init__(self, user_id):
        self.user_id = user_id
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 300))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))
        self.gad1 = (random.randrange(2, 3))
        self.gad2 = (random.randrange(2, 3))
        self.gad3= (random.randrange(2, 3))
        self.gad4= (random.randrange(2, 3))
        self.gad5= (random.randrange(2, 3))
        self.gad6= (random.randrange(2, 3))
        self.gad7= (random.randrange(2, 3))


class Depression(object):
    class_type = 'Depression'
    def __init__(self, user_id):
        self.user_id = user_id
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 600))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))
        self.phq1 = (random.randrange(2,3))
        self.phq2 = (random.randrange(2,3))
        self.phq3 = (random.randrange(2,3))
        self.phq4 = (random.randrange(2,3))
        self.phq5 = (random.randrange(2,3))
        self.phq6 = (random.randrange(2,3))
        self.phq7 = (random.randrange(2,3))
        self.phq8 = (random.randrange(2,3))
        self.phq9 = (random.randrange(2,3))

class Insomnia(object):
    class_type = 'Insomnia'
    def __init__(self, user_id):
        self.user_id = user_id
        self.resting_hr = (random.randrange(65, 110))
        self.mins_sleep = (random.randrange(0, 300))
        self.mins_exercise = (random.randrange(0, 40))
        self.mins_sedentary = (random.randrange(500, 750))
        self.steps = (random.randrange(2000, 8000))
        self.isi1 = (random.randrange(3, 4))
        self.isi2 = (random.randrange(3, 4))
        self.isi3= (random.randrange(3, 4))
        self.isi4= (random.randrange(3, 4))
        self.isi5= (random.randrange(3, 4))
        self.isi6= (random.randrange(3, 4))
        self.isi7= (random.randrange(3, 4))


class UnaffectedUser(object):
    class_type = 'Unaffected'
    def __init__(self, user_id):
        self.user_id = user_id
        self.resting_hr = (random.randrange(50,100))
        self.mins_sleep = (random.randrange(420, 540))
        self.mins_exercise = (random.randrange(20, 300))
        self.mins_sedentary = (random.randrange(200, 600)) #avg. american sedentary for 4-6 hrs
        self.steps = (random.randrange(5000, 15000))
        self.gad1 = (random.randrange(0, 1))
        self.gad2 = (random.randrange(0, 1))
        self.gad3= (random.randrange(0, 1))
        self.gad4= (random.randrange(0, 1))
        self.gad5= (random.randrange(0, 1))
        self.gad6= (random.randrange(0, 1))
        self.gad7= (random.randrange(0, 1))
        self.isi1 = (random.randrange(0, 1))
        self.isi2 = (random.randrange(0, 1))
        self.isi3= (random.randrange(0, 1))
        self.isi4= (random.randrange(0, 1))
        self.isi5= (random.randrange(0, 1))
        self.isi6= (random.randrange(0, 1))
        self.isi7= (random.randrange(0, 1))
        self.phq1 = (random.randrange(0, 1))
        self.phq2 = (random.randrange(0, 1))
        self.phq3= (random.randrange(0, 1))
        self.phq4= (random.randrange(0, 1))
        self.phq5= (random.randrange(0, 1))
        self.phq6= (random.randrange(0, 1))
        self.phq7= (random.randrange(0, 1))
        self.phq8= (random.randrange(0, 1))
        self.phq9= (random.randrange(0, 1))
        
def generate_random(user_id):
    classes = (Anxiety, Depression, Insomnia, UnaffectedUser)
    probs = (0.18, 0.08, 0.25, 0.49)
    new_user = np.random.choice((classes), p=probs)(user_id)
    

def assess_phq(score):
    if score >=0 and score <=4:
        return 'None'
    elif score >=5 and score <=9:
        return 'Mild'
    elif score >=10 and score <=14:
        return 'Moderate'
    elif score >= 15 and score <=19:
        return 'Moderately Severe'
    else:
        return 'Severe'

def assess_sleep(score):
    if score >=0 and score <=7:
        return 'None'
    elif score >=8 and score <=14:
        return 'Subthreshold insomnia'
    elif score >=15 and score <=21:
        return 'Moderate severity clinical insomnia'
    elif score >= 22 and score <=28:
        return 'Severe clinical insomnia'

def assess_gad(score):
    if score >=0 and score <=5:
        return 'None'
    elif score >=6 and score <=10:
        return 'Mild'
    elif score >=11 and score <=15:
        return 'Moderate'
    else:
        return 'Severe'


def add_stats(data1, data2):
    # np.mean()

    # mean : fitbit data
    # mean: test scores and interpretations of those scores using assess above
    # median : fitbit data
    # range()
    # std

    test_score_array = np.array(data1)
    test_mean = np.mean(test_score_array)
    fit_score_array = np.array(data2)
    fit_mean = np.mean(fit_score_array)
    test_median = np.median(test_score_array)
    fit_median = np.median(fit_score_array)
    test_range = np.ptp(test_score_array)
    fit_range = np.ptp(fit_score_array)
    test_std = np.std(test_score_array)
    fit_std = np.std(fit_score_array)
    stats_dict = {'test':{
                'mean': int(test_mean),
                'median': int(test_median),
                'range': int(test_range),
                'std': int(test_std)}, 
                'fit':{
                'mean': int(fit_mean),
                'median': int(fit_median),
                'range': int(fit_range),
                'std': int(fit_std)
                }}
    return stats_dict
    

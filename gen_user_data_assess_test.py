import numpy as np
import random



# anxiety: 0.18
# depression: 0.08
# insomnia: 0.25
# populates table

# """



class Anxiety(object):
    """
    Generates user with biometric data consistent with individuals with
    anxiety (ex. increased risk for atrial fibrillation, panic attacks, difficulty falling asleep)
    and Generalized Anxiety Disorder 7 Test scores (standard for diagnosing Anxiety).

    >>> annie=Anxiety(250)
    >>> annie.resting_hr in range(65, 110)
    True
    >>> annie.mins_sleep in range(0, 300)
    True
    >>> annie.mins_exercise in range(0, 40)
    True
    >>> annie.mins_sedentary in range(500, 750)
    True
    >>> annie.steps in range(2000, 8000)
    True
    >>> annie.gad1 in range(2,3)
    True
    >>> annie.gad2 in range(2,3)
    True
    >>> annie.gad3 in range(2,3)
    True
    """
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
    """
    Generates user with biometric data consistent with individuals with Depression (
    ex. increased sleep, decreased activity, etc.) and Patient Health Questionnaire 9 Test
    scores (standard for diagnosing Depression).

    >>> dan = Depression(1)
    >>> dan.resting_hr in range(65,110)
    True
    >>> dan.mins_sleep in range(0, 600)
    True
    >>> dan.mins_exercise in range(0, 40)
    True
    >>> dan.mins_sedentary in range(500, 750)
    True
    >>> dan.steps in range(2000, 8000)
    True
    >>> dan.phq1 in range (2,3)
    True
    >>> dan.phq4 in range(2,3)
    True
    >>> dan.phq9 in range(2,3)
    True
    """
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
    """
    Generates user with biometric data consistent with individuals with Insomnia(
    ex. decreased sleep, decreased daily activity, etc.) and Insomnia Severity Index Test
    scores (standard for diagnosing Insomnia).

    >>> ina = Insomnia(4)
    >>> ina.resting_hr in range (65,110)
    True
    >>> ina.mins_sleep in range (0, 300)
    True
    >>> ina.mins_exercise in range (0, 40)
    True
    >>> ina.mins_sedentary in range (500, 750)
    True
    >>> ina.steps in range (2000, 8000)
    True
    >>> ina.isi1 in range (3, 4)
    True
    >>> ina.isi3 in range (3, 4)
    True
    >>> ina.isi7 in range (3, 4)
    True
    """
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
    """
    Generates user with biometric data similar to individuals unaffected by mental illness and 
    GAD7, PHQ9, ISI test scores.

    >>> uma = UnaffectedUser(6)
    >>> uma.resting_hr in range (50, 100)
    True
    >>> uma.mins_sleep in range (420, 540)
    True
    >>> uma.mins_exercise in range (20, 300)
    True
    >>> uma.mins_sedentary in range (200, 600)
    True
    >>> uma.steps in range (5000, 15000)
    True
    >>> uma.gad1 in range (0, 1)
    True
    >>> uma.isi1 in range (0,1)
    True
    >>> uma.phq1 in range (0, 1)
    True
    """
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
        

def assess_phq(score):
    """
    Takes PHQ9 score as a parameter and evaluates Depression severity.

    >>> assess_phq(4)
    'None'
    >>> assess_phq(8)
    'Mild'
    >>> assess_phq(14)
    'Moderate'
    >>> assess_phq(19)
    'Moderately Severe'
    >>> assess_phq(20)
    'Severe'
    """
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
    """
    Takes ISI score as a parameter and evaluates Insomnia severity. 

    >>> assess_sleep(7)
    'None'
    >>> assess_sleep(9)
    'Subthreshold insomnia'
    >>> assess_sleep(16)
    'Moderate severity clinical insomnia'
    >>> assess_sleep(23)
    'Severe clinical insomnia'
    """
    if score >=0 and score <=7:
        return 'None'
    elif score >=8 and score <=14:
        return 'Subthreshold insomnia'
    elif score >=15 and score <=21:
        return 'Moderate severity clinical insomnia'
    elif score >= 22 and score <=28:
        return 'Severe clinical insomnia'

def assess_gad(score):
    """
    Takes GAD7 score as a parameter and evaluates Anxiety severity.

    >>> assess_gad(5)
    'None'
    >>> assess_gad(9)
    'Mild'
    >>> assess_gad(15)
    'Moderate'
    >>> assess_gad(20)
    'Severe'

    """
    if score >=0 and score <=5:
        return 'None'
    elif score >=6 and score <=10:
        return 'Mild'
    elif score >=11 and score <=15:
        return 'Moderate'
    else:
        return 'Severe'


def add_stats(data):
    """
    Takes specified FitBit data or test scores for a date range and outputs mean,
    median, range, and standard deviation for that data. 

    >>> stats_dict = add_stats([50, 40, 60, 90, 100, 20])
    >>> print(stats_dict)
    {'mean': 60, 'median': 55, 'range': 80, 'std': 27}
    >>> stats_dict = add_stats([20000, 30000, 50000, 1000, 10000])
    >>> print(stats_dict)
    {'mean': 22200, 'median': 20000, 'range': 49000, 'std': 16951}
    """
    test_score_array = np.array(data)
    test_mean = np.mean(test_score_array)
    test_median = np.median(test_score_array)
    test_range = np.ptp(test_score_array)
    test_std = np.std(test_score_array)
    stats_dict = {
                'mean': int(test_mean),
                'median': int(test_median),
                'range':int(test_range),
                'std': int(test_std)
                }
            
    return stats_dict


    

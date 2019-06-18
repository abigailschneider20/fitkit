FitKit
A full-stack web application built in four weeks for a Hackbright Academy final project.

#Description FitKit allows users to import biometric data using the FitBit API and take standard personal health questionnaires (such as the Patient Health Questionnaire) to assess their mental health. Once all of the biometric and personal data is gathered, a user can view a graph of how their biometric data correlates with changes in their mental health status. FitKit also utilizes a logistic regression machine learning model to predict a user’s probability of suffering Depression, Anxiety, and Insomnia based off of their resting heart rate, sleep, and activity patterns.

Link to FitKit

Image of FitKit Homepage

#Technologies Used *FitBit API *Python3 *JSON *Jinja *PSQL *SQLAlchemy *Flask *JavaScript/jQuery *AJAX *HTML *CSS *BootStrap *Mockaroo *ChartJs

#**Features ** *Users can create an account and log into their account. Image of FitKit Login Form

*When logged in, a user is redirected to their user dashboard. Image of FitKit User Dashboard

*Users can take standard mental health tests: *Patient Health Questionnaire/PHQ9 for assessing Depression *Generalized Anxiety Disorder Test/GAD7 for assessing Anxiety *Insomnia Severity Index/ISI for assessing Insomnia Image of Example Test

*Users can import biometric data. *Due to the sensitive nature of FitBit health data, I was unable to access other individuals' FitBit data with the FitBit API, apart from my own. *To accommodate this, I created a Python script which generates user data to mimic the import of actual FitBit data. *This data is generated using the incidences of Anxiety (18%), Depression (8%), and Insomnia (25%) (as well as a 49% probability of being unaffected by one of these mental health conditions) within the United States. *When a new user registers and imports their data, one of the aforementioned "types" is assigned based on the probability of developing one of the respective mental health condition and biometric data and mental health test scores are synthesized for the specified date range.

Image of Import FitBit Data

*Once a user specifies the date range for their FitBit data, their data loads into the database and onto the results page. *A prediction is visible to the user which provides further insight into their mental health. *Based off of the number of steps, minutes of activity, minutes sedentary, minutes of sleep, and resting heart rate, a logistic regression model predicts whether or not an individual is likely to be affected by Anxiety, Depression, and/or Insomnia. *Based on the prediction generated off of the user's biometric data, the user is offered personalized recommendations to improve both their physical and mental health (as seen below). *The logistic regression machine learning models used were trained with 100+ users/approximately 30,000-50,000 data points.

Image of Prediction from FitBit Data

*Users can also view charts which show correlations between their biometric data and responses to mental health tests (using ChartJS).

Image of Chart

*Users can also view statistics for their selected metrics and mental health test scores. Image of Chart Stats

*Users are also able to access a BMI calculator. *This BMI calculator calculates a user's BMI and also provides further recommendations to improve their overall physical and mental health based on their overall BMI and the predictions generated from their FitBit data. Image of BMI Calculator

#Design *Designed using Bootstrap, CSS, and HTML elements. *Logo created by author using FreeLogoDesign *Photos from Unsplash

#Next Steps *Access FitBit API for other user accounts *Increase training data for logistic regression model *Expand number of attributes logistic regression model bases predictions off of *Provide more detailed personalized recommendations for users
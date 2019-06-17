from server import app
from unittest import TestCase
import doctest
import gen_user_data_assess_test

print(doctest.testmod(gen_user_data_assess_test))

def test_doctest():
    result=doctest.testmod(gen_user_data_assess_test)
    if results.failed:
        raise Exception(results)

class TestFlaskRoutes(TestCase):
    """Test Flask routes"""
    def setUp(self):
        """Initializes test client before every test"""
        self.client=app.test_client()
        app.config['TESTING']=True

    def test_index(self):
        """Ensure index route returns correct homepage HTML """

        #creates test client
        client = server.app.test_client()
        result = client.get('/') #uses test client to make requests
        #compares result data with assert method
        self.assertIn(b'<h1>Create a FitKit account today and live healthier now! </h1>', result.data)

    def test_login_form(self):
        """Ensure login route returns correct login form"""
        client=server.app.test_client()
        result=client.get('/login')
        self.assertIn(b' <h5>>Log In to FitKit</h5>')

    def test_login_user(self):
        """Tests that /login route processes login form data correctly """
        client = server.app.test_client()
        result= client.post('/login', data={'email': 'wgrono0@timesonline.co.uk', 
                                            'password': 'oXyNtOmj'},
                                            follow_redirects=True)
        self.assertIn(b' <h1> FitKit Data for Wallace </h1>', result.data)

    def test_registration_form(self):
        """Ensure registration route returns correct registration form"""
        client=server.app.test_client()
        result=client.get('/register')
        self.assertIn(b'<h5>Create an Account</h5>', result.data)

    def test_registration_user(self):
        """Ensures that /register route processes registration form correctly"""
        client=server.app.test_client()
        result=client.post('/register',data={'email': 'test@gmail.com',
                                            'f_name': 'test',
                                            'l_name': 'user',
                                            'age': '25',
                                            'sex': 'F',
                                            'password': 'pass_word'},
                                            follow_redirects=True)
        self.assertIn(b'<h2>HIPAA Compliance Patient Consent Form</h2>', result.data)

    def test_chartdata_form(self):
        """Ensures that chartdata route returns correct form"""
        client = server.app.test_client()
        result=client.get('/chartdata')
        self.assertIn(b'<div>Model Your FitBit Data</div>', result.data)


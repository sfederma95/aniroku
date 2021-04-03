from unittest import TestCase
from sqlalchemy import exc
from flask_bcrypt import Bcrypt

from models import db, connect_db, User, List, List_Entry, Comment, Category, Suggestion

SQLALCHEMY_DATABASE_URI = 'postgres:///anime-list-test'

from app import app

app.testing = True

bcrypt = Bcrypt()

db.drop_all()

app.config['WTF_CSRF_ENABLED'] = False
app.config['LOGIN_DISABLED'] = True

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)

class UserViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()
        cls.client = app.test_client()
        cls.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    avatar_url=None)
        cls.testuser_id = 1000
        cls.testuser.id = cls.testuser_id
        cls.u1 = User.signup("my_user1", "test1@test.com", "password", None)
        cls.u1_id = 2000
        cls.u1.id = cls.u1_id
        cls.u2 = User.signup("my_user2", "test2@test.com", "password", None)
        cls.u2_id = 3000
        cls.u2.id = cls.u2_id
        db.session.commit()
    
    def setUp(self):
        self.client = app.test_client()
        login(self.client, 'testuser', 'testuser')
        
    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_update_user(self):
        with self.client as c:
            resp = c.get('/users/1000/update')
            self.assertEqual(resp.status_code,200)
            self.assertIn("Update your info", str(resp.data))
            data = {'username':'testuser','password':'testuser','email':'newemail@yahoo.com','new_password':None,'avatar_url':None}
            resp2 = c.post(f"/users/1000/update", data=data)
            user = User.query.filter(User.id==1000).first()
            self.assertEqual(user.email,'newemail@yahoo.com')

    def test_update_invalid_user(self):
        logout(self.client)
        login(self.client, 'my_user1', 'password')
        with self.client as c:
            data = {'username':'testuser','password':'testuser','email':'newemail@yahoo.com','new_password':None,'avatar_url':None}
            resp = c.post(f"/users/1000/update", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login to your Aniroku account", str(resp.data))

    def test_update_user_taken_email(self):
        with self.client as c:
            data = {'username':'testuser','password':'testuser','email':'test1@test.com','new_password':None,'avatar_url':None}
            resp = c.post(f"/users/1000/update", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Update your info", str(resp.data))

    def test_update_user_bad_auth(self):
        with self.client as c:
            data = {'username':'testuser','password':'testuser1','email':'newemail@yahoo.com','new_password':None,'avatar_url':None}
            resp = c.post(f"/users/1000/update", data=data)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Update your info", str(resp.data))

    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/my-lists/1000")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome to your portal", str(resp.data))

    def test_user_show_invalid(self):
        logout(self.client)
        with self.client as c:
            resp = c.get(f"/my-lists/1000",follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login to your Aniroku account", str(resp.data))

    def test_view_user(self):
        logout(self.client)
        with self.client as c:
            resp = c.get('/1000/lists')
            self.assertEqual(resp.status_code,200)
            self.assertIn("View lists for: testuser", str(resp.data))

    def test_z_delete_user(self):
        with self.client as c:
            resp = c.get(f"/users/1000/delete")
            self.assertEqual(resp.status_code,200)
            self.assertIn("delete your account", str(resp.data))
            data = {'username':'testuser','password':'testuser'}
            resp2 = c.post(f"/users/1000/delete",data=data)
            user = User.query.filter(User.id==1000).first()
            self.assertIsNone(user)

    def test_delete_user_invalid(self):
        logout(self.client)
        login(self.client, 'my_user1', 'password')
        with self.client as c:
            data = {'username':'testuser','password':'testuser'}
            resp = c.post(f"/users/1000/delete",data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login to your Aniroku account", str(resp.data))

    def test_delete_user_bad_auth(self):
        with self.client as c:
            data = {'username':'testuser','password':'testuser1'}
            resp = c.post(f"/users/1000/delete",data=data)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("delete your account", str(resp.data))
            user = User.query.filter(User.id==1000).first()
            self.assertIsNotNone(user)

    def test_user_signup(self):
        logout(self.client)
        with self.client as c:
            data = {'username':'newuser','password':'password','email':'newuser@test.com','avatar_url':None}
            resp = c.post(f"/signup",data=data,follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome to your portal", str(resp.data))

    def test_user_signup_bad_username(self):
        logout(self.client)
        with self.client as c:
            data = {'username':'shit','password':'password','email':'newuser1@test.com','avatar_url':None}
            resp = c.post(f"/signup",data=data,follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Join Aniroku today", str(resp.data))

    def test_user_signup_taken_username(self):
        logout(self.client)
        with self.client as c:
            data = {'username':'testuser','password':'password','email':'newuser1@test.com','avatar_url':None}
            resp = c.post(f"/signup",data=data,follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Join Aniroku today", str(resp.data))

    def test_user_signup_taken_email(self):
        logout(self.client)
        with self.client as c:
            data = {'username':'newuser1','password':'password','email':'test1@test.com','avatar_url':None}
            resp = c.post(f"/signup",data=data,follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Join Aniroku today", str(resp.data))
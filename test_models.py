from unittest import TestCase
from sqlalchemy import exc
from flask_bcrypt import Bcrypt

from models import db, connect_db, User, List, List_Entry, Comment, Category, Suggestion

SQLALCHEMY_DATABASE_URI = 'postgres:///anime-list-test'

from app import app

bcrypt = Bcrypt()

class UserModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()
        tester = User.signup('tester','test@yahoo.com','password',None)
        tester.id =1000
        db.session.commit()
        my_tester = User.query.get(1000)
        self.my_tester = my_tester
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        user = User(email='test1@yahoo.com',username='tester2',password='password1',avatar_url=None)
        db.session.add(user)
        db.session.commit()
        self.assertEqual(len(user.user_lists),0)

    def test_taken_username(self):
        user = User.signup('tester','test2@yahoo.com','password',None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_taken_email(self):
        user = User.signup('tester2','test@yahoo.com','password',None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_valid_signup(self):
        user = User.signup('tester2','test2@yahoo.com','password',None)
        user.id = 100
        db.session.commit()
        found_user = User.query.get(100)
        self.assertIn(found_user,User.query.all())
        self.assertNotEqual(found_user.password,'password')
        self.assertNotEqual(found_user.password,self.my_tester.password)

    def test_invalid_authenticate(self):
        invalid_login = User.authenticate('tester','password1')
        hashed_pass = bcrypt.generate_password_hash('password').decode('UTF-8')
        invalid_login2 = User.authenticate('tester',hashed_pass)
        self.assertFalse(invalid_login)
        self.assertFalse(invalid_login2)

    def test_get_id(self):
        self.assertEqual(str(self.my_tester.id), self.my_tester.get_id())

class ListModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()
        tester = User.signup('tester','test@yahoo.com','password',None)
        tester.id =1000
        db.session.commit()
        my_tester = User.query.get(1000)
        self.my_tester = my_tester
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_list_model(self):
        lst = List(name='tester list',user_id=self.my_tester.id)
        lst.id = 100
        db.session.add(lst)
        db.session.commit()
        test_lst = List.query.get(100)
        self.assertEqual(len(test_lst.list_entries),0)
        self.assertEqual(len(test_lst.list_suggestions),0)
        self.assertEqual(test_lst.users.username,'tester')

    def test_duplicate_list_names(self):
        lst1=List(name='tester list',user_id=self.my_tester.id)
        db.session.add(lst1)
        db.session.commit()
        lst2=List(name='tester list',user_id=self.my_tester.id)
        db.session.add(lst2)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

class EntryModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()
        tester = User.signup('tester','test@yahoo.com','password',None)
        tester.id =1000
        db.session.commit()
        my_tester = User.query.get(1000)
        self.my_tester = my_tester
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_entry_model(self):
        lst = List(name='tester list',user_id=self.my_tester.id)
        lst.id = 100
        db.session.add(lst)
        db.session.commit()
        entry = List_Entry(list_id=100, anime_id=1,anime_title='anime',anime_img_url='google.com',anime_type='tv',anime_synopsis='once upon a time',anime_genres=['Action'])
        db.session.add(entry)
        db.session.commit()
        self.assertEqual(len(entry.entry_comments),0)
        self.assertEqual(entry.lists.name,'tester list')

    def test_duplicate_entries(self):
        lst = List(name='tester list',user_id=self.my_tester.id)
        lst.id = 100
        db.session.add(lst)
        db.session.commit()
        entry = List_Entry(list_id=100, anime_id=1,anime_title='anime',anime_img_url='google.com',anime_type='tv',anime_synopsis='once upon a time',anime_genres=['Action'])
        db.session.add(entry)
        db.session.commit()
        entry2 = List_Entry(list_id=100, anime_id=1,anime_title='anime2',anime_img_url='google.com2',anime_type='tv2',anime_synopsis='once upon a time2',anime_genres=['Action2'])
        db.session.add(entry2)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

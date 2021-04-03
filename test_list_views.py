from unittest import TestCase
from sqlalchemy import exc
from flask_bcrypt import Bcrypt
import time

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

class ListViewTestCase(TestCase):
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
        lst1 = List(name='list 1',description='coolest list ever',user_id=1000)
        lst2 = List(name='list 2',user_id=1000)
        lst3 = List(name='list 3',user_id=3000)
        lst1.id = 100
        db.session.add(lst1)
        db.session.add(lst2)
        db.session.add(lst3)
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

    def test_all_lists(self):
        logout(self.client)
        with self.client as c:
            resp=c.get('/lists')
            self.assertIn("testuser", str(resp.data))
            self.assertIn("my_user2", str(resp.data))
            self.assertIn("list 1", str(resp.data))
            self.assertIn("list 2", str(resp.data))

    def test_new_list(self):
        with self.client as c:
            resp = c.post(f"/lists/new/1000", data={"name": "test list"},follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            lst = List.query.filter(List.name == 'test list').first()
            self.assertEqual(lst.name, "test list")
            self.assertIn("Welcome to your portal", str(resp.data))

    def test_new_list_profanity(self):
        with self.client as c:
            resp = c.post(f"/lists/new/1000", data={"name": "shit"},follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Please avoid using profanity!", str(resp.data))

    def test_new_list_profanity(self):
        logout(self.client)
        login(self.client,'my_user1','password')
        with self.client as c:
            resp = c.post(f"/lists/new/1000", data={"name": "not my account"},follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Login to your Aniroku account", str(resp.data))

    def test_list_entry(self):
        with self.client as c:
            data = {'anime': 1, 'rating': 1}
            resp = c.post(f"/lists/100/add?q=cowboy", data=data,follow_redirects=True)
            data2 = {'anime': 20, 'rating': 1}
            resp2 = c.post(f"/lists/100/add?q=naruto", data=data2,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            time.sleep(2)
            entry = List_Entry.query.filter(List_Entry.anime_id == 1).first()
            self.assertEqual(entry.rating, 1)
            resp2=c.get('/lists/100')
            self.assertIn('Cowboy Bebop',str(resp2.data))

    def test_list_entry_invalid_user(self):
        logout(self.client)
        login(self.client,'my_user1','password')
        with self.client as c:
            data = {'anime': 1, 'rating': 1}
            resp = c.post(f"/lists/100/add?q=cowboy", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Login to your Aniroku account", str(resp.data))

    def test_display_list(self):
        with self.client as c:
            resp=c.get('/lists/100')
            self.assertEqual(resp.status_code,200)
            self.assertIn("list 1", str(resp.data))
            self.assertIn("Inbox", str(resp.data))

    def test_update_list(self):
        with self.client as c:
            resp = c.post(f"/lists/100/update", data={'name':'updated list'},follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("updated list", str(resp.data))
            self.assertIn("Inbox", str(resp.data))

    def test_update_list_profanity(self):
        with self.client as c:
            resp = c.post(f"/lists/100/update", data={'name':'shit'},follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Please avoid using profanity!", str(resp.data))

    def test_update_entry(self):
        with self.client as c:
            entry = List_Entry.query.filter(List_Entry.anime_id == 20).first()
            resp = c.post(f"/100/{entry.id}/update", data={'rating': 2},follow_redirects=True)
            entry2 = List_Entry.query.filter(List_Entry.anime_id == 20).first()
            self.assertEqual(entry2.rating, 2)

    def test_remove_entry_valid_user(self):
        with self.client as c:
            entry = List_Entry.query.filter(List_Entry.anime_id == 1).first()
            resp = c.post(f'/100/{entry.id}/remove',follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("list 1", str(resp.data))
            self.assertNotIn('Cowboy Bebop',str(resp.data))

    def test_remove_entry_invalid_user(self):
        logout(self.client)
        login(self.client,'my_user1','password')
        with self.client as c:
            entry = List_Entry.query.filter(List_Entry.anime_id == 1).first()
            resp = c.post(f'/100/{entry.id}/remove',follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Login to your Aniroku account", str(resp.data))

    def test_delete_list_valid_user(self):
        with self.client as c:
            lst = List.query.filter(List.name == 'list 2').first()
            resp = c.post(f'/lists/{lst.id}/delete',follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertNotIn('list 2',str(resp.data))

    def test_delete_list_invalid_user(self):
        logout(self.client)
        login(self.client,'my_user1','password')
        with self.client as c:
            lst = List.query.filter(List.name == 'list 2').first()
            resp = c.post(f'/lists/{lst.id}/delete',follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Login to your Aniroku account", str(resp.data))

    def test_display_genres(self):
        logout(self.client)
        with self.client as c:
            resp=c.get('/genres')
            self.assertEqual(resp.status_code,200)
            self.assertIn("Action", str(resp.data))
    
    def test_unknown_user_genre_post(self):
        logout(self.client)
        with self.client as c:
            resp=c.get('/genres/1')
            self.assertEqual(resp.status_code,200)
            self.assertIn("Action Anime", str(resp.data))
            data = {'anime': 16498, 'list_id': 100}
            resp2 = c.post("/genres/1", data=data,follow_redirects=True)
            self.assertEqual(resp2.status_code,200)
            self.assertIn("Login", str(resp2.data))

    def test_logged_in_user_genre_post(self):
        # must be a real anime that would be listed on that page
        with self.client as c:
            resp=c.get('/genres/1')
            self.assertEqual(resp.status_code,200)
            self.assertIn("Action Anime", str(resp.data))
            data = {'anime': 16498, 'list_id': 100}
            resp2 = c.post("/genres/1", data=data)
            time.sleep(2)
            entry = List_Entry.query.filter(List_Entry.anime_id == 16498).first()
            self.assertEqual(entry.anime_title, 'Shingeki no Kyojin')

    def test_logged_in_user_post_recommended(self):
        # must be a real anime that would be listed on that page
        with self.client as c:
            resp=c.get('/16498/recommendations')
            self.assertEqual(resp.status_code,200)
            self.assertIn("Recommended based on", str(resp.data))
            data = {'anime': 1818, 'list_id': 100}
            resp2 = c.post("/16498/recommendations", data=data)
            time.sleep(2)
            entry = List_Entry.query.filter(List_Entry.anime_id == 1818).first()
            self.assertEqual(entry.anime_title, 'Claymore')

    def test_unknown_user_post_recommended(self):
        logout(self.client)
        with self.client as c:
            resp=c.get('/16498/recommendations')
            time.sleep(1)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Recommended based on", str(resp.data))
            data = {'anime': 1818, 'list_id': 100}
            resp2 = c.post("/16498/recommendations", data=data)
            self.assertEqual(resp2.status_code,200)
            self.assertIn("Login", str(resp2.data))

    def test_category_create(self):
        with self.client as c:
            resp = c.post(f"/category/new", data={"name": "cute"},follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            cat = Category.query.filter(Category.name == 'Cute').first()
            self.assertEqual(cat.name, "Cute")
            self.assertIn("Welcome to your portal", str(resp.data))

    def test_category_create_profanity(self):
        with self.client as c:
            resp = c.post(f"/category/new", data={"name": "shit"},follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Please avoid using profanity!", str(resp.data))

    def test_category_create_already_exists(self):
        with self.client as c:
            resp = c.post(f"/category/new", data={"name": "cute"},follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("This category already exists!", str(resp.data))

    def test_send_suggestion(self):
        logout(self.client)
        login(self.client, 'my_user1', 'password')
        with self.client as c:
            data = {'anime': 1, 'comment': 'test comment'}
            resp = c.post(f"/100/suggestions?q=cowboy", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            suggestion = Suggestion.query.filter(Suggestion.anime_id == 1).first()
            self.assertEqual(suggestion.anime_title, 'Cowboy Bebop')
        logout(self.client)

    def test_send_suggestion_profanity(self):
        logout(self.client)
        login(self.client, 'my_user1', 'password')
        with self.client as c:
            data = {'anime': 1, 'comment': 'shit'}
            resp = c.post(f"/100/suggestions?q=cowboy", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Please avoid using profanity!", str(resp.data))
        logout(self.client)

    def test_send_suggestion_invalid_user(self):
        logout(self.client)
        with self.client as c:
            data = {'anime': 20, 'comment': 'test comment'}
            resp = c.post(f"/100/suggestions?q=cowboy", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Please login to make suggestions.", str(resp.data))
            suggestion = Suggestion.query.filter(Suggestion.anime_id == 20).first()
            self.assertIsNone(suggestion)

    def test_suggestion_inbox_valid_user(self):
        with self.client as c:
            resp=c.get('/100/suggestion-inbox')
            self.assertEqual(resp.status_code,200)
            self.assertIn("Cowboy Bebop", str(resp.data))
            self.assertIn("test comment", str(resp.data))
            suggestion = Suggestion.query.filter(Suggestion.anime_id == 1).first()
            data = {'anime-id': 1, 'list-id': 100}
            resp = c.post(f"/suggestions/{suggestion.id}/add-to-list", data=data)
            self.assertEqual(resp.status_code,302)
            self.assertEqual([],Suggestion.query.all())

    def test_suggestion_inbox_invalid_user(self):
        logout(self.client)
        login(self.client, 'my_user1', 'password')
        with self.client as c:
            suggestion = Suggestion.query.filter(Suggestion.anime_id == 1).first()
            data = {'anime-id': 1, 'list-id': 100}
            resp = c.post(f"/suggestions/{suggestion.id}/add-to-list", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Login to your Aniroku account", str(resp.data))

    def test_delete_suggestion(self):
        logout(self.client)
        login(self.client, 'my_user1', 'password')
        with self.client as c:
            data = {'anime': 20, 'comment': 'test comment'}
            resp = c.post(f"/100/suggestions?q=naruto", data=data,follow_redirects=True)
            suggestion = Suggestion.query.filter(Suggestion.anime_id == 20).first()
            self.assertIsNotNone(suggestion)
        logout(self.client)
        login(self.client, 'testuser','testuser')
        with self.client as c:
            suggestion = Suggestion.query.filter(Suggestion.anime_id == 20).first()
            resp2 = c.post(f"/suggestions/{suggestion.id}/remove")
            removed_suggestion = Suggestion.query.filter(Suggestion.anime_id == 20).first()
            self.assertIsNone(removed_suggestion)

    def test_post_comment(self):
        with self.client as c:
            entry = List_Entry.query.filter(List_Entry.anime_title=='Claymore').first()
            data = {'comment':'test comment','spoiler':False}
            resp = c.post(f"/100/{entry.id}/add-comment", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("test comment", str(resp.data))

    def test_post_comment_profanity(self):
        with self.client as c:
            entry = List_Entry.query.filter(List_Entry.anime_title=='Claymore').first()
            data = {'comment':'shit','spoiler':False}
            resp = c.post(f"/100/{entry.id}/add-comment", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Please avoid using profanity!", str(resp.data))

    def test_post_comment_invalid_user(self):
        logout(self.client)
        with self.client as c:
            entry = List_Entry.query.filter(List_Entry.anime_title=='Claymore').first()
            data = {'comment':'new comment','spoiler':False}
            resp = c.post(f"/100/{entry.id}/add-comment", data=data,follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            self.assertIn("Please login to comment.", str(resp.data))
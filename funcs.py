from flask import Blueprint, current_app, flash
import requests
from flask_mail import Mail, Message
from threading import Thread
from models import List_Entry, Suggestion, User
from flask_sqlalchemy import SQLAlchemy
from random import choice 
from genres import jikan_genres

app_funcs = Blueprint('app_funcs',__name__)

db = SQLAlchemy()
mail = Mail()

def get_anime_info(num):
    resp = requests.get(f'https://api.jikan.moe/v3/anime/{num}/')
    anime_by_id = resp.json()
    genres = [g['name'] for g in anime_by_id['genres']]
    anime_info = {
        'anime_id':num, 'anime_title':anime_by_id['title'],'anime_img_url':anime_by_id['image_url'], 'anime_type':anime_by_id['type'], 'anime_genres':genres, 'anime_synopsis':anime_by_id['synopsis']
    }
    return anime_info

def category_genre_picker(set1,set2):
    if set1 == []:
        q='generic'
    else:
        q=choice(set1)
    if set2 == []:
        set2 = ['Action']
    resp = requests.get(f'https://api.jikan.moe/v3/search/anime?q={q}&genre={jikan_genres[choice(set2)]},{jikan_genres[choice(set2)]},{jikan_genres[choice(set2)]}&genre_exclude=0&limit=5')
    anime_resp = resp.json()
    anime_lst = anime_resp['results']
    return anime_lst

def byRating(el):
    return el.rating

def standardize(string):
    new_string = string.lower()
    new_string=new_string.capitalize()
    return new_string

def send_async_email(app, msg):
    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure/page/2
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, text_body, html_body=None):
    msg = Message(subject, sender='aniroku.app@gmail.com', recipients=[recipients])
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def make_list_entry(anime_id,list_id,rating,categories):
    if categories==['None']:
        categories = []
    else:
        categories = categories
    entry = List_Entry(list_id=list_id, anime_id=anime_id,
                           rating=rating or 0, anime_title=None,
                           anime_img_url=None,anime_type=None,
                           anime_genres=None, categories=categories, anime_synopsis=None)
    Thread(target=submit_list_entry, args=(anime_id,current_app._get_current_object(),entry)).start()

def submit_list_entry(anime_id,app,entry):
    with app.app_context():
        anime_info = get_anime_info(anime_id)
        entry.anime_synopsis = anime_info['anime_synopsis']
        entry.anime_title=anime_info['anime_title']         
        entry.anime_img_url=anime_info['anime_img_url']
        entry.anime_type=anime_info['anime_type']
        entry.anime_genres=anime_info['anime_genres']
        db.session.add(entry)
        db.session.commit()

def send_anime_recommendation(anime_lst, anime_id, comment, username, curr_list):
    anime_by_id = next(item for item in anime_lst['results'] if item['mal_id'] == anime_id)
    suggestion=Suggestion(list_id=curr_list.id,anime_id=anime_id,
    anime_title=anime_by_id['title'],mal_url=anime_by_id['url'],
    comment=comment or 'No comment from suggester.', username=username)
    db.session.add(suggestion)
    db.session.commit()

def invalid_signup(username_data,email_data):
    if User.query.filter(User.username == username_data).first() and User.query.filter(User.email == email_data).first():
        flash("Username already taken", 'danger')
        flash("Email is associated with another account", 'danger')
    elif User.query.filter(User.email == email_data).first():
        flash("Email is associated with another account", 'danger')
    else:
        flash("Username already taken", 'danger')
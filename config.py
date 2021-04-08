import os
from secrets import my_secret, username, password, my_database

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',my_database)

SQLALCHEMY_TRACK_MODIFICATIONS= False
SQLALCHEMY_ECHO = False
DEBUG_TB_INTERCEPT_REDIRECTS= False
SECRET_KEY = os.environ.get('SECRET_KEY',my_secret)

DEBUG = True
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', username)
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', password)

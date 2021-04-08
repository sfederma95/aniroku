import os
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql:///anime-lists')

SQLALCHEMY_TRACK_MODIFICATIONS= False
SQLALCHEMY_ECHO = False
DEBUG_TB_INTERCEPT_REDIRECTS= False
SECRET_KEY = os.environ.get('SECRET_KEY','default')

DEBUG = True
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'default')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'default')

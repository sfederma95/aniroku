from secrets import SECRET_KEY, DATABASE_URL, MAIL_PASSWORD, MAIL_USERNAME

SQLALCHEMY_DATABASE_URI = DATABASE_URL

SQLALCHEMY_TRACK_MODIFICATIONS= False
SQLALCHEMY_ECHO = False
DEBUG_TB_INTERCEPT_REDIRECTS= False
SECRET_KEY = SECRET_KEY

DEBUG = True
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = MAIL_USERNAME
MAIL_PASSWORD = MAIL_PASSWORD

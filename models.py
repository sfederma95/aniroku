from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    avatar_url = db.Column(db.Text, default='/static/images/default_user.png')
    user_lists = db.relationship('List', backref='users',cascade="all, delete-orphan")

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_aunonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @classmethod
    def signup(cls, username, email, password, avatar_url):
        hashed_pass = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(username=username, email=email,
                    password=hashed_pass, avatar_url=avatar_url)
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False


class List(db.Model):
    __tablename__ = 'lists'
    __table_args__ = (db.UniqueConstraint('name', 'user_id'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), nullable=False)
    list_entries = db.relationship('List_Entry', backref='lists',cascade="all, delete-orphan")
    list_suggestions = db.relationship('Suggestion', backref='lists',cascade="all, delete-orphan")


class List_Entry(db.Model):
    __tablename__ = 'entries'
    __table_args__ = (db.UniqueConstraint('list_id', 'anime_id'),)
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'lists.id', ondelete='cascade'), nullable=False)
    anime_id = db.Column(db.Integer, nullable=False)
    anime_title = db.Column(db.Text, nullable=False)
    anime_img_url = db.Column(db.Text, nullable=False)
    anime_type = db.Column(db.Text, nullable=False)
    anime_genres = db.Column(db.ARRAY(db.String),nullable=False)
    categories = db.Column(db.ARRAY(db.String),nullable=True)
    rating = db.Column(db.Integer)
    entry_comments = db.relationship('Comment', backref='entries',cascade="all, delete-orphan")

class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey(
        'entries.id', ondelete='cascade'), nullable=False)
    entry_owner = db.Column(db.Boolean, nullable=False)
    text = db.Column(db.Text,nullable=False, default='No comment by owner.')
    username = db.Column(db.Text, db.ForeignKey(
        'users.username',ondelete='SET NULL'), nullable=True)

class Category(db.Model):
    __tablename__='categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

class Suggestion(db.Model):
    __tablename__='suggestions'
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'lists.id', ondelete='cascade'), nullable=False)
    anime_id = db.Column(db.Integer, nullable=False)
    anime_title = db.Column(db.Text, nullable=False)
    mal_url = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text,nullable=True)
    username = db.Column(db.Text, db.ForeignKey(
        'users.username',ondelete='SET NULL'), nullable=True)




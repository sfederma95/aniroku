
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, URL, Optional, NumberRange


class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=6), Length(max=20)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    avatar_url = StringField('(Optional) Avatar URL',
                             validators=[URL(), Optional()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class ListForm(FlaskForm):
    name = StringField(
        'Name of list', validators=[DataRequired(), Length(min=3), Length(max=20)])
    description = TextAreaField('Description text', validators=[
                                Optional(), Length(max=80)])


class ListUpdateForm(FlaskForm):
    name = StringField(
        'Update name for this list', validators=[Optional(), Length(min=3), Length(max=20)])
    description = TextAreaField('Update description for this list', validators=[
                                Optional(), Length(max=80)])


class AnimeEntryForm(FlaskForm):
    anime = SelectField('Title', coerce=int)
    rating = IntegerField('Rating', validators=[
                          Optional(), NumberRange(min=1, max=10)])
    categories =SelectMultipleField('Categories', coerce=str)

class CategoryForm(FlaskForm):
    name = StringField('Name for this category', validators=[
                           DataRequired(), Length(min=3), Length(max=15)])

class SuggestionForm(FlaskForm):
    anime = SelectField('Anime to be recommended', coerce=int)
    comment = TextAreaField('Why do you recommend this anime?', validators=[
                             Optional(), Length(max=80)])

class DeleteUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired()])
    password = PasswordField('Current Password', validators=[
                             DataRequired()])
    new_password = PasswordField('New Password', validators=[
                             Optional(),Length(min=6)])
    email = StringField('Your new e-mail', validators=[Optional(), Email()])
    avatar_url = StringField('Your new avatar URL',
                             validators=[URL(), Optional()])

class AddAnimeForm(FlaskForm):
    anime = SelectField('Anime to be added', coerce=int)
    list_id = SelectField('List to be added to', coerce=int)


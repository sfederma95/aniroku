from secrets import SECRET_KEY, DATABASE_URL
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from flask_bcrypt import Bcrypt
from genres import jikan_genres
from funcs import get_anime_info, byRating, standardize
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect

from forms import NewUserForm, LoginForm, ListForm, ListUpdateForm, AnimeEntryForm, CategoryForm, SuggestionForm, DeleteUserForm, UpdateUserForm
from models import db, connect_db, User, List, List_Entry, Comment, Category, Suggestion

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
toolbar = DebugToolbarExtension(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt()
connect_db(app)
# db.drop_all()
db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def homepage():
    return render_template('home.html')


@app.route('/lists')
def show_lists():
    lists = List.query.all()
    return render_template('all-lists.html', lists=lists)


@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    form = NewUserForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                avatar_url=form.avatar_url.data or User.avatar_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            flash("Email is associated with another account", 'danger')
            return render_template('signup.html', form=form)

        login_user(user)
        return redirect(f"/my-lists/{user.id}")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user)
            return redirect(f'/my-lists/{user.id}')
        flash("Invalid credentials.", 'danger')
    return render_template('login.html', form=form)


@ app.route('/my-lists/<user_id>')
@ login_required
def user_portal(user_id):
    user = User.query.get_or_404(user_id)
    if current_user != user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    return render_template('portal.html', user=user)


@app.route('/lists/new/<user_id>', methods=['GET', 'POST'])
@login_required
def create_list(user_id):
    user = User.query.get_or_404(user_id)
    if current_user != user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    form = ListForm()
    if form.validate_on_submit():
        try:
            new_list = List(name=form.name.data,
                        description=form.description.data, user_id=user.id)
            db.session.add(new_list)
            db.session.commit()
            return redirect(f"/my-lists/{user.id}")
        except IntegrityError:
            db.session.rollback()
            flash("You already have a list with this name!", "danger")
    return render_template('new-list.html', form=form)


@app.route('/lists/<list_id>')
def show_list(list_id):
    curr_list = List.query.get_or_404(list_id)
    curr_list.list_entries.sort(key=byRating,reverse=True)
    genres = jikan_genres
    categories = set()
    all_categories = Category.query.all()
    for entry in curr_list.list_entries:
        if entry.categories:
            for category in entry.categories:
                categories.add(category)
    return render_template('show-list.html', curr_list=curr_list, genres=genres,categories=categories,all_categories=all_categories)

@app.route('/lists/<list_id>/update',methods=['GET','POST'])
@login_required
def update_list(list_id):
    curr_list = List.query.get_or_404(list_id)
    if current_user.id != curr_list.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    form = ListUpdateForm()
    if form.validate_on_submit():
        try:
            curr_list.name = form.name.data or curr_list.name
            curr_list.description = form.description.data or curr_list.description
            db.session.add(curr_list)
            db.session.commit()
            return redirect(f'/lists/{curr_list.id}')
        except:
            db.session.rollback()
            flash("You already have a list with this name!", "danger")
    return render_template('update-list.html', form=form)

@app.route('/lists/<list_id>/add', methods=['GET', 'POST'])
@login_required
def add_to_list(list_id):
    curr_list = List.query.get_or_404(list_id)
    if current_user.id != curr_list.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    search = request.args.get('q')
    form = AnimeEntryForm()
    form.categories.choices = [(c.name, c.name)
                              for c in Category.query.all()]
    if not search:
        anime=None
    else:
        resp = requests.get(
            f'https://api.jikan.moe/v3/search/anime?q={search}&limit=8')
        anime = resp.json()
        form.anime.choices = [(a['mal_id'], a['title'])
                              for a in anime['results']]
    if form.validate_on_submit():
        anime_info = get_anime_info(form.anime.data)
        try:
            entry = List_Entry(list_id=curr_list.id, anime_id=form.anime.data,
                           rating=form.rating.data or 0, anime_title=anime_info['anime_title'],
                           anime_img_url=anime_info['anime_img_url'],anime_type=anime_info['anime_type'],
                           anime_genres=anime_info['anime_genres'], categories=form.categories.data)
            db.session.add(entry)
            db.session.commit()
            comment = Comment(entry_id=entry.id, entry_owner=True, text=form.comments.data or 'No comment by owner.', username=curr_list.users.username)
            db.session.add(comment)
            db.session.commit()
            return redirect(f'/lists/{curr_list.id}/add')
        except IntegrityError:
            db.session.rollback()
            flash("This anime is already on your list!", "danger")
    return render_template('list-addition.html', form=form, curr_list=curr_list, anime=anime)

@app.route('/<list_id>/<entry_id>/remove',methods=['POST'])
@login_required
def remove_from_list(list_id,entry_id):
    curr_list = List.query.get_or_404(list_id)
    entry = List_Entry.query.get_or_404(entry_id)
    if current_user.id != curr_list.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    db.session.delete(entry)
    db.session.commit()
    return redirect(f'/lists/{curr_list.id}')

@app.route('/<list_id>/<entry_id>/update',methods=['POST'])
@login_required
def update_entry(list_id,entry_id):
    # https://stackoverflow.com/questions/63851329/how-to-add-csrf-to-flask-app-without-wtforms
    curr_list = List.query.get_or_404(list_id)
    entry = List_Entry.query.get_or_404(entry_id)
    if current_user.id != curr_list.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    entry.categories = request.form.getlist('categories') or None
    entry.rating = request.form['rating'] or entry.rating
    db.session.add(entry)
    db.session.commit()
    return redirect(f'/lists/{curr_list.id}')

@app.route('/lists/<list_id>/delete',methods=['POST'])
@login_required
def delete_list(list_id):
    curr_list = List.query.get_or_404(list_id)
    if current_user.id != curr_list.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    db.session.delete(curr_list)
    db.session.commit()
    return redirect(f'/my-lists/{curr_list.users.id}')

@app.route('/genres')
def get_all_genres():
    genres = jikan_genres
    return render_template('all-genres.html',genres=genres)

@app.route('/genres/<genre_id>')
def get_genre_by_id(genre_id):
    resp = requests.get(f'https://api.jikan.moe/v3/genre/anime/{genre_id}')
    anime_genre = resp.json()
    return render_template('show-genre.html',anime_genre=anime_genre)

@app.route('/<anime_id>/recommendations')
def get_recommendations(anime_id):
    resp = requests.get(f'https://api.jikan.moe/v3/anime/{anime_id}/recommendations')
    recommendations = resp.json()
    return render_template('show-recommended.html',recommendations=recommendations)

@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CategoryForm()
    categories = Category.query.all()
    if form.validate_on_submit():
        try:
            category_name=standardize(form.name.data)
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()
            return redirect(f"/my-lists/{current_user.id}")
        except IntegrityError:
            db.session.rollback()
            flash("This category already exists!", "danger")
    return render_template('new-category.html', form=form, categories=categories)

@app.route('/<list_id>/suggestions', methods=['GET','POST'])
@login_required
def make_suggestion(list_id):
    curr_list = List.query.get_or_404(list_id)
    if current_user.id == curr_list.users.id:
        flash("Recommending an anime to yourself?", "warning")
        return redirect(f"/lists/{curr_list.id}")
    search = request.args.get('q')
    form=SuggestionForm()
    if not search:
        anime=None
    else:
        resp = requests.get(
            f'https://api.jikan.moe/v3/search/anime?q={search}&limit=8')
        anime = resp.json()
        form.anime.choices = [(a['mal_id'], a['title'])
                              for a in anime['results']]
    if form.validate_on_submit():
        resp2 = requests.get(f'https://api.jikan.moe/v3/anime/{form.anime.data}/')
        anime_by_id = resp2.json()
        suggestion=Suggestion(list_id=curr_list.id,anime_id=form.anime.data,
        anime_title=anime_by_id['title'],mal_url=anime_by_id['url'],
        comment=form.comment.data or 'No comment from suggester.', username=current_user.username)
        db.session.add(suggestion)
        db.session.commit()
        return redirect(f'/lists/{curr_list.id}')
    return render_template('suggest-form.html',form=form,curr_list=curr_list,anime=anime)

@app.route('/<list_id>/suggestion-inbox')
@login_required
def suggestion_inbox(list_id):
    curr_list = List.query.get_or_404(list_id)
    if current_user.id != curr_list.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    return render_template('suggestion-inbox.html',curr_list=curr_list)

@ app.route('/<user_id>/lists')
def view_users(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('show-user.html', user=user)

@app.route('/suggestions/<suggestion_id>/remove',methods=['POST'])
@login_required
def delete_suggestion(suggestion_id):
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    if current_user.id != suggestion.lists.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    db.session.delete(suggestion)
    db.session.commit()
    return redirect(f'/{suggestion.lists.id}/suggestion-inbox')

@app.route('/<list_id>/<entry_id>/add-comment',methods=['POST'])
@login_required
def new_comment(list_id,entry_id):
    # https://stackoverflow.com/questions/63851329/how-to-add-csrf-to-flask-app-without-wtforms
    curr_list = List.query.get_or_404(list_id)
    entry = List_Entry.query.get_or_404(entry_id)
    comment_data = request.form['comment']
    if current_user.id == curr_list.users.id:
        entry_owner = True
    else:
        entry_owner = False
    comment = Comment(entry_id=entry.id,text=comment_data,username=current_user.username,entry_owner=entry_owner)
    db.session.add(comment)
    db.session.commit()
    return redirect(f'/lists/{curr_list.id}')

@app.route('/users/<user_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    curr_user=User.query.get_or_404(user_id)
    if current_user.id != curr_user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    form = DeleteUserForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            db.session.delete(user)
            db.session.commit()
            logout_user()
            return redirect('/')
        flash("Invalid credentials.", 'danger')
    return render_template('delete-user.html', form=form)

@app.route('/users/<user_id>/update', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    curr_user=User.query.get_or_404(user_id)
    if current_user.id != curr_user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    form = UpdateUserForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            curr_user.avatar_url = form.avatar_url.data or curr_user.avatar_url
            curr_user.email = form.email.data or curr_user.email
            if form.new_password.data:
                hashed_pass = bcrypt.generate_password_hash(form.new_password.data).decode('UTF-8')
                curr_user.password = hashed_pass or curr_user.password
            db.session.add(curr_user)
            db.session.commit()
            return redirect(f'/my-lists/{curr_user.id}')
        flash("Invalid credentials.", 'danger')
    return render_template('update-user.html', form=form)

@ app.route("/logout")
@ login_required
def logout():
    logout_user()
    return redirect('/')

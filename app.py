from flask import Flask, render_template, request, flash, redirect, session, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from flask_bcrypt import Bcrypt
from genres import jikan_genres
from funcs import get_anime_info, byRating, standardize, send_email, make_list_entry, send_anime_recommendation, invalid_signup, category_genre_picker
from funcs import app_funcs
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from profanity_filter import ProfanityFilter
import spacy
from flask_mail import Mail, Message
from sqlalchemy import and_
from ratings import one_star, half_star, no_star, ratings_dict

from forms import NewUserForm, LoginForm, ListForm, ListUpdateForm, AnimeEntryForm, CategoryForm, SuggestionForm, DeleteUserForm, UpdateUserForm, AddAnimeForm
from models import db, connect_db, User, List, List_Entry, Comment, Category, Suggestion

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.register_blueprint(app_funcs)

mail=Mail(app)

toolbar = DebugToolbarExtension(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt()
connect_db(app)
# db.drop_all()
db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

pf = ProfanityFilter()
nlp = spacy.load('en')
profanity_filter = ProfanityFilter(nlps={'en': nlp})  
nlp.add_pipe(profanity_filter.spacy_component, last=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def homepage():
    recent_picks = List_Entry.query.order_by(List_Entry.id.desc()).limit(10).all()
    comments = Comment.query.order_by(Comment.id.desc()).limit(5).all()
    return render_template('home.html', recent_picks=recent_picks, comments=comments)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/<user_id>/my-recommendations')
@login_required
def my_recommended_pg(user_id):
    user = User.query.get_or_404(user_id)
    if current_user != user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    get_categories = set()
    get_genres = set()
    for lst in current_user.user_lists:
        for entry in lst.list_entries:
            if entry.rating >= 9:
                for genre in entry.anime_genres:
                    get_genres.add(genre)
                if entry.categories == None:
                        get_categories = []
                else:
                    for category in entry.categories:
                        get_categories.add(category)
    anime_lst = category_genre_picker(list(get_categories),list(get_genres))
    return render_template('my-interests.html',anime_lst=anime_lst)

@app.route('/lists')
def show_lists():
    lists = List.query.all()
    return render_template('all-lists.html', lists=lists)


@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    form = NewUserForm()
    if form.validate_on_submit():
        if pf.is_profane(form.username.data) == True:
            flash('Please avoid using profanity!','danger')
        else:
            try:
                user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                avatar_url=form.avatar_url.data or User.avatar_url.default.arg,
            )
                db.session.commit()
                login_user(user)
                return redirect(f"/my-lists/{user.id}")
            except IntegrityError:
                db.session.rollback()
                invalid_signup(form.username.data,form.email.data)
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
    comment_occur_lst = []
    for lst in user.user_lists:
        total=0
        for entry in lst.list_entries:
            for comment in entry.entry_comments:
                total+=1
        comment_occur_lst.append(total)
    if current_user != user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    return render_template('portal.html', user=user, comment_occur_lst=comment_occur_lst)


@app.route('/lists/new/<user_id>', methods=['GET', 'POST'])
@login_required
def create_list(user_id):
    user = User.query.get_or_404(user_id)
    if current_user != user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    form = ListForm()
    if form.validate_on_submit():
        if pf.is_profane(form.name.data) == True:
            flash('Please avoid using profanity!','danger')
        else:
            try:
                new_list = List(name=form.name.data,
                        description=form.description.data, user_id=user.id)
                db.session.add(new_list)
                db.session.commit()
                flash("List created successfully!", "success")
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
    ratings = ratings_dict
    for entry in curr_list.list_entries:
        if entry.categories:
            for category in entry.categories:
                categories.add(category)
    return render_template('show-list.html', curr_list=curr_list, genres=genres,categories=categories,all_categories=all_categories, ratings=ratings)

@app.route('/lists/<list_id>/update',methods=['GET','POST'])
@login_required
def update_list(list_id):
    curr_list = List.query.get_or_404(list_id)
    if current_user.id != curr_list.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    form = ListUpdateForm()
    if form.validate_on_submit():
        if pf.is_profane(form.name.data) == True:
            flash('Please avoid using profanity!','danger')
        else:
            try:
                curr_list.name = form.name.data or curr_list.name
                curr_list.description = form.description.data or curr_list.description
                db.session.add(curr_list)
                db.session.commit()
                flash("Your list was updated successfully!", "success")
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
                              for c in Category.query.all()] or [('None','None')]
    if not search:
        anime=None
    else:
        resp = requests.get(
            f'https://api.jikan.moe/v3/search/anime?q={search}&limit=8')
        anime = resp.json()
        form.anime.choices = [(a['mal_id'], a['title'])
                              for a in anime['results']]
    if form.validate_on_submit():
        already_on_list = List_Entry.query.filter(and_(List_Entry.anime_id==form.anime.data, List_Entry.list_id==curr_list.id)).first()
        if already_on_list:
            flash("This anime is already on your list!", "danger")
        else:
            make_list_entry(form.anime.data,curr_list.id,form.rating.data,form.categories.data)
            flash("This anime has been added to your list!", "success")
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
    flash("This title was removed from your list!", "success")
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
    flash("Your entry has been updated!", "success")
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
    flash("Your list was deleted successfully!", "success")
    return redirect(f'/my-lists/{curr_list.users.id}')

@app.route('/genres')
def get_all_genres():
    genres = jikan_genres
    g1 = dict(list(genres.items())[:14])
    g2 = dict(list(genres.items())[15:29])
    g3 = dict(list(genres.items())[30:])
    return render_template('all-genres.html',g1=g1,g2=g2,g3=g3)

@app.route('/genres/<genre_id>', methods=['GET','POST'])
def get_genre_by_id(genre_id):
    form = AddAnimeForm()
    resp = requests.get(f'https://api.jikan.moe/v3/genre/anime/{genre_id}')
    anime_genre = resp.json()
    if current_user.get_id()!=None:
        form.anime.choices = [(a['mal_id'], a['title'])
                              for a in anime_genre['anime'][:20]]
        form.list_id.choices=[(l.id,l.name) for l in current_user.user_lists]
    if form.validate_on_submit():
        curr_list = List.query.get_or_404(form.list_id.data)
        if current_user.id != curr_list.users.id:
            flash("Access unauthorized.", "danger")
            return redirect("/login")
        already_on_list = List_Entry.query.filter(and_(List_Entry.anime_id==form.anime.data, List_Entry.list_id==curr_list.id)).first()
        if already_on_list:
            flash("This anime is already on your list!", "danger")
        else:
            make_list_entry(form.anime.data,curr_list.id,rating=0,categories=None)
            flash("This anime has been added to your list!", "success")
    return render_template('show-genre.html',anime_genre=anime_genre, form=form)

@app.route('/<anime_id>/recommendations', methods=['GET','POST'])
def get_recommendations(anime_id):
    form = AddAnimeForm()
    resp = requests.get(f'https://api.jikan.moe/v3/anime/{anime_id}/recommendations')
    recommendations = resp.json()
    if recommendations["recommendations"] == []:
        abort(404)
    curr_title = request.args.get('t')
    if current_user.get_id()!=None:
        form.anime.choices = [(a['mal_id'], a['title'])
                              for a in recommendations['recommendations']]
        form.list_id.choices=[(l.id,l.name) for l in current_user.user_lists]
    if form.validate_on_submit():
        curr_list = List.query.get_or_404(form.list_id.data)
        if current_user.id != curr_list.users.id:
            flash("Access unauthorized.", "danger")
            return redirect("/login")
        already_on_list = List_Entry.query.filter(and_(List_Entry.anime_id==form.anime.data, List_Entry.list_id==curr_list.id)).first()
        if already_on_list:
            flash("This anime is already on your list!", "danger")
        else:
            make_list_entry(form.anime.data,curr_list.id,rating=0,categories=None)
            flash("This anime has been added to your list!", "success")
    return render_template('show-recommended.html',recommendations=recommendations, form=form, curr_title=curr_title)

@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def create_category():
    if current_user.get_id()==None:
        flash("Please login to make a category.", "danger")
        return redirect("/login")
    form = CategoryForm()
    categories = Category.query.all()
    if form.validate_on_submit():
        if pf.is_profane(form.name.data) == True:
            flash('Please avoid using profanity!','danger')
        else:
            try:
                category_name=standardize(form.name.data)
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()
                flash("Your category was added successfully!", "success")
                return redirect(f"/my-lists/{current_user.id}")
            except IntegrityError:
                db.session.rollback()
                flash("This category already exists!", "danger")
    return render_template('new-category.html', form=form, categories=categories)

@app.route('/<list_id>/suggestions', methods=['GET','POST'])
@login_required
def make_suggestion(list_id):
    if current_user.get_id()==None:
        flash("Please login to make suggestions.", "danger")
        return redirect("/login")
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
        if pf.is_profane(form.comment.data) == True:
            flash('Please avoid using profanity!','danger')
        else:
            send_anime_recommendation(anime,form.anime.data,form.comment.data,current_user.username,curr_list)
            flash(f'{curr_list.users.username} will see your recommendation in their inbox!','success')
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

@app.route('/suggestions/<suggestion_id>/add-to-list',methods=['POST'])
@login_required
def add_from_inbox(suggestion_id):
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    curr_list = List.query.get_or_404(request.form['list-id'])
    if current_user.id != curr_list.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    already_on_list = List_Entry.query.filter(and_(List_Entry.anime_id==request.form['anime-id'], List_Entry.list_id==curr_list.id)).first()
    if already_on_list:
        flash("This anime is already on your list!", "danger")
    else:
        make_list_entry(request.form['anime-id'],curr_list.id,rating=0,categories=None)
        db.session.delete(suggestion)
        db.session.commit()
        flash("This anime has been added to your list!", "success")
    return redirect(f'/{curr_list.id}/suggestion-inbox')

@app.route('/suggestions/<suggestion_id>/remove',methods=['POST'])
@login_required
def delete_suggestion(suggestion_id):
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    if current_user.id != suggestion.lists.users.id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    db.session.delete(suggestion)
    db.session.commit()
    flash("Deleted successfully!", "success")
    return redirect(f'/{suggestion.lists.id}/suggestion-inbox')

@app.route('/<list_id>/<entry_id>/add-comment',methods=['POST'])
@login_required
def new_comment(list_id,entry_id):
    # https://stackoverflow.com/questions/63851329/how-to-add-csrf-to-flask-app-without-wtforms
    if current_user.get_id()==None:
        flash("Please login to comment.", "danger")
        return redirect("/login")
    curr_list = List.query.get_or_404(list_id)
    entry = List_Entry.query.get_or_404(entry_id)
    comment_data = request.form['comment']
    if pf.is_profane(comment_data) == True:
        flash('Please avoid using profanity!','danger')
    else:
        if current_user.id == curr_list.users.id:
            entry_owner = True
        else:
            entry_owner = False
        if request.form.get('spoiler') == None:
            spoiler = False
        else:
            spoiler = True
        comment = Comment(entry_id=entry.id,text=comment_data,username=current_user.username,entry_owner=entry_owner,spoiler=spoiler, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash("Posted!", "success")
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
            flash("Sorry to see you go! Your account has been successfully deleted", "success")
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
            try:
                curr_user.avatar_url = form.avatar_url.data or curr_user.avatar_url
                curr_user.email = form.email.data or curr_user.email
                if form.new_password.data:
                    hashed_pass = bcrypt.generate_password_hash(form.new_password.data).decode('UTF-8')
                    curr_user.password = hashed_pass or curr_user.password
                db.session.add(curr_user)
                db.session.commit()
                flash("Your account was updated successfully!", "success")
                return redirect(f'/my-lists/{curr_user.id}')
            except IntegrityError:
                db.session.rollback()
                flash("Email is associated with another account", 'danger')
        else:
            flash("Invalid credentials.", 'danger')
    return render_template('update-user.html', form=form)

@ app.route('/<user_id>/lists')
def view_users(user_id):
    user = User.query.get_or_404(user_id)
    comment_occur_lst = []
    for lst in user.user_lists:
        total=0
        for entry in lst.list_entries:
            for comment in entry.entry_comments:
                total+=1
        comment_occur_lst.append(total)
    return render_template('show-user.html', user=user, comment_occur_lst=comment_occur_lst)

@ app.route("/logout")
@ login_required
def logout():
    logout_user()
    return redirect('/')

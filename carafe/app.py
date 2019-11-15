""" Carafe Application """
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import (
    LoginManager, current_user, login_user, login_required, logout_user
)
from htmlmin.main import minify
from passlib.hash import sha512_crypt as sha
from sqlalchemy import text

from carafe.config import load_config
from carafe.extensions.login import AnonymousUser
from carafe.database.model import Board, Post, Comment, User, db
from carafe.forms import (
    BoardForm, PostForm, CommentForm, LoginForm, SignupForm
)
from carafe.rest.api import api
from carafe import constants

# APP INIT
APP = Flask(__name__)
APP.register_blueprint(api)
load_config(APP)
db.init_app(APP)
db.app = APP
LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.anonymous_user = AnonymousUser
LOGIN_MANAGER.init_app(APP)

# ERROR HANDLER
@APP.errorhandler(404)
def page_not_found(_error):
    """
    error handler for 404
    """
    return render_template('404.html'), 404


# HTML Response Decorator to Minimize HTML
@APP.after_request
def response_minify(response):
    """
    minifies html response
    """
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(minify(response.get_data(as_text=True)))
        return response
    return response


# Login Manager Decorators
@LOGIN_MANAGER.unauthorized_handler
def unauthorized_callback():
    """
    unauthorized callbacks redirect
    """
    return redirect('/login?next=' + request.path)


@LOGIN_MANAGER.user_loader
def load_user(uid):
    """
    callback that is used to reload user object from the User uid
    """
    return User.query.get(uid)


# Database Helper function to Initialize Database Tables
def create_database_tables():
    """
    initializes database in the proper application context
    """
    with APP.app_context():
        db.create_all()


# Routes
@APP.route('/', methods=constants.METHODS)
def index():
    """
    application index route
    """
    return render_template(
        'index.html',
        boards=Board.query.filter_by(
            deleted=False),
        form=BoardForm())


@APP.route('/admin/panel', methods=constants.METHODS)
@login_required
def panel():
    """
    admin panel route
    """
    if current_user.is_admin:
        return render_template(
            'panel.html',
            User=User,
            Post=Post,
            Comment=Comment,
            Board=Board)
    return redirect(url_for('index'))


@APP.route('/board/<bid>')
def board(bid):
    """
    view that displays the post of the board specified by the provided bid
    """
    form = PostForm(request.form)
    posts = Post.query.filter_by(
        bid=bid, deleted=False).outerjoin(Comment).order_by(
            text("comment.date desc"))
    brd = Board.query.get(bid)
    return render_template('posts.html', posts=posts, b=brd, pform=form)


@APP.route('/board/<bid>/post/<pid>', methods=constants.METHODS)
def post(bid, pid):
    """
    post route
    """
    pst = Post.query.get(pid)
    if pst.deleted:
        flash('The post you are trying to access has been deleted.')
        return redirect(url_for('board', bid=bid))
    comments = Comment.query.filter_by(pid=pid).order_by(text("date asc"))
    return render_template(
        'post.html',
        p=pst,
        bid=bid,
        comments=comments,
        pform=PostForm(),
        cform=CommentForm())


@APP.route('/signup', methods=constants.METHODS)
def sign_up():
    """
    user registration route
    """
    if not current_user.is_admin and not APP.config['REGISTRATION_FLAG']:
        flash('Sorry, user registration is disabled.')
        return redirect(url_for('index'))

    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('index'))

    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        for user in User.query.all():
            if (user.username == form.username.data.lower() or
                    user.email == form.email.data.lower()):
                flash('Username or email is already taken.')
                return render_template('signup.html', form=form)
        user = User(
            form.username.data.lower(),
            form.email.data.lower(),
            sha.encrypt(
                form.password.data))
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering, {}!'.format(user.username))
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@APP.route("/login", methods=constants.METHODS)
def login():
    """
    logs in user if proper parameters are entered and creates a session for
    that user
    """
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(
            username=form.username.data.lower()).first()
        if user and sha.verify(form.password.data, user.password):
            login_user(user)
            flash('You are logged in as {}!'.format(user.username))
            return redirect(url_for('index'))
        flash('User either does not exist or password is invalid.')
    return render_template('login.html', form=form)


@APP.route("/logout")
@login_required
def logout():
    """
    logs out user and redirects to front page
    """
    logout_user()
    flash('Successfully logged out.')
    return redirect(request.referrer)


@APP.route('/board/create', methods=constants.METHODS)
def create_board():
    """
    creates board if form parameters meet requirements
    """
    form = BoardForm(request.form)
    if current_user.is_admin and request.method == 'POST' and form.validate():
        if form.name.data.lower() not in [
                b.name.lower() for b in Board.query.all()]:
            db.session.add(Board(form.name.data, form.desc.data))
            db.session.commit()
            flash('Board ({}) successfully created!'.format(form.name.data))
        else:
            flash('Duplicate board detected.')
    return render_template(
        'index.html',
        boards=Board.query.filter_by(
            deleted=False),
        form=form)


@APP.route('/board/edit/<bid>', methods=constants.METHODS)
def edit_board(bid):
    """
    allows the editing of a board with the provided bid
    """
    form = BoardForm(request.form)
    brd = Board.query.get(bid)
    if current_user.is_admin and request.method == 'POST':
        if form.validate():
            if brd.name != form.name.data or brd.desc != form.desc.data:
                brd.name = form.name.data
                brd.desc = form.desc.data
                db.session.commit()
                flash('Board ({}) successfully edited!'.format(form.name.data))
        else:
            flash(constants.DEFAULT_SUBMISSION_ERR)
    return redirect(request.referrer)


@APP.route('/board/<bid>/delete')
@login_required
def delete_board(bid):
    """
    allows the board to be flagged for deletion by an admin
    """
    if current_user.is_admin:
        Board.query.get(bid).deleted = True
        db.session.commit()
        flash('Board {} is no longer viewable.'.format(bid))
    return redirect(request.referrer)


# POST VIEWS
@APP.route('/board/<bid>/post/create', methods=constants.METHODS)
@login_required
def create_post(bid):
    """
    allows the creation of a post as long as parameters are met and the user
    is in an active session
    """
    form = PostForm(request.form)
    if request.method == 'POST':
        if form.validate():
            db.session.add(
                Post(
                    bid,
                    current_user.uid,
                    form.name.data,
                    form.desc.data))
            db.session.commit()
            flash('Post ({}) successfully created!'.format(form.name.data))
        else:
            flash(constants.DEFAULT_SUBMISSION_ERR)
    return redirect(request.referrer)


@APP.route('/board/<bid>/post/<pid>/edit', methods=constants.METHODS)
@login_required
def edit_post(_bid, pid):
    """
    allows the editing of a post as long as the active user is the post
    creator or admin
    """
    pst = Post.query.get(pid)
    form = PostForm(request.form)
    if request.method == 'POST' and current_user.uid == pst.uid:
        if form.validate():
            if pst.name != form.name.data or pst.text != form.desc.data:
                og_name = pst.name
                pst.name = form.name.data
                pst.text = form.desc.data
                db.session.commit()
                flash('Post ({}) successfully edited!'.format(og_name))
        else:
            flash(constants.DEFAULT_SUBMISSION_ERR)
    return redirect(request.referrer)


@APP.route('/board/<bid>/post/<pid>/delete')
@login_required
def delete_post(_bid, pid):
    """
    allows for the deletion of a post as long as the active user is the post
    creator or admin
    """
    if current_user.is_admin or current_user == Post.query.get(int(pid)).uid:
        Post.query.get(pid).deleted = True
        db.session.commit()
    return redirect(request.referrer)


# COMMENT VIEWS
@APP.route('/board/<bid>/post/<pid>/comment', methods=constants.METHODS)
@login_required
def create_comment(_bid, pid):
    """
    allows for the creation of a comment by an active user
    """
    form = CommentForm(request.form)
    if request.method == 'POST':
        if form.validate():
            db.session.add(Comment(pid, current_user.uid, form.text.data))
            db.session.commit()
            flash('Comment successfully created!')
        else:
            flash(constants.DEFAULT_SUBMISSION_ERR)
    return redirect(request.referrer)


@APP.route(
    '/board/<bid>/post/<pid>/comment/<cid>/edit',
    methods=constants.METHODS)
@login_required
def edit_comment(_bid, _pid, cid):
    """
    allows the editing of a post as long as the active user is the post creator
    or admin
    """
    comment = Comment.query.get(cid)
    form = CommentForm(request.form)
    if request.method == 'POST' and current_user.uid == comment.uid:
        if form.validate():
            if comment.text != form.text.data:
                comment.text = form.text.data
                db.session.commit()
                flash('Comment successfully edited!')
        else:
            flash(constants.DEFAULT_SUBMISSION_ERR)
    return redirect(request.referrer)


@APP.route('/board/<bid>/post/<pid>/comment/<cid>/delete')
@login_required
def delete_comment(_bid, pid, cid):
    """
    allows for a comment to be 'deleted' by the comment creator or admin
    """
    comment = Comment.query.filter_by(pid=pid, cid=cid).first()
    if current_user.is_admin or current_user.uid == comment.uid:
        comment.deleted = True
        db.session.commit()
    return redirect(request.referrer)


@APP.route('/board/<bid>/post/<pid>/comment/<cid>/revive')
def revive_comment(_bid, pid, cid):
    """
    allows for a 'deleted' comment to be 'revived' by an admin
    """
    comment = Comment.query.filter_by(pid=pid, cid=cid).first()
    if current_user.is_admin:
        comment.deleted = False
        db.session.commit()
    return redirect(request.referrer)


@APP.route('/admin/board/<bid>/erase')
@login_required
def erase_board(bid):
    """
    admin "erase" board route
    """
    if current_user.is_admin:
        db.session.delete(Board.query.get(bid))
        db.session.commit()
        msg = 'Board {} permanently removed from database. '\
            'All associated posts and comments have also been removed.'
        flash(msg.format(bid))
    else:
        flash(constants.DEFAULT_SUBMISSION_ERR)
    return redirect(request.referrer)


@APP.route('/admin/board/<bid>/revive')
@login_required
def revive_board(bid):
    """
    admin revive board route
    """
    if current_user.is_admin:
        Board.query.get(bid).deleted = False
        db.session.commit()
        msg = 'Board {} is now visible again.'
        flash(msg.format(bid))
    else:
        flash(constants.DEFAULT_SUBMISSION_ERR)
    return redirect(request.referrer)

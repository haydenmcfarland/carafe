from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from htmlmin.main import minify
from passlib.hash import sha512_crypt as sha
from carafe.config import load_config
from carafe.classes.login import AnonymousUser
from carafe.database.model import Board, Post, Comment, User, Config, db
from carafe.forms import BoardForm, PostForm, CommentForm, LoginForm, SignupForm, ConfigForm
from carafe.rest.api import api
from carafe import constants

# APP INIT
app = Flask(__name__)
app.register_blueprint(api)
load_config(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.anonymous_user = AnonymousUser
login_manager.init_app(app)

#@app.before_request
#def setup_required():
#    if request.path not in ['/', '/login', '/logout'] and 'static' not in request.path and not app.config['SETUP']:
#        flash('Setup is required before Carafe can be used.')
#        return redirect(url_for('index'))


# ERROR HANDLER
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# HTML Response Decorator to Minimize HTML
@app.after_request
def response_minify(response):
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(minify(response.get_data(as_text=True)))
        return response
    return response


# Login Manager Decorators
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@login_manager.user_loader
def load_user(uid):
    """ Callback that is used to reload user object from the User uid. """
    return User.query.get(uid)


# Context Processors for Jinja2 Template Access
def context_config():
    return dict(config=app.config)


# Database Helper function to Initialize Database Tables
def create_database_tables():
    """ Initializes database in the proper application context. """
    with app.app_context():
        db.create_all()


# Routes
@app.route('/', methods=constants.METHODS)
def index():
    #if not app.config['SETUP']:
    #    form = ConfigForm(request.form)
    #    if request.method == 'POST' and form.validate():
    #        app.config['SETUP'] = True
    #        app.config['NAME'] = form.name.data
    #        app.config['REGISTRATION_FLAG'] = form.enable_registration.data
    #        return redirect(url_for('index'))
    #    return render_template('setup.html', form=form)
    #else:
    return render_template('index.html', boards=Board.query.filter_by(deleted=False), form=BoardForm())


@app.route('/admin/panel', methods=constants.METHODS)
@login_required
def panel():
    if current_user.is_admin:
        return render_template('panel.html', User=User, Post=Post, Comment=Comment, Board=Board)
    else:
        return redirect(url_for('index'))


@app.route('/board/<bid>')
def board(bid):
    """ View that displays the post of the board specified by the provided bid. """
    form = PostForm(request.form)
    posts = Post.query.filter_by(bid=bid, deleted=False)
    b = Board.query.get(bid)
    return render_template('posts.html', posts=sorted(posts, key=lambda x: x.recent_date(), reverse=True),
                           b=b, pform=form)


@app.route('/board/<bid>/post/<pid>', methods=constants.METHODS)
def post(bid, pid):
    p = Post.query.get(pid)
    if p.deleted:
        flash('The post you are trying to access has been deleted.')
        return redirect(url_for('board', bid=bid))
    """ View that displays the post specified by the provided pid. """
    return render_template('post.html', p=p, bid=bid,
                           comments=sorted(Comment.query.filter_by(pid=pid), key=lambda x: x.date),
                           pform=PostForm(), cform=CommentForm())


@app.route('/board/<bid>/post/<pid>', methods=constants.METHODS)
def filter_posts(bid, pid):
    p = Post.query.get(pid)
    if p.deleted:
        flash('The post you are trying to access has been deleted.')
        return redirect(url_for('board', bid=bid))
    """ View that displays the post specified by the provided pid. """
    return render_template('post.html', p=p, bid=bid,
                           comments=sorted(Comment.query.filter_by(pid=pid), key=lambda x: x.date),
                           pform=PostForm(), cform=CommentForm())


@app.route('/signup', methods=constants.METHODS)
def sign_up():
    if not current_user.is_admin and not app.config['REGISTRATION_FLAG']:
        flash('Sorry, user registration is disabled.')
        return redirect(url_for('index'))

    elif current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('index'))

    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        for u in User.query.all():
            if u.username == form.username.data.lower() or u.email == form.email.data.lower():
                flash('Username or email is already taken.')
                return render_template('signup.html', form=form)
        user = User(form.username.data.lower(), form.email.data.lower(), sha.encrypt(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering, {}!'.format(user.username))
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route("/login", methods=constants.METHODS)
def login():
    """ Logs in user if proper  parameters are entered and creates a session for that user. """
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and sha.verify(form.password.data, user.password):
            login_user(user)
            flash('You are logged in as {}!'.format(user.username))
            return redirect(url_for('index'))
        else:
            flash('User either does not exist or password is invalid.')
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    """ Logs out user and redirects to front page. """
    logout_user()
    flash('Successfully logged out.')
    return redirect(url_for('index'))


@app.route('/board/create', methods=constants.METHODS)
def create_board():
    """ Creates board if form parameters meet requirements. """
    form = BoardForm(request.form)
    if current_user.is_admin and request.method == 'POST' and form.validate():
        if form.name.data.lower() not in [b.name.lower() for b in Board.query.all()]:
            db.session.add(Board(form.name.data, form.desc.data))
            db.session.commit()
            flash('Board ({}) successfully created!'.format(form.name.data))
        else:
            flash('Duplicate board detected.'.format(form.name.data))
    return render_template('index.html', boards=Board.query.filter_by(deleted=False), form=form)


@app.route('/board/edit/<bid>', methods=constants.METHODS)
def edit_board(bid):
    """ Allows the editing of a board with the provided bid. """
    form = BoardForm(request.form)
    b = Board.query.get(bid)
    if current_user.is_admin and request.method == 'POST' and form.validate():
        b.name = form.name.data
        b.desc = form.desc.data
        db.session.commit()
        flash('Board ({}) successfully edited!'.format(form.name.data))

    return redirect(url_for('index'))


@app.route('/board/<bid>/delete')
@login_required
def delete_board(bid):
    """ Allows the a board to be flagged for deletion only if the user is an Admin. """
    if current_user.is_admin:
        Board.query.get(bid).deleted = True
        db.session.commit()
    return redirect(url_for('index'))


# POST VIEWS
@app.route('/board/<bid>/post/create', methods=constants.METHODS)
@login_required
def create_post(bid):
    """ Allows the creation of a post as long as parameters are met and the user is in an active session. """
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        db.session.add(Post(bid, current_user.uid, form.name.data, form.desc.data))
        db.session.commit()
        flash('Post ({}) successfully created!'.format(form.name.data))
    return redirect(url_for('board', bid=bid))


@app.route('/board/<bid>/post/<pid>/edit', methods=constants.METHODS)
@login_required
def edit_post(bid, pid):
    """ Allows the editing of a post as long as the active user is the post creator or Admin. """
    p = Post.query.get(pid)
    form = PostForm(request.form)
    if current_user.uid == p.uid or current_user.is_admin:
        og_name = p.name
        p.name = form.name.data
        p.text = form.desc.data
        db.session.commit()
        flash('Post ({}) successfully edited!'.format(og_name))
    return redirect(url_for('board', bid=bid))


@app.route('/board/<bid>/post/<pid>/delete')
@login_required
def delete_post(bid, pid):
    """ Allows for the deletion of a post as long as the active user is the post creator or Admin. """
    if current_user.is_admin or current_user == Post.query.get(int(pid)).uid:
        Post.query.get(pid).deleted = True
        db.session.commit()
    return redirect(url_for('board', bid=bid))


# COMMENT VIEWS
@app.route('/board/<bid>/post/<pid>/comment', methods=constants.METHODS)
@login_required
def create_comment(bid, pid):
    """ Allows for the creation of a comment by an active user. """
    form = CommentForm(request.form)
    if request.method == 'POST' and form.validate():
        db.session.add(Comment(pid, current_user.uid, form.text.data))
        db.session.commit()
    return redirect(url_for('post', bid=bid, pid=pid))


@app.route('/board/<bid>/post/<pid>/comment/<cid>/edit', methods=constants.METHODS)
@login_required
def edit_comment(bid, pid, cid):
    """ Allows the editing of a post as long as the active user is the post creator or Admin. """
    c = Comment.query.get(cid)
    form = CommentForm(request.form)
    if current_user.uid == c.uid:
        c.text = form.text.data
        db.session.commit()
        flash('Comment successfully edited!')
    return redirect(url_for('post', bid=bid, pid=pid))


@app.route('/board/<bid>/post/<pid>/comment/<cid>/delete')
@login_required
def delete_comment(bid, pid, cid):
    """ Allows for a comment to be 'deleted' by the comment creator or Admin. """
    comment = Comment.query.filter_by(pid=pid, cid=cid).first()
    if current_user.is_admin or current_user.uid == comment.uid:
        comment.deleted = True
        db.session.commit()
    return redirect(url_for('post', bid=bid, pid=pid))


@app.route('/board/<bid>/post/<pid>/comment/<cid>/revive')
def revive_comment(bid, pid, cid):
    """ Allows for a 'deleted' comment to be 'revived' by an Admin. """
    comment = Comment.query.filter_by(pid=pid, cid=cid).first()
    if current_user.is_admin:
        comment.deleted = False
        db.session.commit()
    return redirect(url_for('post', bid=bid, pid=pid))

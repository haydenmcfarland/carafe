""" Carafe Models """

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from carafe.forms import BoardForm, PostForm, CommentForm
from carafe.database.base import UserContent
from carafe import constants

DB = SQLAlchemy()


class User(DB.Model):
    """
    Carafe User class that describes registered user
    """
    uid = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(constants.USERNAME_LIMIT), unique=True)
    email = DB.Column(DB.String(constants.EMAIL_LIMIT), unique=True)
    password = DB.Column(DB.String(128))
    is_active = DB.Column(DB.Boolean)
    is_anonymous = DB.Column(DB.Boolean)
    is_authenticated = DB.Column(DB.Boolean)
    is_confirmed = DB.Column(DB.Boolean)
    is_admin = DB.Column(DB.Boolean)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.is_active = True
        self.is_anonymous = False
        self.is_authenticated = True
        self.is_confirmed = False

    def get_id(self):
        """
        retrieves the user's id
        """
        return self.uid


class Board(DB.Model):
    """
    Carafe Board class that describes forum boards
    """
    bid = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(constants.NAME_LIMIT), unique=True)
    desc = DB.Column(DB.String(constants.DESC_LIMIT))
    deleted = DB.Column(DB.Boolean)

    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.deleted = False

    def get_recent_post(self):
        """
        gets most recent board post
        """
        return Post.query.filter_by(
            bid=self.bid).order_by(
                text('date desc')).first()

    def get_post_count(self):
        """
        gets the number of posts on a board
        """
        return Post.query.filter_by(bid=self.bid).count()

    def get_edit_form(self):
        """
        gets the edit for for a board
        """
        form = BoardForm()
        form.name.data = self.name
        form.desc.data = self.desc
        return form

    def get_username(self):
        """
        board method to get username
        """
        return User.query.get(self.uid).username


class Post(DB.Model, UserContent):
    """
    Carafe Post class that describes board posts
    """
    pid = DB.Column(DB.Integer, primary_key=True)
    bid = DB.Column(DB.Integer, DB.ForeignKey(Board.bid, ondelete='CASCADE'))
    uid = DB.Column(DB.Integer, DB.ForeignKey(User.uid, ondelete='CASCADE'))
    date = DB.Column(DB.DateTime, index=True)
    date_edited = DB.Column(DB.DateTime, index=True)
    name = DB.Column(DB.String(constants.NAME_LIMIT))
    text = DB.Column(DB.String(constants.TEXT_LIMIT))
    deleted = DB.Column(DB.Boolean)

    def __init__(self, bid, uid, name, txt):
        self.bid = bid
        self.uid = uid
        self.date = datetime.now()
        self.date_edited = self.date
        self.name = name
        self.text = txt
        self.deleted = False

    def get_comment_count(self):
        """
        get total comment count on post
        """
        return Comment.query.filter_by(pid=self.pid).count()

    def get_latest_comment_info(self):
        """
        get the latest comment info on the post
        """
        comment = Comment.query.filter_by(
            pid=self.pid).order_by(
                text("date desc")).first()
        if comment:
            return comment.get_date_str()
        return 'None'

    def recent_date(self):
        """
        get most recent comment date or post date
        """
        comment = Comment.query.filter_by(
            pid=self.pid).order_by(
                text("date desc")).first()
        if comment:
            return comment.date
        return self.date

    def get_edit_form(self):
        """
        gets post edit form
        """
        form = PostForm()
        form.name.data = self.name
        form.desc.data = self.text
        return form

    def get_username(self):
        """
        post helper to get username by id
        """
        return User.query.get(self.uid).username


class Comment(DB.Model, UserContent):
    """
    Carafe Comment class that describes post comments
    """
    cid = DB.Column(DB.Integer, primary_key=True)
    pid = DB.Column(DB.Integer, DB.ForeignKey(Post.pid, ondelete='CASCADE'))
    uid = DB.Column(DB.Integer, DB.ForeignKey(User.uid, ondelete='CASCADE'))
    date = DB.Column(DB.DateTime, index=True)
    date_edited = DB.Column(DB.DateTime, index=True)
    text = DB.Column(DB.String(constants.TEXT_LIMIT))
    deleted = DB.Column(DB.Boolean)

    def __init__(self, pid, uid, txt):
        self.pid = pid
        self.uid = uid
        self.text = txt
        self.date = datetime.now()
        self.date_edited = self.date
        self.deleted = False

    def get_edit_form(self):
        """
        get edit form of comment
        """
        form = CommentForm()
        form.text.data = self.text
        return form

    def get_username(self):
        """
        comment method to get username
        """
        return User.query.get(self.uid).username

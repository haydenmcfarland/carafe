from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from carafe.forms import BoardForm, PostForm, CommentForm
from carafe.database.base import CarafeObj, UserContent
from carafe import constants
from sqlalchemy import text
db = SQLAlchemy()


class User(db.Model, CarafeObj):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(constants.USERNAME_LIMIT), unique=True)
    email = db.Column(db.String(constants.EMAIL_LIMIT), unique=True)
    password = db.Column(db.String(128))
    is_active = db.Column(db.Boolean)
    is_anonymous = db.Column(db.Boolean)
    is_authenticated = db.Column(db.Boolean)
    is_confirmed = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.is_active = True
        self.is_anonymous = False
        self.is_authenticated = True
        self.is_confirmed = False

    def get_id(self):
        return self.uid


class Board(db.Model, CarafeObj):
    bid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(constants.NAME_LIMIT), unique=True)
    desc = db.Column(db.String(constants.DESC_LIMIT))
    deleted = db.Column(db.Boolean)

    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.deleted = False

    def get_recent_post(self):
        return Post.query.filter_by(
            bid=self.id).order_by(
            text('date desc')).first()

    def get_post_count(self):
        return Post.query.filter_by(bid=self.id).count()

    def get_edit_form(self):
        form = BoardForm()
        form.name.data = self.name
        form.desc.data = self.desc
        return form

    def get_username(self):
        return User.query.get(self.uid).username


class Post(db.Model, CarafeObj, UserContent):
    pid = db.Column(db.Integer, primary_key=True)
    bid = db.Column(db.Integer, db.ForeignKey(Board.bid, ondelete='CASCADE'))
    uid = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete='CASCADE'))
    date = db.Column(db.DateTime, index=True)
    date_edited = db.Column(db.DateTime, index=True)
    name = db.Column(db.String(constants.NAME_LIMIT))
    text = db.Column(db.String(constants.TEXT_LIMIT))
    deleted = db.Column(db.Boolean)

    def __init__(self, bid, uid, name, text):
        self.bid = bid
        self.uid = uid
        self.date = datetime.now()
        self.date_edited = self.date
        self.name = name
        self.text = text
        self.deleted = False

    def get_comment_count(self):
        return Comment.query.filter_by(pid=self.id).count()

    def get_latest_comment_info(self):
        comment = Comment.query.filter_by(
            pid=self.id).order_by(
            text("date desc")).first()
        if comment:
            return comment.get_date_str()
        else:
            return 'None'

    def recent_date(self):
        comment = Comment.query.filter_by(
            pid=self.id).order_by(
            text("date desc")).first()
        if comment:
            return comment.date
        else:
            return self.date

    def get_edit_form(self):
        form = PostForm()
        form.name.data = self.name
        form.desc.data = self.text
        return form

    def get_username(self):
        return User.query.get(self.uid).username


class Comment(db.Model, CarafeObj, UserContent):
    cid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey(Post.pid, ondelete='CASCADE'))
    uid = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete='CASCADE'))
    date = db.Column(db.DateTime, index=True)
    date_edited = db.Column(db.DateTime, index=True)
    text = db.Column(db.String(constants.TEXT_LIMIT))
    deleted = db.Column(db.Boolean)

    def __init__(self, pid, uid, text):
        self.pid = pid
        self.uid = uid
        self.text = text
        self.date = datetime.now()
        self.date_edited = self.date
        self.deleted = False

    def get_edit_form(self):
        form = CommentForm()
        form.text.data = self.text
        return form

    def get_username(self):
        return User.query.get(self.uid).username

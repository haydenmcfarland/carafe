from wtforms import (
    StringField, Form, PasswordField, TextAreaField, BooleanField, validators
)
from wtforms.validators import Length, DataRequired, EqualTo
from carafe import constants


class SignupForm(Form):
    username = StringField(
        'Username', [
            Length(
                min=constants.USERNAME_MIN, max=constants.USERNAME_LIMIT)])
    email = StringField(
        'Email Address', [
            Length(
                min=constants.EMAIL_MIN, max=constants.EMAIL_LIMIT)])
    password = PasswordField(
        'Password', [
            validators.DataRequired(), validators.EqualTo(
                'confirm', message='Passwords must match.')])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    username = StringField(
        'Username', [
            Length(
                min=constants.USERNAME_MIN, max=constants.USERNAME_LIMIT)])
    password = PasswordField(
        'Password', [
            DataRequired(), EqualTo(
                'confirm', message='Passwords must match.')])
    confirm = PasswordField('Repeat Password')


class BoardForm(Form):
    name = StringField(
        'Board Name', [
            Length(
                min=constants.NAME_MIN, max=constants.NAME_LIMIT)])
    desc = TextAreaField(
        'Description', [
            Length(
                min=constants.DESC_MIN, max=constants.DESC_LIMIT)])


class PostForm(Form):
    name = StringField(
        'Post Title', [
            Length(
                min=constants.NAME_MIN, max=constants.NAME_LIMIT)])
    desc = TextAreaField(
        'Content', [
            Length(
                min=constants.TEXT_MIN, max=constants.TEXT_LIMIT)])


class CommentForm(Form):
    text = TextAreaField(
        'Leave a comment:', [
            Length(
                min=constants.TEXT_MIN, max=constants.TEXT_LIMIT)])


class ConfigForm(Form):
    name = StringField(
        'Carafe Board Name', [
            Length(
                min=constants.NAME_MIN, max=constants.NAME_LIMIT)])
    enable_registration = BooleanField('Enable registration')

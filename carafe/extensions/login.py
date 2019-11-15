""" Carafe Login Extension """

from flask_login import AnonymousUserMixin


class AnonymousUser(AnonymousUserMixin):
    """ Carafe Anonymous User Mixin """
    is_admin = False

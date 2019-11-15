from flask_login import AnonymousUserMixin


class AnonymousUser(AnonymousUserMixin):
    is_admin = False

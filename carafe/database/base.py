""" Carafe Database """

from flask import Markup
from flask_sqlalchemy import inspect
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from bs4 import BeautifulSoup

OEMBED_PROVIDERS = bootstrap_basic(OEmbedCache())

class CarafeObj:
    """ Base Object """
    @property
    def id(self):
        """
        returns the id of the object
        """
        return self.__dict__[inspect(type(self)).primary_key[0].name]


class UserContent:
    """ UserContent class """
    @property
    def html_content(self):
        """ parses markdown content """
        hil = CodeHiliteExtension(linenums=True, css_class='highlight')
        extra = ExtraExtension()
        mrkdwn_content = markdown(self.text, extensions=[hil, extra])
        oembed_content = parse_html(
            mrkdwn_content,
            OEMBED_PROVIDERS,
            urlize_all=True)
        return Markup(oembed_content)

    @property
    def clean_text(self):
        """ cleans text of html """
        html = markdown(self.text)
        return ''.join(BeautifulSoup(html, "html.parser").findAll(text=True))

    def get_date_str(self):
        """ Carafe Base Object """
        return self.date.strftime('%b %e %Y at ') + \
            self.date.strftime('%I:%M %p').lstrip('0')

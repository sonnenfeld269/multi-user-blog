import webapp2
import jinja2
import os
import hashlib
import hmac
from models import User
from handlers.secret_key import SECRET

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class BaseHandler(webapp2.RequestHandler):

    """
    BaseHandler class

    This class uses webapp2.RequestHandler as a parent. Its responsibility
    is the communication to the client (browser) using jinja2 template engine.

    """

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.get_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def login(self, user):
        """Creates a cookie for the browser.

        Args:
            user: the user who wants to log in
        """
        self.set_cookie('user_id', str(user.key().id()))

    def logout(self):
        """Removes the cookie by adding an empty 'Set-Cookie' to the headers.
        """
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def set_cookie(self, name, value):
        """Creates a cookie, which will be added to the request header of the
        browser.

        Args:
            name: the name of the cookie
            value: the value of the cookie
        """
        secure_value = self.make_secure_value(SECRET, value)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, secure_value))

    def get_cookie(self, name):
        """Get the cookie from the request by the browser and validate it.

        Returns:
            A string containing the cookie information, which was returned from
            the browser.
        """
        our_cookie = self.request.cookies.get(name)
        return our_cookie and self.check_secure_val(our_cookie)

    def make_secure_value(self, secret_key, value):
        """Creates a secure value.

        Returns:
            A string containing the original value followed by a hashed version
            of that value.
        """
        return value + "|" + hmac.new(secret_key, value).hexdigest()

    def check_secure_val(self, h):
        """Creates a secure value and compares it to the original.

        Returns:
            val: the original value
            None: nothing, if given hash is not equal to the secure value.
        """
        val = h.split('|')[0]

        if h == self.make_secure_value(SECRET, val):
            return val
        else:
            return None


class MainPageHandler(BaseHandler):

    def get(self):
        self.redirect("/blog")

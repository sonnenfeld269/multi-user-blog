import webapp2, jinja2
import os, hashlib, hmac
from models import User

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

# a secret key for cookies
SECRET = "uaophahsdfpoahsdfppncvfoefkyyxcvJSFMzzueri"

class BaseHandler(webapp2.RequestHandler):

    """
    BaseHandler class

    This class uses webapp2.RequestHandler as a parent. Its responsibility
    is the communication to the client (browser) using jinja2 template engine.

    """

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.get_cookie('user_id')
        print uid
        self.user = uid and User.by_id(int(uid))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        kw['user'] = self.user
        self.write(self.render_str(template, **kw))

    def login(self, user):
        self.set_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def set_cookie(self, name, value):
        secure_value = self.make_secure_value(SECRET, value)
        # send a response to the browser(client) telling him to add a header
        # called 'set cookie'.
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, secure_value))

    def get_cookie(self, name):
        # request the cookie from the browser response header
        our_cookie = self.request.cookies.get(name)
        return our_cookie and self.check_secure_val(our_cookie)

    def make_secure_value(self, secret_key, value):
        return value + "|" + hmac.new(secret_key, value).hexdigest()

    def check_secure_val(self, h):
        val = h.split('|')[0]

        if h == self.make_secure_value(SECRET, val):
            return val
        else:
            return None

class MainPageHandler(BaseHandler):

    def get(self):
        self.redirect("/blog")

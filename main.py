import hashlib, hmac, os, re # python libraries
import webapp2, jinja2 # external libraries
import models # own-created libraries
import handlers.user_handler, handlers.post_handler
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

# a secret key for cookies
SECRET = "uaophahsdfpoahsdfppncvfoefkyyxcvJSFMzzueri"

class Handler(webapp2.RequestHandler):

    """
    Handler class

    This class uses webapp2.RequestHandler as a parent. Its responsibility
    is the communication to the client (browser) using jinja2 template engine.

    """

    def initialize(self, *a, **kw):
        print "handler is: " + user_handler.initialize()
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.get_cookie('user_id')
        self.user = uid and user.User.by_id(int(uid))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
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
        secure_value = self.make_secure_value(SECRET,value)
        # send a response to the browser(client) telling him to add a header
        # called 'set cookie'.
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name,secure_value))

    def get_cookie(self, name):
        # request the cookie from the browser response header
        our_cookie = self.request.cookies.get(name)
        return our_cookie and self.check_secure_val(our_cookie)

    def make_secure_value(self,secret_key, value):
        return value + "|" + hmac.new(secret_key,value).hexdigest()

    def check_secure_val(self,h):
        val = h.split('|')[0]

        if h == self.make_secure_value(SECRET, val):
            return val
        else:
            return None

class RegisterHandler(Handler):

    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    MAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

    def get(self):
        self.render("auth/register.html")

    def post(self):
        # get the request from the http header
        user_name = self.request.get("name")
        user_password = self.request.get("password")
        user_password_repeat = self.request.get("password_repeat")
        user_email = self.request.get("email")

        # a parameter list to store the values and errors
        # user_name and user_email are the values to be kept in the form
        param_list = dict(user_name=user_name,user_email=user_email)
        any_error = False

        name_error = ""
        if user_name == None or not self.valid_username(user_name):
            param_list['name_error'] = "Username not valid!"
            any_error = True

        password_error = ""
        if not self.valid_password(user_password):
            param_list['password_error'] = "Password not valid!"
            any_error = True

        password_repeat_error = ""
        if user_password != user_password_repeat:
            param_list['password_repeat_error'] = "Passwords do not match!"
            any_error = True

        email_error = ""
        if user_email == None or not self.valid_email(user_email):
            param_list['email_error'] = "Email not valid!"
            any_error = True

        if not any_error:
            # if user exists, re-render form with error message
            if user.User.by_name(user_name):
                self.render("auth/register.html", name_error="User already exists!")
            else:
                u = user.User.register(user_name,user_password,user_email)
                self.login(u)
                self.redirect("/blog")
        else:
            self.render("auth/register.html", **param_list)

    def valid_username(self, username):
        return self.USER_RE.match(username)

    def valid_password(self, password):
        return self.PASS_RE.match(password)

    def valid_email(self, email):
        return self.MAIL_RE.match(email)

class LoginHandler(Handler):

    def get(self):
        self.render("auth/login.html")

    def post(self):
        # get the request from the http header
        user_name = self.request.get("name")
        user_password = self.request.get("password")
        any_error = False
        param_list = dict(user_name=user_name)

        if not user_name:
            param_list['name_error']="Username is missing!"
            any_error = True
        if not user_password:
            param_list['password_error']="Password is missing!"
            any_error = True

        if any_error:
            self.render("auth/login.html", **param_list)
        else:
            u = user.User.login(user_name,user_password)
            if not u:
                param_list['login_error']="Username or Password is invalid!"
                self.render("auth/login.html", **param_list)
            else:
                self.login(u)
                self.redirect("/blog")

class LogoutHandler(Handler):
    def get(self):
        self.logout()
        self.redirect('/blog')

class WelcomeHandler(Handler):

    # also if there is a redirect to "/welcome", this get methos will be called
    # and we can pass data inside here, instead inside the redirect url
    def get(self):
        username = self.request.get("username")
        self.render("welcome.html", user=username,
                    logged=current_user['logged'])

class BlogHandler(Handler):

    """ Get all posts from the database and render them """
    def get(self):
        posts = post.Post.get_all()
        self.render("blog/blog.html", posts=posts)

class PostHandler(Handler):

    def get(self):
        if self.user:
            self.render("blog/addpost.html")
        else:
            self.redirect("/login")

    def post(self):
        post_title = self.request.get("post_title")
        post_content = self.request.get("post_content")
        param_list = dict(post_title=post_title,post_content=post_content)
        any_error = False

        if not post_title:
            param_list['title_error'] = "Title is missing!"
            any_error = True
        if not post_content:
            param_list['content_error'] = "Content is missing!"
            any_error = True

        if any_error:
            self.render("blog/addpost.html", **param_list)
        else:
            # add post to database
            p = post.Post.add_post(post_title,post_content)
            self.redirect('/blog/%s' % str(p.key().id()))

class SinglePostHandler(Handler):

    # get the id from the url "blog/some_id"
    def get(self, post_id):

        # get the database key, which was generated by google datastore and
        # then it post that belongs to that key
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        # if there is not post with that id, return an error
        if not post:
            self.error(404)
            return
        # else render "permalink" with the post
        self.render("blog/permalink.html", post = post)

class MainPage(Handler):

    def get(self):
        self.render("blog/blog.html")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register', RegisterHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/logout', LogoutHandler),
    ('/welcome', WelcomeHandler),
    ('/blog', BlogHandler),
    ('/blog/addpost', PostHandler),
    ('/blog/([0-9]+)', SinglePostHandler)
], debug=True)

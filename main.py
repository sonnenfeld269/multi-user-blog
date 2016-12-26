import hashlib
import hmac
import os
import re  # python libraries
import webapp2
import jinja2  # external libraries
from models import Post, User, Comment  # own-created libraries
# import handlers.user_handler as user_handler, handlers.post_handler as post_handler
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

# USER and AUTHENTICATION handlers


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
        param_list = dict(user_name=user_name, user_email=user_email)
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
            if User.by_name(user_name):
                self.render("auth/register.html",
                            name_error="User already exists!")
            else:
                u = User.register(user_name, user_password, user_email)
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
            param_list['name_error'] = "Username is missing!"
            any_error = True
        if not user_password:
            param_list['password_error'] = "Password is missing!"
            any_error = True

        if any_error:
            self.render("auth/login.html", **param_list)
        else:
            u = User.login(user_name, user_password)
            if not u:
                param_list['login_error'] = "Username or Password is invalid!"
                self.render("auth/login.html", **param_list)
            else:
                self.login(u)
                self.redirect("/blog")

class LogoutHandler(Handler):

    def get(self):
        self.logout()
        self.redirect('/blog')

class BlogHandler(Handler):

    """ Get all posts from the database and render them """

    def get(self):
        self.render_blog()

    def render_blog(self, **kw):
        if kw.has_key('user_posts'):
            posts = kw['user_posts']
        else:
            posts = Post.get_all()

        rendered_posts = ""
        for post in posts:
            if kw.has_key('rendered_comments'):
                rendered_posts += self.render_str("blog/singlepost.html", p=post, rendered_comments=kw['rendered_comments'])
            else:
                rendered_posts += self.render_str("blog/singlepost.html", p=post)

        self.render("blog/blog.html", rendered_posts=rendered_posts, **kw)

# POST handlers

class UserPostHandler(BlogHandler):

    def get(self):
        user_posts = Post.get_by_user(self.user.get_id())
        self.render_blog(user_posts=user_posts)

class PostHandler(Handler):

    def get(self):
        if self.user:
            self.render("blog/addpost.html")
        else:
            self.redirect("/login")

    def post(self):
        post_title = self.request.get("post_title")
        post_content = self.request.get("post_content")
        param_list = dict(post_title=post_title, post_content=post_content)
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
            print "the user is: " + str(self.user.key().id())
            p = Post.add_post(post_title, post_content, self.user.key().id())
            self.redirect('/blog/%s' % str(p.key().id()))

class SinglePostHandler(Handler):

    # get the id from the url "blog/some_id"
    def get(self, post_id):

        post = Post.by_id(int(post_id))

        # if there is not post with that id, return an error
        if not post:
            self.error(404)
            return
        # else render "permalink" with the post
        single_post = self.render_str("blog/singlepost.html", p=post)
        self.render("blog/permalink.html", single_post=single_post)

class EditPostHandler(Handler):

    # get the id from the url "blog/some_id"
    def get(self, post_id):
        post = Post.by_id(int(post_id))

        # if there is not post with that id, return an error
        if not post:
            self.error(404)
            return

        # else render "editpost.html" with the post
        self.render("/blog/editpost.html", post=post)

    def post(self, post_id):
        post = Post.by_id(int(post_id))
        post_title = self.request.get("post_title")
        post_content = self.request.get("post_content")
        param_list = dict(post=post, post_title=post_title,
                          post_content=post_content)
        any_error = False

        if not post_title:
            param_list['title_error'] = "Title is missing!"
            any_error = True
        if not post_content:
            param_list['content_error'] = "Content is missing!"
            any_error = True

        if any_error:
            self.render("blog/editpost.html", **param_list)
        else:
            # add post to database
            p = Post.update_post(int(post_id), post_title, post_content)
            self.redirect('/blog/%s' % str(p.get_id()))

class LikePostHandler(Handler):

    # get the id from the url "blog/some_id"
    def get(self, post_id):
        Post.add_like(int(post_id), self.user.get_id())
        self.redirect('/blog')

class DeletePostHandler(Handler):

    # get the id from the url "blog/some_id"
    def get(self, post_id):
        Post.delete_post(post_id)
        self.redirect('/blog')

# COMMENT handlers

class CommentPostHandler(BlogHandler):

    def get(self, post_id):
        post = Post.by_id(int(post_id))
        if post.show_comments:
            post.set_show_comments(False)
        else:
            post.set_show_comments(True)

        rendered_comments = self.render_comments(post=post)
        self.render_blog(rendered_comments=rendered_comments)

    def post(self, post_id):
        comment_content = self.request.get("comment_content")
        Post.add_comment(int(post_id), int(self.user.get_id()), comment_content)
        self.redirect('/blog')

    def render_comments(self, post, comment_to_edit=None):
        print "inside render comments"
        if comment_to_edit:
            comment_to_edit=Comment.by_id(int(comment_id))

        rendered_comments = ""
        for comment in post.comments:
            if comment_to_edit and comment.get_id == comment_to_edit.get_id:
                rendered_comments += self.render_str("blog/editcomment.html", comment=comment_to_edit)
            else:
                rendered_comments += self.render_str("blog/singlecomment.html", comment=comment)
        return rendered_comments

class CommentEditHandler(CommentPostHandler):

    def get(self, comment_id):
        self.render_comments(comment_id)

    def post(self, comment_id):
        comment_content = self.request.get("comment_content")
        comment = Comment.by_id(int(comment_id))
        comment.set_content(comment_content)

        self.redirect('/blog')

class CommentDeleteHandler(Handler):

    def get(self, comment_id):
        print "Comment id is: " + str(comment_id)
        self.redirect('/blog')

    def post(self, post_id):
        pass

class MainPage(Handler):

    def get(self):
        self.redirect("/blog")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register', RegisterHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/blog', BlogHandler),
    ('/blog/([0-9]+)', SinglePostHandler),
    ('/blog/addpost', PostHandler),
    ('/blog/myposts', UserPostHandler),
    ('/blog/comment/([0-9]+)', CommentPostHandler),
    ('/blog/comment/edit/([0-9]+)', CommentEditHandler),
    ('/blog/comment/delete/([0-9]+)', CommentDeleteHandler),
    ('/blog/edit/([0-9]+)', EditPostHandler),
    ('/blog/like/([0-9]+)', LikePostHandler),
    ('/blog/delete/([0-9]+)', DeletePostHandler)

], debug=True)

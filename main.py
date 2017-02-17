import webapp2

# TODO can I make those imports shorter, so it follows the pep8 style guide?
from handlers.post_handler import BlogHandler, SinglePostHandler, AddPostHandler
from handlers.post_handler import EditPostHandler, DeletePostHandler, UserPostHandler, LikePostHandler
from handlers.post_handler import PostCommentsHandler, CommentEditHandler, CommentDeleteHandler
from handlers.user_handler import RegisterHandler, LoginHandler, LogoutHandler, WelcomeHandler
from google.appengine.ext import db

"""
This is the mapping module. Based on the url the defined handlers will be
initiated.
"""

app = webapp2.WSGIApplication([
    ('/', BlogHandler),
    ('/register', RegisterHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/welcome', WelcomeHandler),
    ('/blog', BlogHandler),
    ('/blog/addpost', AddPostHandler),
    ('/blog/myposts', UserPostHandler),
    ('/blog/([0-9]+)', SinglePostHandler),
    ('/blog/([0-9]+)/comments', SinglePostHandler),
    ('/blog/([0-9]+)/comments/new', PostCommentsHandler),
    ('/blog/([0-9]+)/edit', EditPostHandler),
    ('/blog/([0-9]+)/like', LikePostHandler),
    ('/blog/([0-9]+)/delete', DeletePostHandler),
    ('/blog/([0-9]+)/comment/([0-9]+)/edit', CommentEditHandler),
    ('/blog/([0-9]+)/comment/([0-9]+)/delete', CommentDeleteHandler)

], debug=True)

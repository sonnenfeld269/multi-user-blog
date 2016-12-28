import webapp2

from handlers.post_handler import MainPageHandler, BlogHandler, SinglePostHandler
from handlers.post_handler import AddPostHandler, EditPostHandler, DeletePostHandler, UserPostHandler, LikePostHandler 
from handlers.post_handler import CommentPostHandler, CommentEditHandler, CommentDeleteHandler
from handlers.user_handler import RegisterHandler, LoginHandler, LogoutHandler
from google.appengine.ext import db


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/register', RegisterHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/blog', BlogHandler),
    ('/blog/([0-9]+)', SinglePostHandler),
    ('/blog/([0-9]+)/comments', SinglePostHandler),
    ('/blog/addpost', AddPostHandler),
    ('/blog/myposts', UserPostHandler),
    ('/blog/comment/([0-9]+)', CommentPostHandler),
    ('/blog/comment/edit/([0-9]+)', CommentEditHandler),
    ('/blog/comment/delete/([0-9]+)', CommentDeleteHandler),
    ('/blog/edit/([0-9]+)', EditPostHandler),
    ('/blog/like/([0-9]+)', LikePostHandler),
    ('/blog/delete/([0-9]+)', DeletePostHandler)

], debug=True)

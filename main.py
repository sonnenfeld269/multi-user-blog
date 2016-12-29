import webapp2

#from handlers.base_handler import MainPageHandler
from handlers.post_handler import BlogHandler, SinglePostHandler
from handlers.post_handler import AddPostHandler, EditPostHandler, DeletePostHandler, UserPostHandler, LikePostHandler
from handlers.post_handler import PostCommentsHandler, CommentEditHandler, CommentDeleteHandler
from handlers.user_handler import RegisterHandler, LoginHandler, LogoutHandler
from google.appengine.ext import db


app = webapp2.WSGIApplication([
    ('/', BlogHandler),                                         # GET - show all blog posts
    #('/register', RegisterHandler),                                 # GET/POST - show register form or submit
    #('/login', LoginHandler),                                       # GET/POST - show login form or submit
    #('/logout', LogoutHandler),                                     # GET - logout the user
    ('/blog', BlogHandler),                                         # GET - show all blog posts
    #('/blog/addpost', AddPostHandler),                              # GET/POST - show add post form and submit
    #('/blog/myposts', UserPostHandler),                             # GET - show all posts of user
    #('/blog/([0-9]+)', SinglePostHandler),                          # GET - show single post
    #('/blog/([0-9]+)/comments', PostCommentsHandler),               # GET/POST - show all comments of post or submit
    #('/blog/([0-9]+)/edit', EditPostHandler),                       # GET/POST - show edit form of post or submit
    #('/blog/([0-9]+)/like', LikePostHandler),                       # POST - add like to post
    #('/blog/([0-9]+)/delete', DeletePostHandler),                   # POST - delete a post
    #('/blog/([0-9]+)/comment/([0-9]+)/edit', CommentEditHandler),   # GET/POST - show edit form or submit
    #('/blog/([0-9]+)/comment/([0-9]+)/delete', CommentDeleteHandler)# POST - delete a post

], debug=True)

from base_handler import BaseHandler
import webapp2
from models import Post, User

class BasePostHandler(BaseHandler):

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user_id = super(BasePostHandler, self).get_cookie("user_id")
        print user_id
        if user_id:
            BaseHandler.user = User.by_id(int(user_id))

class BlogHandler(BasePostHandler):

    def get(self):
        print "inside bloghandler"
        self.render_posts()

    def render_posts(self):

        """
        1.  get all the posts
        2.  render each post and save it in a single string
        3.  pass the single string containing all rendered posts to
            jinja2 using
        """
        posts = Post.get_all()

        rendered_posts = ""
        for post in posts:
            rendered_posts += post.render()

        self.render("blog/blog.html", rendered_posts=rendered_posts)

class UserPostHandler(BasePostHandler):

    """ Show all posts of one user """

    def get(self):
        user_posts = Post.get_by_user(int(self.user))
        self.render_posts(user_posts=user_posts)

class AddPostHandler(BasePostHandler):

    def get(self):
        """
        1.  if user exists, render "addpost.html"
        2.  else redirect to "/login"
        """
        if self.user:
            self.render("blog/addpost.html")
        else:
            self.redirect("/login")

    def post(self):
        """
        1.  get all the parameters from the request (form) and save them
            into variables
        2.  check if title and content exists, if not then put some error
            messages into a param list
        3.  if there is an error, render "addpost.html" with the errors inside
            the param list. else add the post to the database and redirect
            to page showing the single post with the url "/blog/{{\post_id}}"
        """
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
            p = Post.add_post(post_title, post_content, int(self.user))
            self.redirect('/blog/%s' % str(p.key().id()))

class SinglePostHandler(BasePostHandler):

    def get(self, post_id):
        """
        1. get the post by post_id and save it into single_post
        2. render it using "permalink.html" and single_post as the parameter
        """
        single_post = Post.by_id(int(post_id)).render()
        self.render("blog/permalink.html", single_post=single_post)


class EditPostHandler(BasePostHandler):

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

class LikePostHandler(BasePostHandler):

    # get the id from the url "blog/some_id"
    def get(self, post_id):
        Post.add_like(int(post_id), self.user.get_id())
        self.redirect('/blog')

class DeletePostHandler(BasePostHandler):

    # get the id from the url "blog/some_id"
    def get(self, post_id):
        Post.delete_post(post_id)
        self.redirect('/blog')

# COMMENT handlers

class PostCommentsHandler(BlogHandler):

    def get(self, post_id):
        post = Post.by_id(int(post_id))
        if post.show_comments:
            post.set_show_comments(False)
        else:
            post.set_show_comments(True)

        # returns a string of rendered comments
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

class CommentEditHandler(PostCommentsHandler):

    def get(self, comment_id):
        self.render_comments(comment_id)

    def post(self, comment_id):
        comment_content = self.request.get("comment_content")
        comment = Comment.by_id(int(comment_id))
        comment.set_content(comment_content)

        self.redirect('/blog')

class CommentDeleteHandler(BasePostHandler):

    def get(self, comment_id):
        print "Comment id is: " + str(comment_id)
        self.redirect('/blog')

    def post(self, post_id):
        pass

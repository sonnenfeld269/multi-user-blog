from base_handler import BaseHandler
from models import Post

class MainPageHandler(BaseHandler):

    def get(self):
        self.redirect("/blog")

class BlogHandler(BaseHandler):

    """ Get all posts from the database and render them """

    def get(self):
        self.render_posts()

    def render_posts(self, **kw):
        if kw.has_key('user_posts'):
            posts = kw['user_posts']
        else:
            posts = Post.get_all()

        rendered_posts = ""
        for post in posts:
            if kw.has_key('rendered_comments'):
                rendered_posts += self.render_str("blog/singlepost.html", p=post, rendered_comments=kw['rendered_comments'])
            else:
                rendered_posts += post.render()

        self.render("blog/blog.html", rendered_posts=rendered_posts, **kw)

class UserPostHandler(BlogHandler):

    """ Show all posts of one user """

    def get(self):
        user_posts = Post.get_by_user(self.user.get_id())
        self.render_posts(user_posts=user_posts)

class PostHandler(BaseHandler):

    def render_post(self, post_id):
        post = Post.by_id(int(post_id))

        if not post:
            self.error(404)
            return

        return self.render_str("blog/singlepost.html", p=post)

class AddPostHandler(PostHandler):

    """ Adding a post. """

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
            p = Post.add_post(post_title, post_content, self.user.key().id())
            self.redirect('/blog/%s' % str(p.key().id()))

class SinglePostHandler(PostHandler):

    """ Showing a single post. """

    def get(self, post_id):

        post = self.render_post(post_id=post_is)
        self.render("blog/permalink.html", single_post=single_post)


class EditPostHandler(BaseHandler):

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

class LikePostHandler(BaseHandler):

    # get the id from the url "blog/some_id"
    def get(self, post_id):
        Post.add_like(int(post_id), self.user.get_id())
        self.redirect('/blog')

class DeletePostHandler(BaseHandler):

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

class CommentEditHandler(CommentPostHandler):

    def get(self, comment_id):
        self.render_comments(comment_id)

    def post(self, comment_id):
        comment_content = self.request.get("comment_content")
        comment = Comment.by_id(int(comment_id))
        comment.set_content(comment_content)

        self.redirect('/blog')

class CommentDeleteHandler(BaseHandler):

    def get(self, comment_id):
        print "Comment id is: " + str(comment_id)
        self.redirect('/blog')

    def post(self, post_id):
        pass

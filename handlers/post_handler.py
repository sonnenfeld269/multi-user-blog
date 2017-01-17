from base_handler import BaseHandler
import webapp2
from models import Post, User, Comment

#### post-handlers

class PostHandler(BaseHandler):

    """ Responsible for rendering multiple and single posts and comments. """

    def render_posts(self, **params):

        """
            Creates a string of all rendered posts and uses render to show
            them on the blog page.
        """

        if params.has_key('user_posts'):
            posts = params['user_posts']
        else:
            posts = Post.get_all()

        rendered_posts = ""
        for post in posts:
            if params.has_key('comment'):
                print "here"
                rendered_posts += self.render_post(post,params['comment'])
            else:
                rendered_posts += self.render_post(post)

        self.render("blog/blog.html", rendered_posts=rendered_posts)

    def render_post(self, post, comment_to_edit=None):

        """ Renders a single post as a string. """

        """
        TODO
        To keep the code more object-oriented I wanted to have the render_comments() method inside the PostCommentsHandler() class.
        But then I get following error:
        AttributeError: 'NoneType' object has no attribute 'cookies'.
        Thats why I put render_comments into this PostHandler Class.
        """
        #rendered_comments = PostCommentsHandler().render_comments()
        rendered_comments = self.render_comments(post=post, comment_to_edit=comment_to_edit)

        return self.render_str("blog/singlepost.html", p = post, comments=rendered_comments)

    def render_comments(self, post, comment_to_edit=None):

        """ Renders all comments of a single post. """

        rendered_comments = ""
        for comment in post.comments:
            if comment_to_edit and comment.get_id() == comment_to_edit.get_id():
                rendered_comments += self.render_str("blog/editcomment.html", comment=comment_to_edit)
            else:
                rendered_comments += self.render_str("blog/singlecomment.html", p=post, comment=comment)
        return rendered_comments

class BlogHandler(PostHandler):

    """ Responsible for forwarding the request coming from the "/blog" url """

    def get(self):

        """ Calls the method render_posts of the PostHandler class. """

        self.render_posts()

class UserPostHandler(PostHandler):

    """ Show all posts of one user. """

    def get(self):
        user_posts = Post.get_by_user(self.user.get_id())
        self.render_posts(user_posts=user_posts)

class AddPostHandler(BaseHandler):

    """ Responsible for adding a post to the database. """

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
            p = Post.add_post(post_title, post_content, self.user)
            self.redirect('/blog/%s' % str(p.key().id()))

class SinglePostHandler(PostHandler):

    """ Responsible for rendering a single post. """

    def get(self, post_id):
        """
        1. get the post by id
        2. return a single post by rendering "permalink.html"
        """
        single_post = self.render_post(Post.by_id(int(post_id)))
        self.render("blog/permalink.html", single_post=single_post)

class EditPostHandler(BaseHandler):

    """ Responsible for updating a post. """

    def get(self, post_id):
        """
        1. get the post by id
        2. return the edit form by rendering "editpost.html"
        """
        post = Post.by_id(int(post_id))

        if not post:
            self.error(404)
            return

        post.content = post.content.replace('<br>', '\n')
        self.render("/blog/editpost.html", post=post)

    def post(self, post_id):
        """
        1. get the post by id
        2. get the form requests and save them in a parameter list, to store
        the errors
        3. return form if there is an error, else update the post
        """
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
            p = Post.update_post(int(post_id), post_title, post_content)
            self.redirect('/blog/%s' % str(p.get_id()))

class LikePostHandler(BaseHandler):

    """ Responsible for adding a like to a single post. """

    def get(self, post_id):
        """
        1. call the add_like method with the post and user id as parameters
        2. redirect to "/blog"
        """
        Post.add_like(int(post_id), self.user.get_id())
        self.redirect('/blog')

class DeletePostHandler(BaseHandler):

    """ Responsible for deleting a single post. """

    def get(self, post_id):
        """
        1. call the delete_post method with the post id as the parameter
        2. redirect to "/blog"
        """
        Post.delete_post(post_id)
        self.redirect('/blog')

#### comment-handlers

class PostCommentsHandler(BaseHandler):

    """ Responsible for adding a comment to a single post. """

    def get(self, post_id):
        """
        No need to have a get method, because "Show Comments"-Button uses jquery
        """
        pass

    def post(self, post_id):
        """
        1. get the comment content
        2. add the comment to the post
        3. redirect to "/blog"
        """
        comment_content = self.request.get("comment_content")
        Post.add_comment(int(post_id), int(self.user.get_id()), comment_content)
        self.redirect('/blog')

class CommentEditHandler(PostHandler):

    """ Responsible for updating a comment of a single post. """

    def get(self, post_id, comment_id):
        post = Post.by_id(int(post_id))
        comment = Comment.by_id(int(comment_id))
        self.render_posts(comment=comment)

    def post(self, post_id, comment_id):
        comment_content = self.request.get("comment_content")
        comment = Comment.by_id(int(comment_id))
        comment.set_content(comment_content)
        self.redirect('/blog')

class CommentDeleteHandler(BaseHandler):

    """ Responsible for deleting a comment of a single post. """

    def get(self, post_id, comment_id):
        comment = Comment.by_id(int(comment_id))
        comment.delete_comment()
        self.redirect('/blog')

    def post(self, post_id):
        pass

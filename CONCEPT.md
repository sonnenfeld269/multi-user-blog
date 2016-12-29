# Concept

## Project structure

- multi-user-blog/
    - handlers/
        - base_handler.py - containing webapp2 module
        - post_handler.py - responsible for post-related requests
        - user_handler.py - responsible for user-related requests
    - main.py - containing all the url-mapping to handlers
    - models.py - containing our User and Post class (db.Model)

## Implementation

### Database Layer

1 : * relation between User : Post
1 : * relation between Post : Comment
1 : * relation between User : Comment

Which results in following classes

```
class Post(db.Model,BaseHandler):

    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    author = db.ReferenceProperty(User, required = True, collection_name="posts")
    likes = db.IntegerProperty(required = False,default=0)
    liked_by_users = db.StringListProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    show_comments = db.BooleanProperty(default=False)

    ## getter-setter-methods

class User(db.Model, BaseHandler):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    ## getter-setter-methods

class Comment(db.Model):
    post = db.ReferenceProperty(Post, required = True, default=None, collection_name="comments")
    user = db.ReferenceProperty(User, required = True)
    content = db.StringProperty(required = True,multiline=True)

    ## getter-setter-methods
```

### Service Layer

BaseHandler is our parent module, which is responsible for handling the responses to the browser using jinja2.

![handler inheritance](webapp.png)

#### User actions

Here you can see the user actions and the handlers that will be called on that action.

|URL, HANDLER           |POST/GET | ACTION |
|-----------------------|---------|--------|
|('/', MainPageHandler)|GET|show all blog posts|
|('/register', RegisterHandler)|GET/POST|show register form or submit|
|('/login', LoginHandler)|GET/POST|show login form or submit|
|('/logout', LogoutHandler)|GET|logout the user|
|('/blog', BlogHandler)|GET|show all blog posts|
|('/blog/addpost', AddPostHandler)|GET/POST|show add post form and submit|
|('/blog/myposts', UserPostHandler)|GET|show all posts of user|
|('/blog/([0-9]+)', SinglePostHandler)|GET|show single post|
|('/blog/([0-9]+)/comments', PostCommentsHandler)|GET/POST|show all comments of post or submit|
|('/blog/([0-9]+)/edit', EditPostHandler)|GET/POST|show edit form of post or submit|
|('/blog/([0-9]+)/like', LikePostHandler)|POST|add like to post|
|('/blog/([0-9]+)/delete', DeletePostHandler)|POST|delete a post|
|('/blog/([0-9]+)/comment/([0-9]+)/edit', CommentEditHandler)|GET/POST|show edit form or submit|
|('/blog/([0-9]+)/comment/([0-9]+)/delete', CommentDeleteHandler)|POST|delete a comment|


#### Code-Examples with pseudo-code comments

This part shows us the implementation of 3 handlers in detail.
The **BlogHandler**, **AddPostHandler** and **SinglePostHandler**.

1. Implementing **show all blog posts** action

    |('/blog', BlogHandler)|GET|show all blog posts|
    |-----------------|---------|--------|

    As we can see, this should be implemented as GET, because the user just requests
    the fetched data from the database. There is no data to changed on the database.
    When the user points the the url `/blog`, the `get()` method of BlogHander
    will be called. Below you can see the class with some pseude-code

    ```
    class BlogHandler(BaseHandler):

        def get(self):
            self.render_posts()

        def render_posts(self, **kw):

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

            self.render("blog/blog.html", rendered_posts=rendered_posts, **kw)
    ```

2. Implementing **show add post form and submit** action

    |('/blog/addpost', AddPostHandler)|GET/POST|show add post form and submit|
    |-----------------|---------|--------|

    Here we have to use cases. If the user clicks on **add post**, the `get()`
    method should be called, where a form is returned to the user. And if
    the user clicks then on submit, we want to call our `post()` method, which
    adds the post to the database.

    ```
    class AddPostHandler(BaseHandler):

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
                p = Post.add_post(post_title, post_content, int(self.user))
                self.redirect('/blog/%s' % str(p.key().id()))
    ```

    At the last line we see `self.redirect('/blog/%s' % str(p.key().id()))`,
    which will redirect us to the `/blog/([0-9]+)` url as shown in our
    user action table

    |('/blog/([0-9]+)', SinglePostHandler)|GET|show single post|
    |-----------------|---------|--------|

    And the Implemention of SinglePostHandler is quite simple. It should render
    the given single_post:

    ```
    class SinglePostHandler(BaseHandler):

        def get(self, post_id):
            """
            1. get the post by post_id and save it into single_post
            2. render it using "permalink.html" and single_post as the parameter
            """
            single_post = Post.by_id(int(post_id)).render()
            self.render("blog/permalink.html", single_post=single_post)
    ```

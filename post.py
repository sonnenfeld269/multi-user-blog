from google.appengine.ext import db
import main

class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    @classmethod
    def by_id(cls, pid):
        return Post.get_by_id(pid)

    @classmethod
    def get_all(cls):
        return Post.all().order('-created')

    @classmethod
    def add_post(cls, post_title, post_content):

        p = Post(title = post_title,content=post_content)
        p.put()
        return p

    """
    with an own render function it is a lot easier to render the posts
    on different pages
    """
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("blog/singlepost.html", p = self)

import hashlib, hmac, random
from string import letters
from google.appengine.ext import db
import main

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = cls.make_pw_hash(name, pw)
        u = User(name = name,
                 pw_hash = pw_hash,
                 email = email)
        u.put()
        return u

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and cls.valid_pw(name, pw, u.pw_hash):
            return u

    @classmethod
    def make_salt(cls, length = 5):
        return ''.join(random.choice(letters) for x in xrange(length))

    @classmethod
    def make_pw_hash(cls, name, pw, salt = None):
        if not salt:
            salt = cls.make_salt()
        h = hashlib.sha256(name + pw + salt).hexdigest()
        return '%s,%s' % (salt, h)

    @classmethod
    def valid_pw(cls, name, password, h):
        salt = h.split(',')[0]
        return h == cls.make_pw_hash(name, password, salt)

class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    author = db.ReferenceProperty(User, required = False)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    @classmethod
    def by_id(cls, pid):
        return Post.get_by_id(pid)

    def get_id(self):
        return Post.get_by_id(self)

    @classmethod
    def get_all(cls):
        return Post.all().order('-created')

    @classmethod
    def add_post(cls, post_title, post_content, author_id):

        p = Post(title = post_title,content=post_content,author=User.by_id(author_id))
        p.content = p.content.replace('\n', '<br>')
        p.put()
        return p

    @classmethod
    def delete_post(cls, pid):
        print "inside delete"
        key = db.Key.from_path('Post', int(pid))
        post = db.get(key)
        post.delete()


    """
    with an own render function it is a lot easier to render the posts
    on different pages
    """
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("blog/singlepost.html", p = self)

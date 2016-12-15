from google.appengine.ext import db
import random
import hashlib, hmac
from string import letters

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
        return User(name = name,
                    pw_hash = pw_hash,
                    email = email)

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

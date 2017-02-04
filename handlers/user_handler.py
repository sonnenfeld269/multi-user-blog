from base_handler import BaseHandler
from models import User
import re


class RegisterHandler(BaseHandler):

    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    MAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

    def get(self):
        self.render("auth/register.html")

    def post(self):
        # get the request from the http header
        user_name = self.request.get("name")
        user_password = self.request.get("password")
        user_password_repeat = self.request.get("password_repeat")
        user_email = self.request.get("email")

        # a parameter list to store the values and errors
        # user_name and user_email are the values to be kept in the form
        param_list = dict(user_name=user_name, user_email=user_email)
        any_error = False

        name_error = ""
        if user_name is None or not self.valid_username(user_name):
            param_list['name_error'] = "Username not valid!"
            any_error = True

        password_error = ""
        if not self.valid_password(user_password):
            param_list['password_error'] = "Password not valid!"
            any_error = True

        password_repeat_error = ""
        if user_password != user_password_repeat:
            param_list['password_repeat_error'] = "Passwords do not match!"
            any_error = True

        email_error = ""
        if user_email is None or not self.valid_email(user_email):
            param_list['email_error'] = "Email not valid!"
            any_error = True

        if not any_error:
            # if user exists, re-render form with error message
            if User.by_name(user_name):
                self.render("auth/register.html",
                            name_error="User already exists!")
            else:
                u = User.register(user_name, user_password, user_email)
                self.login(u)
                self.redirect("/welcome")
        else:
            self.render("auth/register.html", **param_list)

    def valid_username(self, username):
        return self.USER_RE.match(username)

    def valid_password(self, password):
        return self.PASS_RE.match(password)

    def valid_email(self, email):
        return self.MAIL_RE.match(email)


class LoginHandler(BaseHandler):

    def get(self):
        self.render("auth/login.html")

    def post(self):
        # get the request from the http header
        user_name = self.request.get("name")
        user_password = self.request.get("password")
        any_error = False
        param_list = dict(user_name=user_name)

        if not user_name:
            param_list['name_error'] = "Username is missing!"
            any_error = True
        if not user_password:
            param_list['password_error'] = "Password is missing!"
            any_error = True

        if any_error:
            self.render("auth/login.html", **param_list)
        else:
            u = User.login(user_name, user_password)
            if not u:
                param_list['login_error'] = "Username or Password is invalid!"
                self.render("auth/login.html", **param_list)
            else:
                self.login(u)
                self.redirect("/welcome")


class LogoutHandler(BaseHandler):

    def get(self):
        self.logout()
        self.redirect('/login')


class WelcomeHandler(BaseHandler):
    """Show a welcome page when user registered of logged in successfully
    """

    def get(self):
        if self.user:
            self.render("auth/welcome.html")
        else:
            self.redirect("/login")

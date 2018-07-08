from google.appengine.api import users
from webapp2 import redirect_to
from app.settings import ADMINS


def admin_required(handler):
    def check_login(self, *args, **kwargs):
        user = users.get_current_user()
        if user:
            email = user.email()
            if email in ADMINS:
                return handler(self, *args, **kwargs)
            else:
                return redirect_to("forbidden")
        else:
            return redirect_to("login")
    return check_login
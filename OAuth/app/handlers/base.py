# From https://github.com/ramuta/basic-webapp2-template
# Handles simplifying our calls
import os
import jinja2
import webapp2
import urllib
from google.appengine.api import users
from app.utils.decorators import admin_required

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               extensions=['jinja2.ext.autoescape'],
                               autoescape=False)

CLIENT_ID = "p-jcoLKBynTLew"
CLIENT_SECRET = "gko_LXELoV07ZBNUXrvWZfzE3aI"
REDIRECT_URI = "http://localhost:65010/reddit_callback"

class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        user = users.get_current_user()
        if user:
            params["user"] = user
        t = jinja_env.get_template(view_filename)
        self.write(t.render(params))
    
    def make_authorization_url():
	    # Generate a random string for the state parameter
	    # Save it for use later to prevent xsrf attacks
	    from uuid import uuid4
	    state = str(uuid4())
	    save_created_state(state)
	    params = {"client_id": CLIENT_ID,
			  "response_type": "code",
			  "state": state,
			  "redirect_uri": REDIRECT_URI,
			  "duration": "temporary",
			  "scope": "identity"}
	    url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.urlencode(params)
	    return url

class MainHandler(Handler):
    def get(self):
        self.render_template("test.html")

class OAuthHandler(Handler):
    def get(self):
        self.render_template("test.html")

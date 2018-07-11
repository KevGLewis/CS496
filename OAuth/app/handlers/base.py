# From https://github.com/ramuta/basic-webapp2-template
# Handles simplifying our calls
import os
import jinja2
import logging
import webapp2
import urllib
import json
from uuid import uuid4
from urllib import urlencode
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               extensions=['jinja2.ext.autoescape'],
                               autoescape=False)

CLIENT_ID = "1007134695985-f378vpoct42aqooctd1hl5tvnrum1pke.apps.googleusercontent.com"
CLIENT_SECRET = "JAvADPuxKJDYgLRZzCsexVJU"
#REDIRECT_URI = "https://cs496oauthtwo.appspot.com/OAuth_callback"
REDIRECT_URI = "http://localhost:8080/OAuth_callback"
FILE_NAME = "variables_save.txt"
NDB_ID = 1

# [START databaseClasses]
class State_Model(ndb.Model):
    state = ndb.StringProperty()

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
        t = jinja_env.get_template(view_filename)
        self.write(t.render(params))
    
    def make_authorization_url(self):
        # Derived from https://github.com/reddit-archive/reddit/wiki/OAuth2-Python-Example
        state = str(uuid4())
        self.save_state(state)
        params = {"client_id": CLIENT_ID,
			  "response_type": "code",
			  "state": state,
			  "redirect_uri": REDIRECT_URI,
			  "scope": "email"}
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.urlencode(params)
        return url

    def save_state(self, stateIn):
        # check if the key has already been created
        if(self.get_key_check(NDB_ID)):
            new_state = State_Model(state=stateIn, id=NDB_ID)
            new_state.put()
        else:
            s = ndb.State_Model(State_Model, id=NDB_ID).get()
            s.state = stateIn
            s.put()

    def is_valid_state(self, stateIn):
        for s in State_Model.query().fetch():
            if s.state == stateIn:
                return True
        return False

    def get_state(self):
        if(self.get_key_check(NDB_ID)):
            s = ndb.Key(State_Model, NDB_ID).get()
            return s.state;

    def get_key_check(self, id):
        try:
            s = ndb.Key(State_Model, id).get()
        except (ValueError, TypeError, ProtocolBufferDecodeError):
            return False
        
        return True

class MainHandler(Handler):
    def get(self):
        url = self.make_authorization_url();
        self.render_template("test.html", {"googleURL": url})

class OAuthHandler(Handler):
    def get(self):
        code = self.request.GET['code']
        state = self.request.GET['state']
        if(self.is_valid_state(state) != True):
            logging.info("Not the right code")
            self.render_template("403.html")
            return
        gp_results = json.loads(self.get_googlep_info(json.loads(self.get_token(code))))

        html_data = { "clientURL": gp_results["url"],
                    "clientName": gp_results["displayName"],
                    "state": state}

        self.render_template("OAuth_Redirect.html", html_data)

    def get_token(self, code):
        # Compile the payload data
        payload_data = {
		    "code": code,
            "client_id": CLIENT_ID,
			"client_secret": CLIENT_SECRET,
			"redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
            }
            
        # Make the request to google here
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            result = urlfetch.fetch(
                url='https://www.googleapis.com/oauth2/v4/token',
                payload=urlencode(payload_data),
                method=urlfetch.POST,
                headers=headers)
            logging.info("The result is" + result.content)
            token_json = result.content
            return token_json
        except urlfetch.Error:
            logging.exception('Caught exception fetching url')
            self.render_template("403.html")
            return

    def get_googlep_info(self, token):
                # Make the request to google here
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'Authorization': token["token_type"] + " " + token["access_token"]}
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)
            return result.content
        except urlfetch.Error:
            logging.exception('Caught exception fetching url')
            self.render_template("403.html")
            return

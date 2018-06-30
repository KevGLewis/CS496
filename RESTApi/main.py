#!/usr/bin/env python

# [START imports]
import urllib

from google.appengine.ext import ndb
import webapp2
import json

parent_boat = "parent_boat"
parent_slip = "parent_slip"

# [START databaseClasses]
class Boat(ndb.Model):
    name = ndb.StringProperty()
    type = ndb.StringProperty()
    length = ndb.IntegerProperty()
    at_sea = ndb.BooleanProperty()

    def query_all_boats(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key)

class Slip(ndb.Model):
    number = ndb.IntegerProperty()
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty()
# [END databaseClasses]

# [START handlers]
class BoatHandler(webapp2.RequestHandler):
    # add a boat
    def post(self):
        parent_key = ndb.Key(Boat, parent_boat)
        boat_data = json.loads(self.request.body)
        new_boat = Boat(name=boat_data["name"], type=boat_data["type"],
                        length=boat_data["length"], at_sea=True, parent=parent_key)
        new_boat.put()
        boat_dict = new_boat.to_dict()
        boat_dict["id"] = new_boat.key.urlsafe() 
        self.response.write(json.dumps(boat_dict))

    # get a boat
    def get(self, id=None):
        if id:
            b = ndb.Key(urlsafe = id).get()
            b_dict = b.to_dict()
            b_dict["id"] = id
            self.response.write(json.dumps(b_dict))
        else:
            self.response.write(json.dumps([dict(b.to_dict(), **dict(id=b.key.urlsafe())) for b in Boat.query().fetch()]))

    def delete(self, id=None):
        if id:
            b = ndb.Key(urlsafe = id).get()
            # the parent represents the slip, so we need to clear the slip

class SlipHandler(webapp2.RequestHandler):
    # add a slip
    def post(self):
        slip_data = json.loads(self.request.body)
        new_slip = Slip(number=slip_data["number"], current_boat=None,
                        arrival_date=None)
        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict["id"] = new_slip.key.urlsafe() 
        self.response.write(json.dumps(slip_dict))

    # get a slip
    def get(self, id=None, boat_id=None):
        # A specific slip
        if id:
            # return the information about the boat in the slip
            if boat_id:
                
            # return information about a specific slip
            else: 
                s = ndb.Key(urlsafe = id).get()
                s_dict = s.to_dict()
                s_dict["id"] = id
                self.response.write(json.dumps(s_dict))
        # All the slips
        else:
            self.response.write(json.dumps([dict(s.to_dict(), **dict(id=s.key.urlsafe())) for s in Slip.query().fetch()]))

# [END handlers]

# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Hello World")
# [END main_page]


# [START app]
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boat', BoatHandler),
    ('/boat/(.*)', BoatHandler),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler)
], debug=True)
# [END app]
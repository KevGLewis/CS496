#!/usr/bin/env python

# [START imports]
import urllib
import logging

from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
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

# [Start utility functions]
def get_key_check(self, id):
    try:
        s = ndb.Key(urlsafe = id).get()
    except (ValueError, TypeError, ProtocolBufferDecodeError):
        self.response.set_status(510)
        self.response.write("Bad ID")
        return None
    
    return s
# [End utility functions]



# [START handlers]
class BoatHandler(webapp2.RequestHandler):
    # add a boat
    def post(self):
        boat_data = json.loads(self.request.body)
        new_boat = Boat(name=boat_data["name"], type=boat_data["type"],
                        length=boat_data["length"], at_sea=True)
        new_boat.put()
        boat_dict = new_boat.to_dict()
        boat_dict["id"] = new_boat.key.urlsafe() 
        self.response.write(json.dumps(boat_dict))

    # get a boat
    def get(self, id=None):
        if id:
            b = get_key_check(self, id)
            if(b == None):
                self.response.set_status(500)
                return
            b_dict = b.to_dict()
            b_dict["id"] = id
            self.response.write(json.dumps(b_dict))
        else:
            self.response.write(json.dumps([dict(b.to_dict(), **dict(id=b.key.urlsafe())) for b in Boat.query().fetch()]))

    def patch(self, id=None):
        if id:
            b = get_key_check(self, id)
            if(b == None):
                return

            boat_data = json.loads(self.request.body)

            # Verify the values exist before adding to json
            if "name" in boat_data:
                b.name = boat_data["name"] if type(boat_data["name"]) is str else b.name
            if "type" in boat_data:
                b.type = boat_data["type"] if type(boat_data["type"]) is str else b.type
            if "length" in boat_data:
                b.length = boat_data["length"] if type(boat_data["length"]) is int else b.length
            if "at_sea" in boat_data:
                # If we are going out to sea
                if boat_data["at_sea"] == True:
                    # Let's free the slip
                    for s in Slip.query().fetch():
                        if s.current_boat == b.key.urlsafe():
                            s.current_boat = None
                            s.arrival_date = None
                            s.put()
                    # Put the boat out to sea
                    b.at_sea = True;
                else:
                    b.at_sea = False;
            b.put()
            b_dict = b.to_dict()
            b_dict["id"] = id
            self.response.write(json.dumps(b_dict))
        else:
            self.response.set_status(500)
            self.response.write("No ID Provided") 

    def delete(self, id=None):
        if id:
            #Try to grab the boat from the id
            b = get_key_check(self, id)
            if(b == None):
                return
             # Let's free the slip
            for s in Slip.query().fetch():
                if s.current_boat == b.key.urlsafe():
                    s.current_boat = None
                    s.arrival_date = None
                    s.put()

            b.key.delete()
        else:
            self.response.set_status(500)
            self.response.write("No ID Provided") 

class SlipHandler(webapp2.RequestHandler):
    # add a slip
    def post(self):
        slip_data = json.loads(self.request.body)
        # Ensure the required data exists before creating the slip
        if("number" in slip_data):
            new_slip = Slip(number=slip_data["number"], current_boat=None,
                            arrival_date=None)
        else:
            self.response.set_status(500)
            self.response.write("Missing Data")
            return

        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict["id"] = new_slip.key.urlsafe() 
        self.response.write(json.dumps(slip_dict))

    def patch(self, id=None):
        if (id == None):
            self.response.set_status(500)
        else:
            # Try to get the slip
            s = get_key_check(self, id)
            if(s == None):
                return
                
            data = json.loads(self.request.body)

            if "number" in data:
                s.number = data["number"] if type(data["number"]) is int else s.number

            #verify the data is there
            if "current_boat" in data and "arrival_date" not in data:
                self.response.set_status(510)
                self.response.write("Missing Arrival Date")
                return
            
            if "current_boat" in data and "arrival_date" in data:
                # Check if there is already a boat in the slip
                if s.current_boat != None:
                    self.response.set_status(403)
                    self.response.write("Slip is already occuppied")
                    return

                #Try to grab the boat from the id
                b = get_key_check(self, data["current_boat"])
                if(b == None):
                    return

                # Update the boat including add slip as parent
                b.at_sea = False
                b.put()
                
                # Update the slip
                s.current_boat = data["current_boat"]
                s.arrival_date = data["arrival_date"]
                
            s.put()
            # return the updated slip information
            slip_dict = s.to_dict()
            slip_dict["id"] = s.key.urlsafe() 
            self.response.write(json.dumps(slip_dict))

    # get a slip
    def get(self, id=None):
        # A specific slip
        if id:  
            # Try to get the slip
            s = get_key_check(self, id)
            if(s == None):
                self.response.set_status(500)
                return

            s_dict = s.to_dict()
            s_dict["id"] = id
            self.response.write(json.dumps(s_dict))
        # All the slips
        else:
            self.response.write(json.dumps([dict(s.to_dict(), **dict(id=s.key.urlsafe())) for s in Slip.query().fetch()]))

    def delete(self, id=None):
        if id:
            #Try to grab the boat from the id
            s = get_key_check(self, id)
            if(s == None):
                return
            # Set the boat currently in the slip out to sea
            b = get_key_check(self, s.current_boat)
            if (b == None):
                return
            b.at_sea = True
            b.put()
            s.key.delete()
        else:
            self.response.set_status(500)
            self.response.write("No ID Provided")

class SlipBoatHandler(webapp2.RequestHandler):
    # add a slip
    def get(self, id=None):
        # Get the slip key
        print("Slip Boat Handler")
        s = get_key_check(self, id)
        if(s == None):
            return

        # Get the boat
        slip_boat = get_key_check(self, s.current_boat)
        if(slip_boat == None):
            return
        
        b_dict = slip_boat.to_dict()
        b_dict["id"] = slip_boat.key.urlsafe() 
        self.response.write(json.dumps(b_dict))

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
    ('/boats', BoatHandler),
    ('/boats/(.*)', BoatHandler),
    ('/slips', SlipHandler),
    ('/slips/(.*)/boat', SlipBoatHandler),
    ('/slips/(.*)', SlipHandler)
], debug=True)
# [END app]
#!/usr/bin/env python

# [START imports]
import urllib
import logging

from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from google.oauth2 import id_token
from google.auth.transport import requests
import webapp2
import json

parent_boat = "parent_boat"
parent_slip = "parent_slip"

# [START databaseClasses]
class Book(ndb.Model):
    title = ndb.StringProperty()
    author = ndb.StringProperty()
    length = ndb.IntegerProperty()
    imageURL = ndb.StringProperty()
    checked_out = ndb.BooleanProperty()

    def UpdateBook(self, book_data):
        # Verify the values exist before adding to json
        if "title" in book_data:
            self.title = book_data["title"] if type(book_data["title"]) is str else self.title
        if "author" in book_data:
            self.author = book_data["author"] if type(book_data["author"]) is str else self.author
        if "imageURL" in book_data:
            self.imageURL = book_data["imageURL"] if type(book_data["imageURL"]) is str else self.imageURL
        if "length" in book_data:
            self.length = book_data["length"] if type(book_data["length"]) is int else self.length
        if "checked_out" in book_data:
            # If we are trying to return the book
            if book_data["checked_out"] == False:
                # Let's return the book to the library
                self.ReturnBook()
                
            else:
                self.checked_out = True;

        def ReturnBook(self):
            for s in Patron.query().fetch():
                if b.key.urlsafe() in s.checked_out_books:
                    s.checked_out_books.remove(b.key.urlsafe())
                    s.put()
            # Return the book to the library
            self.checked_out = False;

class Patron(ndb.Model):
    userid = ndb.IntegerProperty()
    checked_out_books = ndb.StringProperty(repeated=True)

    def UpdateBooks(self, patron_data):
        if "books" in patron_data:
            self.books = patron_data["book"]
            for val in self.books:
                book = get_key_check(val)
                if book != None:
                    book.checked_out = False
                    book.put()

    def CompileAllBooks(self):
        bookCompilation = []
        for val in self.books:
            book = get_key_check(val)
            if book != None:
                bookCompilation.append(book.to_dict())
                book.put()
        return bookCompilation

    def ReturnAllBooks(self):
        for val in self.books:
            book = get_key_check(val)
            if book != None:
                book.checked_out = False
                book.put()

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
class BookHandler(webapp2.RequestHandler):
    # add a boat
    def post(self):
        book_data = json.loads(self.request.body)
        new_book = Book(title=book_data["title"], author=book_data["author"],
                        length=book_data["length"], imageURL=book_data["imageURL"], checked_out=False)
        new_book.put()
        book_dict = new_book.to_dict()
        book_dict["id"] = new_book.key.urlsafe() 
        self.response.write(json.dumps(book_dict))

    # get a book
    def get(self, id=None):
        if id:
            b = get_key_check(self, id)
            if(b == None):
                self.response.set_status(406)
                return
            b_dict = b.to_dict()
            b_dict["id"] = id
            self.response.write(json.dumps(b_dict))
        else:
            self.response.write(json.dumps([dict(b.to_dict(), **dict(id=b.key.urlsafe())) for b in Book.query().fetch()]))

    def patch(self, id=None):
        if id:
            b = get_key_check(self, id)
            if(b == None):
                return

            b.UpdateBook(json.loads(self.request.body))
            b.put()
            b_dict = b.to_dict()
            b_dict["id"] = id
            self.response.write(json.dumps(b_dict))
        else:
            self.response.set_status(406)
            self.response.write("No ID Provided") 

    def delete(self, id=None):
        if id:
            #Try to grab the boat from the id
            b = get_key_check(self, id)
            if(b == None):
                return
             # Let's free the slip
            b.ReturnBook()

            b.key.delete()
        else:
            self.response.set_status(500)
            self.response.write("No ID Provided") 

class PatronHandler(webapp2.RequestHandler):
    # add a slip
    def post(self):
        patron_data = json.loads(self.request.body)
        # Ensure the required data exists before creating the slip
        if("userid" in patron_data):
            new_patron = Slip(userid=patron_data["userid"], checked_out_books=None)
        else:
            self.response.set_status(500)
            self.response.write("Missing Data")
            return

        new_patron.put()
        patron_dict = new_patron.to_dict()
        self.response.write(json.dumps(patron_dict))

    def patch(self, id=None):
        if (id == None):
            self.response.set_status(406)
        else:
            # Try to get the paron
            s = Patron.query(Patron.userid == id)
            if(s == None):
                return
                
            s.UpdateBooks(json.loads(self.request.body))
                
            s.put()
            # return the updated slip information
            patron_dict = s.to_dict()
            self.response.write(json.dumps(patron_dict))

    # get a slip
    def get(self, id=None):
        # A specific slip
        if id:  
            # Try to get the slip
            s = Patron.query(Patron.userid == id)
            if(s == None):
                self.response.set_status(500)
                return

            s_dict = s.to_dict()
            self.response.write(json.dumps(s_dict))
        # All the slips
        else:
            self.response.write(json.dumps([dict(s.to_dict() for s in Slip.query().fetch()]))

    def delete(self, id=None):
        if id:
            #Try to grab the Patron
            s = Patron.query(Patron.userid == id)
            if(s == None):
                return
            s.ReturnAllBooks()
            s.key.delete()
        else:
            self.response.set_status(500)
            self.response.write("No ID Provided")

class PatronBookHandler(webapp2.RequestHandler):
    # add a slip
    def get(self, id=None):
        # Get the slip key
        print("Patron Book Handler")
        p = Patron.query(Patron.userid == id)
        if(p == None):
            self.response.set_status(500)
            self.response.write("Bad ID Provided")
            return
    
        self.response.write(json.dumps(p.CompileAllBooks()))

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
    ('/boats'BookHandler),
    ('/boats/(.*)'BookHandler),
    ('/patrons', PatronHandler),
    ('/patrons/(.*)/books', PatronBookHandler),
    ('/patrons/(.*)', PatronHandler)
], debug=True)
# [END app]
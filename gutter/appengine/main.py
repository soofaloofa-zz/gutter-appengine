"""
Application entry point.
"""
import webapp2


ROUTES = [webapp2.SimpleRoute('/gutter/?',
                              handler='gutter.appengine.handlers.IndexHandler',
                              name='index'), ]
APP = webapp2.WSGIApplication(ROUTES)

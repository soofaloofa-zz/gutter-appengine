"""
Test app for Gutter App Engine.
"""
import os
import sys

sys.path[0:0] = [
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib'),
]

from webapp2 import WSGIApplication, Route

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

CONFIG = {
    'webapp2_extras.jinja2': {
        'template_path': os.path.join(CURRENT_PATH, 'templates')
    }
}

ROUTES = [
    Route('/', handler='views.TestView'),
]

APP = WSGIApplication(ROUTES, debug=True, config=CONFIG)

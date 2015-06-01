"""
Models
"""
from google.appengine.ext import ndb


class SwitchModel(ndb.Model):
    """
    A datastore model for storing switches.
    Used by datastoredict.
    """
    value = ndb.PickleProperty()

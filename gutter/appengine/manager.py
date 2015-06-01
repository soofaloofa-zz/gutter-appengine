"""
Default manager instance
"""
from gutter.client.models import Manager
from gutter.appengine.models import SwitchModel
from datastoredict import DatastoreDict


default_manager = Manager(
    storage=DatastoreDict(SwitchModel),
    autocreate=True,
)

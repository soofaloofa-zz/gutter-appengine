"""
handlers
"""
import os
import webapp2
from webapp2_extras import jinja2

from gutter.client.default import gutter

import forms


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_PATH = os.path.join(CURRENT_PATH, 'templates')


class BaseHandler(webapp2.RequestHandler):
    """
    Sets up Jinja templating path.
    """

    def render_response(self, template, **context):
        """
        Renders a template and writes the result to the response.
        """
        app = webapp2.WSGIApplication.active_instance
        config = {'template_path': TEMPLATE_PATH, }
        jinja = jinja2.Jinja2(app, config=config)
        rv = jinja.render_template(template, **context)
        self.response.write(rv)


class IndexHandler(BaseHandler):
    """
    Managing the list of switches.
    """

    def get(self, errors=None):
        """
        Displays the list of enabled switches.
        """
        new_switch = forms.SwitchForm()
        new_condition = forms.ConditionForm()
        # Used built-in function map, pylint: disable=W0141
        switches = sorted(map(forms.SwitchForm.from_object, gutter.switches),
                          key=lambda x: x.name.data)

        context = {
            'new_switch': new_switch,
            'new_condition': new_condition,
            'switches': switches,
            'errors': errors,
        }
        self.render_response('index.html', **context)

    def post(self):
        """
        Create/Update an individual switch.
        """
        switch = forms.SwitchForm(self.request.POST)

        if not switch.validate():
            return self.get(errors=switch.errors)

        # Delete a switch
        if switch.delete.data:
            gutter.unregister(switch.name.data)
            return self.get()

        # Create/update the switch
        switch = switch.to_object()
        gutter.register(switch)

        return self.redirect('/gutter/')

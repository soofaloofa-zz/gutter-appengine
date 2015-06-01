"""
Views for test app.
"""
import webapp2
from webapp2_extras import jinja2

# from gutter.client.default import gutter


class TestView(webapp2.RequestHandler):
    """
    An HTML view for an end-user.
    """
    @webapp2.cached_property
    def jinja2(self):
        """ Returns a Jinja2 renderer cached in the app registry. """
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, template, **context):
        """ Renders a template and writes the result to the response. """
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)

    def get(self):
        """
        Return the response
        """
        context = {
            'switches': {
                # Test your switches here
                # 'global': gutter.active('global'),
            }.items()
        }
        rv = self.jinja2.render_template('index.html', **context)
        self.response.write(rv)

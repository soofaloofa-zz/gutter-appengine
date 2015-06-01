from fixtures import GaeTestCase
from gutter.client.models import Switch
from gutter.client import arguments

from gutter.appengine.forms import SwitchForm
from gutter.appengine import registry


class User(arguments.Container):

    nickname = arguments.String(lambda self: self.input.nickname())
    email = arguments.String(lambda self: self.input.email())
    user_id = arguments.String(lambda self: self.input.user_id())


class SwitchFormToObjectTests(GaeTestCase):

    def setUp(self):
        super(SwitchFormToObjectTests, self).setUp()
        registry.arguments.register(User.email)
        registry.arguments.register(User.nickname)
        registry.arguments.register(User.user_id)

    def tearDown(self):
        super(SwitchFormToObjectTests, self).tearDown()
        registry.arguments = registry.ArgumentsDict()

    def test_creates_switch_from_form_data(self):
        switch = SwitchForm(state=1).to_object()
        self.assertEquals(type(switch), Switch)

    def test_returns_switch_with_no_conditions(self):
        switch = SwitchForm(state=1).to_object()
        self.assertEquals(len(switch.conditions), 0)

    def test_returns_all_switch_data_from_form(self):
        form = SwitchForm(name='new-switch',
                          label='group one',
                          description='a cool switch',
                          state=2,
                          compounded=False,
                          concent=True)

        switch = form.to_object()

        self.assertEquals(switch.name, 'new-switch')
        self.assertEquals(switch.label, 'group one')
        self.assertEquals(switch.description, 'a cool switch')
        self.assertEquals(switch.state, 2)
        self.assertFalse(switch.compounded)
        self.assertTrue(switch.concent)

    def test_returns_conditions_from_form(self):
        form = SwitchForm(state=2)

        condition = {
            'argument': 'User.email',
            'negative': '1',
            'operator': 'between'
        }

        form.conditions.append_entry(condition)

        switch = form.to_object()

        self.assertEquals(switch.conditions[0].argument, User)
        self.assertEquals(switch.conditions[0].negative, True)


class SwitchFormFromObjectTests(GaeTestCase):

    def setUp(self):
        super(SwitchFormFromObjectTests, self).setUp()
        registry.arguments.register(User.email)
        registry.arguments.register(User.nickname)
        registry.arguments.register(User.user_id)

    def test_creates_form_from_switch_objecdt(self):
        switch = SwitchForm(name='new-switch',
                            label='group one',
                            description='a cool switch',
                            state=2,
                            compounded=False,
                            concent=True)
        form = SwitchForm.from_object(switch)

        self.assertEquals(form.name.data.data, 'new-switch')
        self.assertEquals(form.label.data.data, 'group one')
        self.assertEquals(form.description.data.data, 'a cool switch')

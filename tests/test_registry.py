from fixtures import GaeTestCase
from gutter.client import arguments

from gutter.appengine import registry


class User(arguments.Container):

    nickname = arguments.String(lambda self: self.input.nickname())
    email = arguments.String(lambda self: self.input.email())
    user_id = arguments.String(lambda self: self.input.user_id())


class OperatorsDictTests(GaeTestCase):
    def test_operators_create_correct_choices(self):
        choices = registry.operators.as_choices
        self.assertEquals(
            choices, [('Comparable',
                       [('between', 'Between'), ('equals', 'Equal To'),
                        ('before', 'Less Than'),
                        ('less_than_or_equal_to', 'Less Than Or Equal To'),
                        ('more_than', 'More Than'),
                        ('more_than_or_equal_to', 'More Than Or Equal To')]),
                      ('Identity', [('true', 'True')]),
                      ('Misc',
                       [('percent_range', 'In The Percentage Range Of'),
                        ('percent', 'Within The Percentage Of')])])

    def test_operators_create_correct_arguments(self):
        args = registry.operators.arguments
        self.assertEquals(args, {
            'more_than_or_equal_to': ('lower_limit', ),
            'more_than': ('lower_limit', ),
            'less_than_or_equal_to': ('upper_limit', ),
            'percent': ('percentage', ),
            'equals': ('value', ),
            'percent_range': ('lower_limit', 'upper_limit'),
            'between': ('lower_limit', 'upper_limit'),
            'true': (),
            'before': ('upper_limit', )
        })


class ArgumentsDictTests(GaeTestCase):
    def tearDown(self):
        super(ArgumentsDictTests, self).tearDown()
        registry.arguments = registry.ArgumentsDict()

    def test_arguments_begin_empty(self):
        self.assertEqual(registry.arguments, {})

    def test_can_register_arguments(self):
        registry.arguments.register(User.email)
        registry.arguments.register(User.nickname)
        registry.arguments.register(User.user_id)

        self.assertEqual(len(registry.arguments), 3)

    def test_arguments_return_expected_choices(self):
        registry.arguments.register(User.email)
        registry.arguments.register(User.nickname)
        registry.arguments.register(User.user_id)

        self.assertEqual(registry.arguments.as_choices,
                         [('User', [('User.email', 'User.email'),
                                    ('User.nickname', 'User.nickname'),
                                    ('User.user_id', 'User.user_id')])])

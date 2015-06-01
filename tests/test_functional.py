"""
End-to-end tests
"""

import unittest
import zlib

from gutter.client.operators.comparable import Equals, Between, LessThan, \
    MoreThanOrEqualTo
from gutter.client.operators.identity import Truthy
from gutter.client.operators.misc import Percent, PercentRange

from gutter.client.models import Switch, Condition, Manager
from gutter.client import arguments


class deterministicstring(str):
    """
    Since the percentage-based conditions rely on the hash value from their
    arguments, we use this special deterministicstring class to return
    deterministic string values from the crc32 of itself.
    """

    def __hash__(self):
        return zlib.crc32(self)


class User(object):
    def __repr__(self):
        return u'<User "%s" is %d years old>' % (self.name, self.age)

    def __init__(self, name, age, location='San Francisco', married=False):
        self.name = name
        self.age = age
        self.location = location
        self.married = married


class UserArguments(arguments.Container):
    COMPATIBLE_TYPE = User

    name = arguments.String(lambda self: self.input.name)
    age = arguments.Value(lambda self: self.input.age)
    location = arguments.String(lambda self: self.input.location)
    married = arguments.Boolean(lambda self: self.input.married)


class IntegerArguments(arguments.Container):
    COMPATIBLE_TYPE = int

    value = arguments.Integer(lambda self: self.input)


class FloatArguments(arguments.Container):
    COMPATIBLE_TYPE = float

    value = arguments.Integer(lambda self: self.input)


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        super(FunctionalTests, self).setUp()
        self.manager = Manager(storage=dict())

        # Inputs
        self.jeff = User(deterministicstring('jeff'), 21)
        self.frank = User(deterministicstring('frank'), 10, location="Seattle")
        self.bill = User(deterministicstring('bill'), 70,
                         location="Yakima",
                         married=True)
        self.timmy = User(deterministicstring('timmy'), 12)
        self.steve = User(deterministicstring('timmy'), 19)

        # Conditions
        self.age_65_and_up = Condition(UserArguments, 'age',
                                       MoreThanOrEqualTo(lower_limit=65))
        self.age_under_18 = Condition(UserArguments, 'age',
                                      LessThan(upper_limit=18))
        self.age_not_under_18 = Condition(UserArguments, 'age',
                                          LessThan(upper_limit=18),
                                          negative=True)
        self.age_21_plus = Condition(UserArguments, 'age',
                                     MoreThanOrEqualTo(lower_limit=21))
        self.age_between_13_and_18 = Condition(UserArguments, 'age',
                                               Between(lower_limit=13,
                                                       upper_limit=18))

        self.in_sf = Condition(UserArguments, 'location',
                               Equals(value='San Francisco'))
        self.has_location = Condition(UserArguments, 'location', Truthy())

        self.ten_percent = Condition(UserArguments, 'name',
                                     Percent(percentage=10))
        self.upper_50_percent = Condition(UserArguments, 'name',
                                          PercentRange(lower_limit=50,
                                                       upper_limit=100))
        self.float_50_percent = Condition(FloatArguments, 'value',
                                          PercentRange(lower_limit=50,
                                                       upper_limit=100))
        self.answer_to_life = Condition(IntegerArguments, 'value',
                                        Equals(value=42))

        self.is_not_jeff = Condition(UserArguments, 'name',
                                     Equals(value='jeff'),
                                     negative=True)
        self.is_not_frank = Condition(UserArguments, 'name',
                                      Equals(value='frank'),
                                      negative=True)

        # Switches
        self.add_switch('can drink', condition=self.age_21_plus)
        self.add_switch('can drink in europe',
                        condition=self.age_21_plus,
                        state=Switch.states.GLOBAL)
        self.add_switch('can drink:answer to life',
                        condition=self.answer_to_life)
        self.add_switch('can drink:wine', condition=self.in_sf, concent=True)
        self.add_switch('retired', condition=self.age_65_and_up)
        self.add_switch('can vote', condition=self.age_not_under_18)
        self.add_switch('teenager', condition=self.age_between_13_and_18)
        self.add_switch('SF resident', condition=self.in_sf)
        self.add_switch('teen or in SF', self.age_between_13_and_18,
                        self.in_sf)
        self.add_switch('teen and in SF', self.age_between_13_and_18,
                        self.has_location,
                        compounded=True)
        self.add_switch('10 percent', self.ten_percent)
        self.add_switch('Upper 50 percent', self.upper_50_percent)
        self.add_switch('is over 21 and knows the meaning of life',
                        self.answer_to_life, self.age_21_plus,
                        state=Switch.states.SELECTIVE,
                        compounded=True)
        self.add_switch('is not jeff or frank', self.is_not_jeff,
                        self.is_not_frank,
                        state=Switch.states.SELECTIVE,
                        compounded=True)
        self.add_switch('is not jeff or frank and float is >50th percentile',
                        self.is_not_jeff, self.is_not_frank,
                        self.float_50_percent,
                        state=Switch.states.SELECTIVE,
                        compounded=True)

    def add_switch(self, name, condition=None, *conditions, **kwargs):
        switch = Switch(name, compounded=kwargs.get('compounded', False))
        switch.state = kwargs.get('state', Switch.states.SELECTIVE)
        conditions = list(conditions)

        if condition:
            conditions.append(condition)

        [switch.conditions.append(c) for c in conditions]
        if 'manager' in kwargs:
            kwargs.get('manager', self.manager).register(switch)
        else:
            self.manager.register(switch)
        return switch

    def test_basic_switches_work_with_conditions(self):
        manager = self.manager
        manager.input(self.bill)

        self.assertTrue(manager.active('can drink'))
        self.assertTrue(manager.active('can drink in europe'))
        self.assertTrue(manager.active('can vote'))
        self.assertFalse(manager.active('SF resident'))
        self.assertTrue(manager.active('retired'))
        self.assertFalse(manager.active('10 percent'))
        self.assertTrue(manager.active('Upper 50 percent'))

        manager = self.manager
        manager.input(self.jeff)

        self.assertTrue(manager.active('can drink'))
        self.assertTrue(manager.active('can drink in europe'))
        self.assertTrue(manager.active('can vote'))
        self.assertTrue(manager.active('SF resident'))
        self.assertFalse(manager.active('teenager'))
        self.assertTrue(manager.active('teen or in SF'))
        self.assertFalse(manager.active('teen and in SF'))
        self.assertFalse(manager.active('10 percent'))
        self.assertTrue(manager.active('Upper 50 percent'))

        manager = self.manager
        manager.input(self.frank)

        self.assertFalse(manager.active('can drink'))
        self.assertTrue(manager.active('can drink in europe'))
        self.assertFalse(manager.active('can vote'))
        self.assertFalse(manager.active('teenager'))
        self.assertFalse(manager.active('10 percent'))
        self.assertTrue(manager.active('Upper 50 percent'))

    def test_can_use_extra_inputs_to_active(self):
        manager = self.manager
        manager.input(self.frank)

        self.assertFalse(manager.active('can drink'))
        self.assertTrue(manager.active('can drink', self.bill))

        manager = self.manager
        manager.input(self.bill)

        self.assertTrue(manager.active('can drink'))
        self.assertFalse(manager.active('can drink', self.frank,
                                        exclusive=True))

    def test_switches_with_multiple_inputs(self):

        manager = self.manager
        manager.input(self.bill, self.jeff)

        self.assertTrue(manager.active('can drink'))
        self.assertTrue(manager.active('can drink in europe'))
        self.assertTrue(manager.active('SF resident'))
        self.assertFalse(manager.active('teenager'))
        self.assertFalse(manager.active('10 percent'))
        self.assertTrue(manager.active('Upper 50 percent'))

        manager = self.manager
        manager.input(self.frank, self.jeff)

        self.assertTrue(manager.active('can drink'))
        self.assertTrue(manager.active('can drink in europe'))
        self.assertTrue(manager.active('SF resident'))
        self.assertFalse(manager.active('teenager'))
        self.assertFalse(manager.active('10 percent'))
        self.assertTrue(manager.active('Upper 50 percent'))

    def test_switches_with_multiple_inputs_of_multiple_types(self):
        manager = self.manager
        manager.input(self.bill, 4242, 0.2)

        # should fail because bill is not jeff or frank but 0.2 is < 50%
        self.assertFalse(manager.active(
            'is not jeff or frank and float is >50th percentile'))

        manager = self.manager
        manager.input(self.bill, 4242, 0.8)

        # should pass because bill is not jeff or frank and 0.8 is > 50%')
        self.assertTrue(manager.active(
            'is not jeff or frank and float is >50th percentile'))

        manager = self.manager
        manager.input(self.jeff, 4242, 0.8)

        # should fail because jeff is jeff or frank even though 0.8 is > 50%
        self.assertFalse(manager.active(
            'is not jeff or frank and float is >50th percentile'))

        manager = self.manager
        manager.input(self.bill, 4242)

        # should work because bill is not jeff or frank
        self.assertTrue(manager.active('is not jeff or frank'))

        manager = self.manager
        manager.input(self.frank, self.jeff, 4242)

        # should fail because jeff and frank are inputs
        self.assertFalse(manager.active('is not jeff or frank'))

        manager = self.manager
        manager.input(self.bill, self.jeff, 42, 0.3)

        # should pass because bill and jeff are over 21 and 42 is an input
        self.assertTrue(
            manager.active('is over 21 and knows the meaning of life'))

    def test_switches_can_consent_top_parent_switch(self):
        manager = self.manager
        manager.input(self.jeff)

        self.assertTrue(manager.active('can drink'))
        self.assertTrue(manager.active('can drink in europe'))
        self.assertTrue(manager.active('SF resident'))
        self.assertTrue(manager.active('can drink:wine'))

        manager = self.manager
        manager.input(self.timmy)

        self.assertFalse(manager.active('can drink'))
        self.assertTrue(manager.active('can drink in europe'))
        self.assertTrue(manager.active('SF resident'))
        self.assertFalse(manager.active('can drink:wine'))

    def test_changing_parent_is_reflected_in_child_switch(self):
        manager = self.manager
        manager.input(self.jeff)

        self.assertTrue(manager.active('can drink:wine'))

        parent = self.manager['can drink']
        parent.state = Switch.states.DISABLED
        parent.save()

        self.assertFalse(manager.active('can drink:wine'))

    def test_switches_can_be_deregistered_and_then_autocreated(self):
        manager = self.manager
        manager.input(self.jeff)

        self.assertTrue(manager.active('can drink'))

        manager.unregister('can drink')

        with self.assertRaises(ValueError):
            manager.active('can drink')

        manager.autocreate = True
        self.assertFalse(manager.active('can drink'))

    def test_namespaes_keep_switches_isloated(self):
        germany = Manager(storage=dict()).namespaced('germany')
        usa = Manager(storage=dict()).namespaced('usa')

        self.add_switch('booze', condition=self.age_21_plus, manager=usa)
        self.add_switch('booze',
                        condition=self.age_not_under_18,
                        manager=germany)

        self.assertEquals(len(germany.switches), 1)
        self.assertEquals(len(usa.switches), 1)

        self.assertEquals(usa.switches[0].conditions, [self.age_21_plus])
        self.assertEquals(germany.switches[0].conditions,
                          [self.age_not_under_18])

        usa.input(self.jeff)
        self.assertTrue(usa.active('booze'))

        usa.input(usa, self.jeff, self.timmy)
        self.assertTrue(usa.active('booze'))  # Jeff is 21, so he counts
        self.assertFalse(usa.active('booze', self.timmy,
                                    exclusive=True))  # Timmy is 10

        usa.input(self.timmy)
        self.assertFalse(usa.active('booze'))

        usa.input(self.timmy, self.steve)
        self.assertFalse(usa.active('booze'))

        germany.input(self.timmy)
        self.assertFalse(germany.active('booze'))  # 10 is still too young

        germany.input(self.steve)
        self.assertTrue(germany.active('booze'))  # 19 is old enough!

        germany.input(self.timmy, self.steve)
        self.assertTrue(germany.active('booze'))  # Cause steve is 19

        germany.input(self.jeff, self.timmy)
        self.assertTrue(germany.active('booze'))  # Cause jeff is 21

        germany.input(self.jeff)
        # exclusive timmy is 10
        self.assertFalse(germany.active('booze', self.timmy,
                                        exclusive=True))

    def test_namespace_switches_not_shared_with_parent(self):
        base = self.manager
        daughter = self.manager.namespaced('daughter')
        son = self.manager.namespaced('son')

        self.assertTrue(base.switches is not daughter.switches)
        self.assertTrue(base.switches is not son.switches)
        self.assertTrue(daughter.switches is not son.switches)

        daughter_switch = self.add_switch('daughter only', manager=daughter)
        son_switch = self.add_switch('son only', manager=son)

        self.assertEquals(daughter.switches, [daughter_switch])
        self.assertEquals(son.switches, [son_switch])

        self.assertTrue(daughter_switch not in base.switches)
        self.assertTrue(son_switch not in base.switches)

    def test_retrieved_switches_can_be_updated(self):
        switch = Switch('foo')
        self.manager.register(switch)

        self.assertEquals(self.manager.switch('foo').name, 'foo')

        switch.state = Switch.states.GLOBAL
        switch.save()

        self.assertEquals(self.manager.switch('foo').state,
                          Switch.states.GLOBAL)

    def test_concent_with_different_arguments(self):
        # Test that a parent switch with a different argument type from the
        # child works.
        self.manager.input(self.jeff, 42)
        self.assertTrue(self.manager.active('can drink:answer to life'))

        self.manager.input(self.timmy, 42)
        self.assertFalse(self.manager.active('can drink:answer to life'))

        self.manager.input(self.jeff, 77)
        self.assertFalse(self.manager.active('can drink:answer to life'))

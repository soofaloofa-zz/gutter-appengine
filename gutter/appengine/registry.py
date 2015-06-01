"""
A registry of all operators and arguments for switches.
To implement custom arguments or operators, add them to
the registry.
"""
from gutter.client.operators.comparable import Equals, Between, LessThan, LessThanOrEqualTo, MoreThan, \
    MoreThanOrEqualTo
from gutter.client.operators.identity import Truthy
from gutter.client.operators.misc import Percent, PercentRange

from itertools import groupby
from operator import attrgetter, itemgetter


class OperatorsDict(dict):
    """
    A dictionary representing all operators.
    """
    def __init__(self, *ops):
        map(self.register, ops)

    def register(self, operator):
        """
        Register a new operator.
        """
        self[operator.name] = operator

    @property
    def as_choices(self):
        """
        Return all operators as wtforms SelectField choices.
        """
        groups = {}

        for operator in sorted(self.values(), key=attrgetter('preposition')):
            key = operator.group.title()
            pair = (operator.name, operator.preposition.title())

            groups.setdefault(key, [])
            groups[key].append(pair)

        return sorted(groups.items(), key=itemgetter(0))

    @property
    def arguments(self):
        """
        Return arguments for each operator, keyed by operator name.
        """
        return dict((name, op.arguments) for name, op in self.items())


class ArgumentsDict(dict):
    """
    A dictionary representing all arguments.
    """

    @property
    def as_choices(self):
        """
        Return all arguments as wtforms choices.
        """
        # Used map built-in, pylint: disable=W0141
        sorted_strings = sorted(map(str, self.values()))
        extract_classname = lambda a: a.split('.')[0]

        grouped = groupby(sorted_strings, extract_classname)

        groups = {}
        for name, args in grouped:
            groups.setdefault(name, [])
            groups[name].extend((a, a) for a in args)

        return groups.items()

    def register(self, argument):
        """
        Register a new argument.
        """
        self[str(argument)] = argument


# Invalid name, pylint: disable=C0103
operators = OperatorsDict(Equals, Between, LessThan, LessThanOrEqualTo,
                          MoreThan, MoreThanOrEqualTo, Truthy, Percent,
                          PercentRange)

# Invalid name, pylint: disable=C0103
arguments = ArgumentsDict()

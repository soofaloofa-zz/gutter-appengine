"""
Configure gutter
"""
# Declare and register arguments before creating the manager
# so that the manager knows how to unpickle the classes.
from gutter.client import arguments
from gutter.appengine import registry


class User(arguments.Container):

    nickname = arguments.String(lambda self: self.input.nickname())
    email = arguments.String(lambda self: self.input.email())
    user_id = arguments.String(lambda self: self.input.user_id())


class Account(arguments.Container):

    account_group_id = arguments.String(
        lambda self: self.input.account_group_id()
    )


class Partner(arguments.Container):

    partner_id = arguments.String(lambda self: self.input.partner_id)


registry.arguments.register(User.email)
registry.arguments.register(User.nickname)
registry.arguments.register(User.user_id)
registry.arguments.register(Account.account_group_id)


from gutter.client.settings import manager
from gutter.appengine.manager import default_manager

manager.default = default_manager

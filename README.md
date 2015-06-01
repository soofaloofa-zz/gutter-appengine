# Gutter for AppEngine

[![Build Status](https://travis-ci.org/soofaloofa/gutter-appengine.svg)](https://travis-ci.org/soofaloofa/gutter-appengine)

gutter-appengine provides an App Engine front-end for [gutter][gutter]. It
allows you to create and update switches using a UI and to register new
arguments and operators particular to your application.


## Getting Started

The first step is to include gutter-appengine in your app.yaml.

```python
includes:
- lib/gutter/appengine/
```

Next, in appengine_config.py set the default gutter manager to use the App Engine manager.

```python
from gutter.client.settings import manager
from gutter.appengine.manager import default_manager

manager.default = default_manager
```

Now, you are ready to define your switches and switch conditions. Also in
appengine_config.py (and above setting the default manager so that the manager
knows how to unpickle the classes).

```python
from gutter.client import arguments
from gutter.appengine import registry


class User(arguments.Container):

    nickname = arguments.String(lambda self: self.input.nickname())
    email = arguments.String(lambda self: self.input.email())
    user_id = arguments.String(lambda self: self.input.user_id())


class Account(arguments.Container):

    account_group_id = arguments.String(lambda self: self.input.account_group_id())


class Partner(arguments.Container):

    partner_id = arguments.String(lambda self: self.input.partner_id)


registry.arguments.register(User.email)
registry.arguments.register(User.nickname)
registry.arguments.register(User.user_id)
registry.arguments.register(Account.account_group_id)
```


Navigate to /gutter/ to begin creating switches. The example in `example_app`
shows a full example of integrating gutter with your project.

## Defining Switches

A Switch takes one or more Conditions and passes or fails based on whether or
not its input satisfies the Conditions. Each Condition takes one or more
Arguments. You can think of this as defining a list of equations that any inputs
must satisfy to pass or fail a switch.

```python
class UserArguments(arguments.Container):
    age = arguments.Integer(lambda self: self.input.age())

condition = Condition(UserArguments, 'age', LessThan(upper_limit=18))

switch = Switch('minor', compounded=False)
switch.conditions = [condition]
```

## Using Switches

To use a switch, call `active` and pass it an input. The input can be any object
matching the Arguments to your Condition. `active` will return True if the input
satisfies the condition or False otherwise.

```python
from gutter.client.default import gutter

is_active = gutter.active('minor', User)  # User is your domain object
```

## More Information

If you need more information on gutter internals, refer to the official [gutter
project][gutter].

## Development

Using virtualenv is recommended for development.

```bash
virtualenv .
source ./bin/activate
Development Dependencies
```

We use flake8 for checking both PEP-8 and common Python errors and invoke for continuous integration.

```bash
pip install -U flake8
pip install -U invoke
```

You can list available build tasks with inv -l.

Due to a limitation with Google Appengine, dependencies must be installed locally before running tests. TThe fetch_deps make command will install dependencies to the vendor directory.

```bash
inv fetch_deps
```

## Publishing to PyPI

You need pip, setuptools and wheel to publish to PyPI.

```bash
inv publish
```

[gutter]: https://github.com/disqus/gutter

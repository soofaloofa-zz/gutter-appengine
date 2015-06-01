"""
wtforms extension for handling condition selections.
"""

import six
from cgi import escape
from wtforms import SelectField as _SelectField
from wtforms.widgets import html_params, HTMLString, Select as _Select
from wtforms.validators import ValidationError
from .registry import operators


class SelectWidget(_Select):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(val, label, selected))
        html.append('</select>')
        return HTMLString(''.join(html))

    def render_optgroup(self, value, label, mixed):
        """
        Render an optgroup.
        """
        children = []

        for item_value, item_label in label:
            item_html = self.render_option(item_value, item_label, mixed)
            children.append(item_html)

        html = u'<optgroup label="%s">%s</optgroup>'
        data = (escape(six.text_type(value)), u'\n'.join(children))
        return HTMLString(html % data)

    def render_option(self, value, label, mixed):
        """
        Render option as HTML tag, but not forget to wrap options into
        ``optgroup`` tag if ``label`` var is ``list`` or ``tuple``.
        """
        if isinstance(label, (list, tuple)):
            return self.render_optgroup(value, label, mixed)

        coerce_func, data = mixed
        if isinstance(data, list) or isinstance(data, tuple):
            selected = coerce_func(value) in data
        else:
            selected = coerce_func(value) == data

        options = {'value': value}

        if selected:
            options['selected'] = True

        if value in operators.arguments:
            options['data-arguments'] = ','.join(operators.arguments[value])

        data = (html_params(**options), escape(six.text_type(label)))

        html = u'<option %s>%s</option>'
        return HTMLString(html % data)


class SelectField(_SelectField):
    """
    Add support of ``optgroup``'s' to default WTForms' ``SelectField`` class.

    So, next choices would be supported as well::

        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            ))
        )

    Also supports lazy choices (callables that return an iterable)
    """
    widget = SelectWidget()

    def iter_choices(self):
        """
        We should update how choices are iter to make sure that value from
        internal list or tuple should be selected.
        """
        for value, label in self.concrete_choices:
            yield (value, label, (self.coerce, self.data))

    @property
    def concrete_choices(self):
        """
        Return the current choices.
        """
        if callable(self.choices):
            return self.choices()
        return self.choices

    @property
    def choice_values(self):
        """
        Return the current choice values.
        """
        values = []
        for value, label in self.concrete_choices:
            if isinstance(label, (list, tuple)):
                for subvalue, _ in label:
                    values.append(subvalue)
            else:
                values.append(value)
        return values

    def pre_validate(self, form):
        """
        Don't forget to validate also values from embedded lists.
        """
        values = self.choice_values
        if (self.data is None and u'' in values) or self.data in values:
            return True

        raise ValidationError(self.gettext(u'Not a valid choice'))

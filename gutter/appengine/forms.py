"""
Forms
"""
import wtforms
from gutter.client.models import Switch, Condition

from . import wtforms_extension
from .registry import operators, arguments


class ConditionForm(wtforms.Form):
    """
    Form defining the individual condition of a switch.
    """

    argument = wtforms_extension.SelectField(choices=arguments.as_choices)
    negative = wtforms.SelectField(choices=(('0', 'Is'), ('1', 'Is Not')))
    operator = wtforms_extension.SelectField(choices=operators.as_choices)

    operator_arguments = wtforms.FieldList(wtforms.StringField(),
                                           min_entries=2,
                                           max_entries=2)


class SwitchForm(wtforms.Form):
    """
    Form defining a switch.
    """
    name = wtforms.StringField(u'Name',
                               validators=[wtforms.validators.required(),
                                           wtforms.validators.length(max=100)])
    label = wtforms.StringField(u'Label')
    description = wtforms.TextAreaField(u'Description')

    state = wtforms.SelectField(
        u'State',
        choices={'1': 'Disabled',
                 '2': 'Selective',
                 '3': 'Global'}.items())

    compounded = wtforms.BooleanField()
    concent = wtforms.BooleanField(u'Consent')
    delete = wtforms.HiddenField()
    is_new = wtforms.HiddenField()

    conditions = wtforms.FieldList(wtforms.FormField(ConditionForm),
                                   min_entries=0)

    def to_object(self):
        """
        Return a Switch object based on form data.
        """
        switch = Switch(name=self.name.data,
                        label=self.label.data,
                        description=self.description.data,
                        # States must be integer to match gutter client
                        state=int(self.state.data),
                        compounded=self.compounded.data,
                        concent=self.concent.data)

        for condition in self.conditions:
            switch.conditions.append(self.make_condition(condition))

        return switch

    def make_condition(self, condition_form):
        """
        Create a condition based on form input
        """
        # Operators in the registry are the types (classes), so extract that
        # and we will construct it from the remaining data, which are the
        # arguments for the operator
        operator_type = operators[condition_form.operator.data]

        # Arguments are a Class property, so just a simple fetch from the
        # arguments dict will retreive it
        argument = arguments[condition_form.argument.data]

        # The remaining variables in the data are the arguments to the
        # operator, but they need to be cast by the argument to their
        # right type
        caster = argument.variable.to_python

        operator_kwargs = dict((k, caster(v)) for k, v in zip(
            operator_type.arguments, condition_form.operator_arguments.data))

        return Condition(argument=argument.owner,
                         attribute=argument.name,
                         operator=operator_type(**operator_kwargs),
                         negative=bool(int(condition_form.negative.data)))

    @classmethod
    def from_object(cls, switch):
        """
        Return a new form based on a Switch object.
        """
        data = dict(label=switch.label,
                    name=switch.name,
                    description=switch.description,
                    state=switch.state,
                    compounded=switch.compounded,
                    concent=switch.concent)

        instance = cls(**data)

        for condition in switch.conditions:
            instance.append_condition(condition)

        return instance

    def append_condition(self, condition):
        """
        Given a condition, append it to the list of form conditions.
        """
        fields = dict(argument='.'.join((condition.argument.__name__,
                                         condition.attribute)),
                      negative='1' if condition.negative else '0',
                      operator=condition.operator.name)

        operator_arguments = [condition.operator.variables[arg]
                              for arg in condition.operator.arguments]
        fields['operator_arguments'] = operator_arguments

        self.conditions.append_entry(fields)

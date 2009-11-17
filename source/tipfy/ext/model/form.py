# -*- coding: utf-8 -*-
"""
    tipfy.ext.model.form
    ~~~~~~~~~~~~~~~~~~~~

    Form generation utilities for db.Model classes, based on wtforms.

    The goal of model_form() is to provide a clean, explicit and predictable
    way to generate a form for a ``db.Model`` class. No malabarism or hidden
    magic should be necessary to generate a form based on one or multiple
    models, and to add custom non-model related fields: model_form() simply
    generates a form class that can be used as it is, be extended or be used
    as base class for a new form classes created using model_form().

    Example usage:

        from google.appengine.ext import db
        from tipfy.ext.model.form import model_form

        # Define an example model and add a record.
        class Contact(db.Model):
            name = db.StringProperty(required=True)
            city = db.StringProperty()
            age = db.IntegerProperty(required=True)
            is_admin = db.BooleanProperty(default=False)

        new_entity = Contact(key_name='test', name='Test Name', age=17)
        new_entity.put()

        # Generate a form based on the model.
        ContactForm = model_form(Contact)

        # Get a form populated with entity data.
        entity = Contact.get_by_key_name('test')
        form = ContactForm(obj=entity)

    Properties from de model can be excluded from the generated form, or it can
    include just a set of properties. For example:

        # Generate a form based on the model, excluding 'city' and 'is_admin'.
        ContactForm = model_form(Contact, exclude=('city', 'is_admin'))

        # or...

        # Generate a form based on the model, only including 'name' and 'age'.
        ContactForm = model_form(Contact, only=('name', 'age'))

    The form can be generated setting field arguments:

        ContactForm = model_form(Contact, only=('name', 'age'), field_args={
            'name': {
                'label': 'Full name',
                'description': 'Your name',
            },
            'age': {
                'label': 'Age',
                'validators': [validators.NumberRange(min=14, max=99)],
            }
        })

    The class returned by model_form() can be used as a base class for forms
    mixing non-model fields and/or other model forms. For example:

        # Generate a form based on the model.
        BaseContactForm = model_form(Contact)

        # Generate a form based on other model.
        ExtraContactForm = model_form(MyOtherModel)

        class ContactForm(BaseContactForm):
            # Add an extra, non-model related field.
            subscribe_to_news = f.BooleanField()

            # Add the other model form as a subform.
            extra = f.FormField(ExtraContactForm)

    The class returned by model_form() can also extend an existing form class:

        class BaseContactForm(Form):
            # Add an extra, non-model related field.
            subscribe_to_news = f.BooleanField()

        # Generate a form based on the model.
        ContactForm = model_form(Contact, base_class=BaseContactForm)

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE.txt for more details.
"""
from wtforms import Form, validators, fields as f


class StringListPropertyField(f.TextAreaField):
    """A field for ``db.StringListProperty``. The list items are rendered in a
    textarea.
    """
    def process_data(self, value):
        if isinstance(value, list):
            value = '\n'.join(value)

        self.data = value

    def populate_obj(self, obj, name):
        if isinstance(self.data, basestring):
            value = self.data.splitlines()
        else:
            value = []

        setattr(obj, name, value)


def get_TextField(kwargs):
    """Returns a ``TextField``, applying the ``db.StringProperty`` length limit
    of 500 bytes.
    """
    kwargs['validators'].append(validators.length(max=500))
    return f.TextField(**kwargs)


def get_IntegerField(kwargs):
    """Returns an ``IntegerField``, applying the ``db.IntegerProperty`` range
    limits.
    """
    kwargs['validators'].append(validators.NumberRange(min=0x8000000000000000,
        max=0x7fffffffffffffff))
    return f.IntegerField(**kwargs)


def convert_StringProperty(model, prop, kwargs):
    """Returns a form field for a StringProperty."""
    if prop.multiline:
        kwargs['validators'].append(validators.length(max=500))
        return f.TextAreaField(**kwargs)
    else:
        return get_TextField(kwargs)


def convert_ByteStringProperty(model, prop, kwargs):
    """Returns a form field for a ByteStringProperty."""
    return get_TextField(kwargs)


def convert_BooleanProperty(model, prop, kwargs):
    """Returns a form field for a BooleanProperty."""
    return f.BooleanField(**kwargs)


def convert_IntegerProperty(model, prop, kwargs):
    """Returns a form field for a IntegerProperty."""
    return get_IntegerField(kwargs)


def convert_FloatProperty(model, prop, kwargs):
    """Returns a form field for a FloatProperty."""
    return get_TextField(kwargs)


def convert_DateTimeProperty(model, prop, kwargs):
    """Returns a form field for a DateTimeProperty."""
    if prop.auto_now or prop.auto_now_add:
        return None
    return f.DateTimeField(format='%Y-%m-%d %H-%M-%S', **kwargs)


def convert_DateProperty(model, prop, kwargs):
    """Returns a form field for a DateProperty."""
    if prop.auto_now or prop.auto_now_add:
        return None
    return f.DateTimeField(format='%Y-%m-%d', **kwargs)


def convert_TimeProperty(model, prop, kwargs):
    """Returns a form field for a TimeProperty."""
    if prop.auto_now or prop.auto_now_add:
        return None
    return f.DateTimeField(format='%H-%M-%S', **kwargs)


def convert_ListProperty(model, prop, kwargs):
    """Returns a form field for a ListProperty."""
    raise NotImplementedError()


def convert_StringListProperty(model, prop, kwargs):
    """Returns a form field for a StringListProperty."""
    return StringListPropertyField(**kwargs)


def convert_ReferenceProperty(model, prop, kwargs):
    """Returns a form field for a ReferenceProperty."""
    raise NotImplementedError()


def convert_SelfReferenceProperty(model, prop, kwargs):
    """Returns a form field for a SelfReferenceProperty."""
    raise NotImplementedError()


def convert_UserProperty(model, prop, kwargs):
    """Returns a form field for a UserProperty."""
    raise NotImplementedError()


def convert_BlobProperty(model, prop, kwargs):
    """Returns a form field for a BlobProperty."""
    return f.FileField(**kwargs)


def convert_TextProperty(model, prop, kwargs):
    """Returns a form field for a TextProperty."""
    return f.TextAreaField(**kwargs)


def convert_CategoryProperty(model, prop, kwargs):
    """Returns a form field for a CategoryProperty."""
    return get_TextField(kwargs)


def convert_LinkProperty(model, prop, kwargs):
    """Returns a form field for a LinkProperty."""
    kwargs['validators'].append(validators.url())
    return get_TextField(kwargs)


def convert_EmailProperty(model, prop, kwargs):
    """Returns a form field for a EmailProperty."""
    kwargs['validators'].append(validators.email())
    return get_TextField(kwargs)


def convert_GeoPtProperty(model, prop, kwargs):
    """Returns a form field for a GeoPtProperty."""
    raise NotImplementedError()


def convert_IMProperty(model, prop, kwargs):
    """Returns a form field for a IMProperty."""
    raise NotImplementedError()


def convert_PhoneNumberProperty(model, prop, kwargs):
    """Returns a form field for a PhoneNumberProperty."""
    return get_TextField(kwargs)


def convert_PostalAddressProperty(model, prop, kwargs):
    """Returns a form field for a PostalAddressProperty."""
    return get_TextField(kwargs)


def convert_RatingProperty(model, prop, kwargs):
    """Returns a form field for a RatingProperty."""
    kwargs['validators'].append(validators.NumberRange(min=0, max=100))
    return f.IntegerField(**kwargs)


class ModelConverter(object):
    """Converts properties from a ``db.Model`` class to form fields.

    Default conversions between properties and fields:

    +====================+===================+==============+==================+
    | Property subclass  | Field subclass    | datatype     | notes            |
    +====================+===================+==============+==================+
    | StringProperty     | TextField         | unicode      | TextArea         |
    |                    |                   |              | if multiline     |
    +--------------------+-------------------+--------------+------------------+
    | ByteStringProperty | TextField         | str          |                  |
    +--------------------+-------------------+--------------+------------------+
    | BooleanProperty    | BooleanField      | bool         |                  |
    +--------------------+-------------------+--------------+------------------+
    | IntegerProperty    | IntegerField      | int or long  |                  |
    +--------------------+-------------------+--------------+------------------+
    | FloatProperty      | TextField         | float        |                  |
    +--------------------+-------------------+--------------+------------------+
    | DateTimeProperty   | DateTimeField     | datetime     | skipped if       |
    |                    |                   |              | auto_now[_add]   |
    +--------------------+-------------------+--------------+------------------+
    | DateProperty       | DateTimeField     | date         | skipped if       |
    |                    |                   |              | auto_now[_add]   |
    +--------------------+-------------------+--------------+------------------+
    | TimeProperty       | DateTimeField     | time         | skipped if       |
    |                    |                   |              | auto_now[_add]   |
    +--------------------+-------------------+--------------+------------------+
    | ListProperty       | None              | list         | always skipped   |
    +--------------------+-------------------+--------------+------------------+
    | StringListProperty | TextAreaField     | list of str  |                  |
    +--------------------+-------------------+--------------+------------------+
    | ReferenceProperty  | None              | db.Model     | always skipped   |
    +--------------------+-------------------+--------------+------------------+
    | SelfReferenceP.    | None              | db.Model     | always skipped   |
    +--------------------+-------------------+--------------+------------------+
    | UserProperty       | None              | users.User   | always skipped   |
    +--------------------+-------------------+--------------+------------------+
    | BlobProperty       | FileField         | str          |                  |
    +--------------------+-------------------+--------------+------------------+
    | TextProperty       | TextAreaField     | unicode      |                  |
    +--------------------+-------------------+--------------+------------------+
    | CategoryProperty   | TextField         | unicode      |                  |
    +--------------------+-------------------+--------------+------------------+
    | LinkProperty       | TextField         | unicode      |                  |
    +--------------------+-------------------+--------------+------------------+
    | EmailProperty      | TextField         | unicode      |                  |
    +--------------------+-------------------+--------------+------------------+
    | GeoPtProperty      | None              | db.GeoPt     | always skipped   |
    +--------------------+-------------------+--------------+------------------+
    | IMProperty         | None              | db.IM        | always skipped   |
    +--------------------+-------------------+--------------+------------------+
    | PhoneNumberProperty| TextField         | unicode      |                  |
    +--------------------+-------------------+--------------+------------------+
    | PostalAddressP.    | TextField         | unicode      |                  |
    +--------------------+-------------------+--------------+------------------+
    | RatingProperty     | IntegerField      | int or long  |                  |
    +--------------------+-------------------+--------------+------------------+
    | _ReverseReferenceP.| None              | <iterable>   | always skipped   |
    +====================+===================+==============+==================+
    """
    default_converters = {
        'StringProperty':        convert_StringProperty,
        'ByteStringProperty':    convert_ByteStringProperty,
        'BooleanProperty':       convert_BooleanProperty,
        'IntegerProperty':       convert_IntegerProperty,
        'FloatProperty':         convert_FloatProperty,
        'DateTimeProperty':      convert_DateTimeProperty,
        'DateProperty':          convert_DateProperty,
        'TimeProperty':          convert_TimeProperty,
        'ListProperty':          convert_ListProperty,
        'StringListProperty':    convert_StringListProperty,
        'ReferenceProperty':     convert_ReferenceProperty,
        'SelfReferenceProperty': convert_SelfReferenceProperty,
        'UserProperty':          convert_UserProperty,
        'BlobProperty':          convert_BlobProperty,
        'TextProperty':          convert_TextProperty,
        'CategoryProperty':      convert_CategoryProperty,
        'LinkProperty':          convert_LinkProperty,
        'EmailProperty':         convert_EmailProperty,
        'GeoPtProperty':         convert_GeoPtProperty,
        'IMProperty':            convert_IMProperty,
        'PhoneNumberProperty':   convert_PhoneNumberProperty,
        'PostalAddressProperty': convert_PostalAddressProperty,
        'RatingProperty':        convert_RatingProperty,
    }

    def __init__(self, converters=None):
        """Constructs the converter, setting the converter callables.

        :param converters:
            A dictionary of converter callables for each property type. The
            callable must accept the arguments (model, prop, kwargs).
        """
        self.converters = converters or self.default_converters

    def convert(self, model, prop, field_args):
        """Returns a form field for a single model property.

        :param model:
            The ``db.Model`` class that contains the property.
        :param prop:
            The model property: a ``db.Property`` instance.
        :param field_args:
            Optional keyword arguments to construct the field.
        """
        kwargs = {
            'label': prop.name,
            'default': prop.default_value(),
            'validators': [],
        }
        if field_args:
            kwargs.update(field_args)

        if prop.required:
            kwargs['validators'].append(validators.required())

        if prop.choices:
            # Use choices in a select field.
            kwargs['choices'] = [(v, v) for v in prop.choices]
            return f.SelectField(**kwargs)
        else:
            method = self.converters.get(type(prop).__name__, None)
            if method is not None:
                return method(model, prop, kwargs)


def model_form(model, base_class=Form, only=None, exclude=None, field_args=None,
    converter=None):
    """Creates and returns a dynamic ``wtforms.Form`` class for a a given
    ``db.Model`` class. The form class can be used as it is or serve as a base
    for extended form classes, which can then mix non-model related fields,
    subforms with other model forms, among other possibilities.

    :param model:
        The ``db.Model`` class to generate a form for.
    :param base_class:
        Base form class to extend from. Must be a ``wtforms.Form`` subclass.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to a keyword arguments
        used to construct each field object.
    :param converter:
        A converter to generate the fields based on the model properties. If
        not set, ``ModelConverter`` is used.
    """
    converter = converter or ModelConverter()
    field_args = field_args or {}

    # Get the field names we want to include or exclude, starting with the
    # full list of model properties.
    props = model.properties()
    field_names = props.keys()
    if only:
        field_names = list(f for f in only if f in field_names)
    elif exclude:
        field_names = list(f for f in field_names if f not in exclude)

    # Create all fields.
    field_dict = {}
    for name in field_names:
        field = converter.convert(model, props[name], field_args.get(name))
        if field is not None:
            field_dict[name] = field

    # Return a dynamically created new class, extending from base_class and
    # including the created fields as properties.
    return type(model.kind() + 'Form', (base_class,), field_dict)

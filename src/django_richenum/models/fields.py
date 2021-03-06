import numbers

from django.db import models

from richenum import OrderedRichEnumValue


class IndexEnumField(models.IntegerField):
    '''Store ints in DB, but expose OrderedRichEnumValues in Python.

    '''
    description = 'Efficient storage for OrderedRichEnums'
    __metaclass__ = models.SubfieldBase

    def __init__(self, enum, *args, **kwargs):
        if not hasattr(enum, 'from_index'):
            raise TypeError("%s doesn't support index-based lookup." % enum)
        self.enum = enum
        super(IndexEnumField, self).__init__(*args, **kwargs)

    def get_default(self):
        # Override Django's implementation, which casts all default values to
        # unicode.
        if self.has_default():
            return self.default
        return None

    def get_prep_value(self, value):
        # Convert value to integer for storage/queries.
        if value is None:
            return None
        elif isinstance(value, OrderedRichEnumValue):
            return value.index
        elif isinstance(value, numbers.Integral):
            return value
        else:
            raise TypeError('Cannot convert value: %s (%s) to an int.' % (value, type(value)))

    def to_python(self, value):
        # Convert value to OrderedRichEnumValue. (Called on *all* assignments
        # to the field, including object creation from a DB record.)
        if value is None:
            return None
        elif isinstance(value, OrderedRichEnumValue):
            return value
        elif isinstance(value, numbers.Integral):
            return self.enum.from_index(value)
        else:
            raise TypeError('Cannot interpret %s (%s) as an OrderedRichEnumValue.' % (value, type(value)))


class LaxIndexEnumField(IndexEnumField):
    '''Like IndexEnumField, but also allows casting to and from
    canonical names.

    '''
    def get_prep_value(self, value):
        if isinstance(value, basestring):
            return self.enum.from_canonical(value).index
        return super(LaxIndexEnumField, self).get_prep_value(value)

    def to_python(self, value):
        if isinstance(value, basestring):
            return self.enum.from_canonical(value)
        return super(LaxIndexEnumField, self).to_python(value)

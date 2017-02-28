# -*- coding: utf-8 -*-
from flask_restplus import fields as basefields
from sqlalchemy.sql.schema import ColumnDefault
import aniso8601
from six import string_types

class FromSQLAlchemyColumnMixin(object):
    def __init__(self, *args, **kwargs):
        super(FromSQLAlchemyColumnMixin, self).__init__(*args, **kwargs)
        column = kwargs.pop("column", None)
        if column is not None:
            self.required = not column.nullable
            self.description = column.description
            if hasattr(column, 'default'):
                self.default = column.default
                if isinstance(self.default, ColumnDefault):
                    self.default = self.default.arg
            if not self.required:
                self.__schema_type__ = [self.__schema_type__, "null"]

class Integer(FromSQLAlchemyColumnMixin, basefields.Integer):
    pass


class Boolean(FromSQLAlchemyColumnMixin, basefields.Boolean):
    pass


class DateTime(FromSQLAlchemyColumnMixin, basefields.DateTime):
    def __init__(self, dt_format='rfc822', **kwargs):
        super(DateTime, self).__init__(dt_format, **kwargs)


class Float(FromSQLAlchemyColumnMixin, basefields.Float):
    pass


class String(FromSQLAlchemyColumnMixin, basefields.String):
    pass


class Nested(FromSQLAlchemyColumnMixin, basefields.Nested):
    pass


class List(FromSQLAlchemyColumnMixin, basefields.List):
    pass


class Date(FromSQLAlchemyColumnMixin, basefields.Raw):
    __schema_type__ = 'string'
    __schema_format__ = '^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}'

    def schema(self):
        return {
            'type': self.__schema_type__,
            'format': self.__schema_format__,
            'title': self.title,
            'description': self.description,
            'readOnly': self.readonly,
        }

    def parse(self, value):
        if value is None:
            return None
        elif isinstance(value, string_types):
            return aniso8601.parse_date(value)
        elif isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        else:
            raise ValueError('Unsupported Date format')

    def format(self, value):
        if isinstance(value, string_types):
            return value
        return value.isoformat()

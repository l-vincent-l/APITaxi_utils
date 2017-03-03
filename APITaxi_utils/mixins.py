# -*- coding: utf-8 -*-
from flask_security import current_user
from flask import request
from sqlalchemy_defaults import Column
from sqlalchemy import types as sqlalchemy_types
from sqlalchemy.schema import ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import inspect
from datetime import datetime
from . import fields as custom_fields
from flask_restplus.fields import Nested as fields_Nested
from flask_restplus import abort

class AsDictMixin(object):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class FilterOr404Mixin(object):
    @classmethod
    def filter_by_or_404(cls, *args, **kwargs):
        message = kwargs.pop('message', 'Unable to find {} for {}'.format(
            cls.__tablename__, kwargs))
        if args:
            query = cls.query.filter(*args, **kwargs)
        else:
            query = cls.query.filter_by(**kwargs)
        if hasattr(cls, 'added_at'):
            query = query.order_by(cls.added_at.desc())
        v = query.first()
        if not v:
            abort(404, message=message)
        return v

class GetOr404Mixin(object):
    @classmethod
    def get_or_404(cls, id_):
        v = cls.cache.get(id_)
        if not v:
            message = 'Unable to find {} with id {}'.format(cls.__tablename__, id_)
            abort(404, message=message)
        return v


class MarshalMixin(object):

    inspect_obj = None
    map_ = {
            sqlalchemy_types.Integer: lambda c: custom_fields.Integer(column=c),
            sqlalchemy_types.INTEGER: lambda c: custom_fields.Integer(column=c),
            sqlalchemy_types.Boolean: lambda c: custom_fields.Boolean(column=c),
            sqlalchemy_types.BOOLEAN: lambda c: custom_fields.Boolean(column=c),
            sqlalchemy_types.DateTime: lambda c: custom_fields.DateTime(column=c),
            sqlalchemy_types.DATETIME: lambda c: custom_fields.DateTime(column=c),
            sqlalchemy_types.Date: lambda c: custom_fields.Date(column=c),
            sqlalchemy_types.DATE: lambda c: custom_fields.Date(column=c),
            sqlalchemy_types.Float: lambda c: custom_fields.Float(column=c),
            sqlalchemy_types.FLOAT: lambda c: custom_fields.Float(column=c),
            sqlalchemy_types.Enum: lambda c: custom_fields.String(column=c,
                       enum=c.type.enums),
            sqlalchemy_types.String: lambda c: custom_fields.String(column=c)
        }


    @classmethod
    def marshall_obj(cls, show_all=False, filter_id=False, level=0, api=None):
        if level == 2:
            return {}
        cls.inspect_obj = inspect(cls)
        fields_cls = cls.list_fields()
        if not show_all and hasattr(cls, 'public_fields'):
            fields_cls = filter(lambda f: f.name in cls.public_fields, fields_cls)

        def to_keep(c):
            return not c.primary_key and len(c.foreign_keys) == 0\
                        and type(c.type) in cls.map_.keys()
        fields_cls = filter(to_keep, fields_cls)
        fields_cls = map(lambda c: (c.name,
                           cls.map_[type(c.type)](c)),
                         fields_cls)
        return_dict = dict(fields_cls)
        if cls.inspect_obj.relationships:
            for k, r in cls.inspect_obj.relationships.items():
                if k.startswith("_"):
                    continue
                if not show_all and hasattr(cls, 'public_relations') and k not in cls.public_relations:
                    continue
                value = r.mapper.class_.marshall_obj(show_all, filter_id, level=level+1)
                if len(value.keys()) == 0:
                    continue
                return_dict[k] = fields_Nested(api.model(k, value))
        return return_dict


    @classmethod
    def list_fields(cls):
        if not cls.inspect_obj:
            cls.inspect_obj = inspect(cls).columns
        columns = list(cls.inspect_obj.columns)
        if hasattr(cls, 'to_exclude'):
            columns = filter(lambda c: c.name not in cls.to_exclude(), columns)
        return columns



class HistoryMixin(MarshalMixin):
    added_at = Column(sqlalchemy_types.DateTime)
    added_via = Column(sqlalchemy_types.Enum('form', 'api', name="sources"), default='api')
    source = Column(sqlalchemy_types.String(255), default='added_by')
    last_update_at = Column(sqlalchemy_types.DateTime, nullable=True,
                           onupdate=datetime.now)

    @classmethod
    def to_exclude(cls):
        columns = filter(lambda f: isinstance(getattr(HistoryMixin, f), Column), HistoryMixin.__dict__.keys())
        return columns

    def __init__(self):
        self.added_via = 'form' if 'form' in request.url_rule.rule else 'api'
        self.source = 'added_by'
        self.added_by = current_user.id if not current_user.is_anonymous else None
        self.added_at = datetime.utcnow()

    def can_be_deleted_by(self, user):
        return user.has_role("admin") or self.added_by == user.id

    def can_be_edited_by(self, user):
        return user.has_role("admin") or self.added_by == user.id

    @classmethod
    def can_be_listed_by(cls, user):
        return user.has_role("admin") or user.has_role("operateur")


    def showable_fields(self, user):
        cls = self.__class__
        if user.has_role("admin") or self.added_by == user.id:
            return cls.list_fields()
        return cls.public_fields if hasattr(cls, "public_fields") else set()



#Source: https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/UniqueObject

def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        obj = cache[key]
        for k, v in kw.iteritems():
            try:
                setattr(obj, k, v)
            except AttributeError:
                pass
        session.add(obj)
        return obj
    else:
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            obj = q.first()
            if not obj:
                obj = constructor(*arg, **kw)
            else:
                for k, v in kw.iteritems():
                    try:
                        setattr(obj, k, v)
                    except AttributeError:
                        pass
            session.add(obj)
        cache[key] = obj
        return obj



def unique_constructor(scoped_session, hashfunc, queryfunc):
    def decorate(cls):
        def _null_init(self, *arg, **kw):
            pass
        def __new__(cls, bases, *arg, **kw):
            # no-op __new__(), called
            # by the loading procedure
            if not arg and not kw:
                return object.__new__(cls)

            session = scoped_session()

            def constructor(*arg, **kw):
                obj = object.__new__(cls)
                obj._init(*arg, **kw)
                return obj

            return _unique(
                        session,
                        cls,
                        hashfunc,
                        queryfunc,
                        constructor,
                        arg, kw
                   )

        # note: cls must be already mapped for this part to work
        cls._init = cls.__init__
        cls.__init__ = _null_init
        cls.__new__ = classmethod(__new__)
        return cls

    return decorate

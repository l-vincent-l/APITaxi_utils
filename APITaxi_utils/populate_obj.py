# -*- coding: utf-8 -*-
from .mixins import HistoryMixin

def create_obj_from_json(cls, json_obj, obj=None):
    cols = [k for k in cls.__table__.columns
            if k.name not in cls.to_exclude()
    ]
    if hasattr(cls, '_additionnal_columns'):
        cols += cls._additionnal_columns
    required_keys = [c.name for c in cols
                     if not c.nullable and not c.primary_key\
                     and (not hasattr(c, 'default') or c.default is None)
    ]
    for key in required_keys:
        if key not in json_obj or json_obj[key] is None:
            raise KeyError("Missing key: '{}'".format(key))

    keys = [k.name for k in cols]
    if hasattr(cls, '_additionnal_keys'):
        keys += cls._additionnal_keys
    return cls(**{k: json_obj[k] for k in map(lambda k: unicode(k), keys)
                  if k in json_obj
                 }
    )

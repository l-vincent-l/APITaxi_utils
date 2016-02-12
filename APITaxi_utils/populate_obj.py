# -*- coding: utf-8 -*-
from .mixins import HistoryMixin

def create_obj_from_json(cls, json_obj, obj=None):
    keys = [k for k in cls.__table__.columns if k.name not in HistoryMixin.to_exclude()]
    required_keys = [k.name for k in keys if not k.nullable and not k.primary_key]
    for key in required_keys:
        if key not in json_obj or json_obj[key] is None:
            raise KeyError(key)
    if obj is None:
        obj = cls()
    for k in keys:
        name = k.name
        if name not in json_obj:
            continue
        setattr(obj, name, json_obj[name])
    return obj

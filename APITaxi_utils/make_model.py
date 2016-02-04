# -*- coding: utf-8 -*-
import importlib
from flask.ext.restplus import fields as basefields

def make_model(filename, model_name, api, *args, **kwargs):
    module = importlib.import_module(".".join(['APITaxi', 'models', filename]))
    model = getattr(module, model_name)
    list_names = [filename, model_name]
    list_names.extend([str(i) for i in args])
    list_names.extend([k + "_" + str(v) for k, v in kwargs.items()])
    register_name = "_".join(list_names)
    details_dict = model.marshall_obj(*args, **kwargs)
    details = api.model(register_name + "_details", details_dict)
    return api.model(register_name,
        {"data": basefields.List(basefields.Nested(details))})

#coding: utf-8
from flask_restplus import abort

def Integer(options):
    def wrap(value):
        if value not in options:
            raise ValueError("{} is not in {}".format(value, options))
        return int(value)
    return wrap

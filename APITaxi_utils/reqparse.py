# -*- coding: utf-8 -*-
from flask_restful import abort, marshal
from flask_restful.reqparse import RequestParser

class DataJSONParser(RequestParser):

    def __init__(self, max_length=1, min_length=0, filter_=None, *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        self.filter_ = filter_
        super(DataJSONParser, self).__init__(*args, **kwargs)
        self.add_argument("data", location="json", required=True,
                         type=self.check_data, nullable=False, ignore=True)

    def check_data(self, value):
        if not isinstance(value, list) or\
           not all(map(lambda v: isinstance(v, dict), value)):
            raise ValueError("data must contain a list of objects")
        if len(value) > self.max_length:
            raise ValueError("data must contain at must {} object".format(self.max_length))
        if len(value) < self.min_length:
            raise ValueError("data must contain at most {} object".format(self.max_length))
        return value

    def get_data(self):
        if self.filter_ is None:
            return self.parse_args()['data']
        else:
            return marshal(self.parse_args(), self.filter_)['data']

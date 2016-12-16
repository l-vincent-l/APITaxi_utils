# -*- coding: utf-8 -*-
from flask_restful import reqparse, abort

class DataJSONParser(reqparse.RequestParser):

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop('max_length') if 'max_length' in kwargs else 1
        self.min_length = kwargs.pop('min_length') if 'min_length' in kwargs else 0
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
        return self.parse_args()['data']

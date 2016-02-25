#coding: utf-8
from flask import request, g, abort
from .request_wants_json import request_wants_json

valid_versions = ['1', '2']
def check_version(sender, **extra):
    if not request_wants_json():
        return
    if request.url_rule is None:
        return
    endpoint = request.url_rule.endpoint
    if endpoint == 'api.specs' or endpoint == 'static' or endpoint.startswith('js_bo'):
        return
    version = request.headers.get('X-VERSION', None)
    if version not in valid_versions:
        abort(404, message="Invalid version, valid versions are: {}".format(valid_versions))
    g.version = int(version)

def add_version_header(sender, response, **extra):
    response.headers['X-VERSION'] = request.headers.get('X-VERSION')

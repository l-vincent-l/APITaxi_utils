# -*- coding: utf-8 -*-
from flask_restplus import Resource, abort
from flask import request, url_for
from flask_security import current_user
from APITaxi_utils.request_wants_json import request_wants_json
from datetime import datetime
from APITaxi_utils.slack import slack as slacker

class ResourceFileOrJSON(Resource):

    def dispatch_request(self, *args, **kwargs):
        if not request.is_json:
            before = self.post.__apidoc__['validate']
            self.post.__apidoc__['validate'] = False

        resp = super(ResourceFileOrJSON, self).dispatch_request(*args, **kwargs)

        if not request.is_json:
            self.post.__apidoc__['validate'] = before
        return resp

    def post(self):
        if request.is_json:
            return self.post_json()
        elif 'file' in request.files:
            return self.post_file()
        else:
            abort(400, message="Unable to find file")

    def post_file(self):
        filename = "{}-{}-{}.csv".format(self.filetype, current_user.email,
                str(datetime.now()))
        self.documents.save(request.files['file'], name=filename)
        slack = slacker()
        if slack:
            slack.chat.post_message('#taxis',
                'Un nouveau fichier {} a été envoyé par {}. {}'.format(
                    self.filetype, current_user.email,
                    url_for('documents.documents', filename=filename, _external=True)
                )
            )
        return "OK"

import json
from flask import Blueprint, Response
from flask.views import MethodView
from flask.ext.script import Manager
from fcs.models import Undertaking

api = Blueprint('api', __name__)

api_manager = Manager()


@api_manager.command
def test():
    """ Return a list of all undertakings """
    import pprint

    undertakings = Undertaking.query.all()

    res = [u.as_dict() for u in undertakings]
    pprint.pprint(res)


class ApiView(MethodView):
    def dispatch_request(self):
        resp = super(ApiView, self).dispatch_request()

        if isinstance(resp, (dict, list, tuple)):
            return Response(json.dumps(resp),  mimetype='application/json')

        return resp


class UndertakingList(ApiView):
    def get(self):
        return [u.as_dict() for u in Undertaking.query.all()]


api.add_url_rule('/undertaking/list',
                 view_func=UndertakingList.as_view('undertaking-list'))

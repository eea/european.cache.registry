import json

from flask import current_app
from flask import request
from flask import Response
from flask.views import MethodView


def pretty_float_json_dumps(json_obj):
    dumps_str = ""

    if isinstance(json_obj, dict):
        dumps_str += "{"
        for k, v in json_obj.items():
            dumps_str += json.dumps(k) + ":"
            if isinstance(v, float):
                float_tmp_str = ("%.16f" % v).rstrip("0")
                dumps_str += (
                    float_tmp_str + "0"
                    if float_tmp_str.endswith(".")
                    else float_tmp_str
                ) + ","
            elif isinstance(v, list) or isinstance(v, dict):
                dumps_str += pretty_float_json_dumps(v) + ","
            else:
                dumps_str += pretty_float_json_dumps(v) + ","
        if dumps_str.endswith(","):
            dumps_str = dumps_str[:-1]
        dumps_str += "}"
    elif isinstance(json_obj, list):
        dumps_str += "["
        for v in json_obj:
            if isinstance(v, float):
                float_tmp_str = ("%.16f" % v).rstrip("0")
                dumps_str += (
                    float_tmp_str + "0"
                    if float_tmp_str.endswith(".")
                    else float_tmp_str
                ) + ","
            elif isinstance(v, list) or isinstance(v, dict):
                dumps_str += pretty_float_json_dumps(v) + ","
            else:
                dumps_str += pretty_float_json_dumps(v) + ","
        if dumps_str.endswith(","):
            dumps_str = dumps_str[:-1]
        dumps_str += "]"
    else:
        dumps_str += json.dumps(json_obj)
    return dumps_str


class ApiView(MethodView):
    model = None

    def dispatch_request(self, use_decimal_notation=False, **kwargs):
        if not ApiView.authenticate():
            resp = {
                "status": "Unauthorized",
                "message": "You need to be authenticated "
                "in order to access this resource.",
            }
            status_code = 401
            return (
                Response(json.dumps(resp, indent=2), mimetype="application/json"),
                status_code,
            )

        resp = super(ApiView, self).dispatch_request(**kwargs)

        if isinstance(resp, (dict, list, tuple)):
            if use_decimal_notation:
                return Response(
                    pretty_float_json_dumps(resp), mimetype="application/json"
                )
            else:
                return Response(json.dumps(resp, indent=2), mimetype="application/json")

        return resp

    @classmethod
    def authenticate(cls):
        token = current_app.config.get("API_TOKEN", "")
        authorization = request.headers.get("Authorization", "")
        if authorization == token:
            return True
        return False

    @classmethod
    def serialize(cls, obj, **kwargs):
        pop_id = kwargs.get("pop_id", True)
        if not obj:
            return None
        data = obj.as_dict()
        if pop_id:
            data.pop("id")
        return data


class ListView(ApiView):
    def get_queryset(self, **kwargs):
        return self.model.query.all()

    def get(self, **kwargs):
        return [self.serialize(u) for u in self.get_queryset(**kwargs)]


class DetailView(ApiView):
    def get_object(self, pk, **kwargs):
        return self.model.query.get_or_404(pk)

    def get(self, pk, **kwargs):
        return self.serialize(self.get_object(pk, **kwargs))

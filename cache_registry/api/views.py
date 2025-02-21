import json

from flask import current_app
from flask import request
from flask import Response
from flask.views import MethodView


class ApiView(MethodView):
    model = None

    def __init__(self):
        self.status_code = 200
        super(ApiView, self).__init__()

    def dispatch_request(self, **kwargs):
        if not ApiView.authenticate():
            resp = {
                "status": "Unauthorized",
                "message": "You need to be authenticated "
                "in order to access this resource.",
            }
            self.status_code = 401
            return (
                Response(json.dumps(resp, indent=2), mimetype="application/json"),
                self.status_code,
            )

        resp = super(ApiView, self).dispatch_request(**kwargs)

        if isinstance(resp, (dict, list, tuple)):
            return (
                Response(json.dumps(resp, indent=2), mimetype="application/json"),
                self.status_code,
            )

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
        page = request.args.get("page")
        per_page = request.args.get("per-page")
        if page and per_page:
            return self.model.query.paginate(int(page), int(per_page)).items
        return self.model.query.all()

    def get(self, **kwargs):
        return [self.serialize(u) for u in self.get_queryset(**kwargs)]


class DetailView(ApiView):
    def get_object(self, pk, **kwargs):
        return self.model.query.get_or_404(pk)

    def get(self, pk, **kwargs):
        return self.serialize(self.get_object(pk, **kwargs))

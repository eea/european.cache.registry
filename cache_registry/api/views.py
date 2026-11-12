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


def remove_overridden_licences(data, override_setting, pk, year=None):
    """Drop the cached licences that are fully replaced by patch data.

    The override setting is a list of {"company_id": .., "year": ..} entries;
    an entry without year overrides all the years of that company.
    """
    overrides = [
        element
        for element in current_app.config.get(override_setting, [])
        if element.get("company_id") == pk
        and (year is None or element.get("year") in (None, year))
    ]
    if not overrides:
        return data
    if any(element.get("year") is None for element in overrides):
        return []
    years = {element["year"] for element in overrides}
    return [licence for licence in data if licence.get("year") not in years]

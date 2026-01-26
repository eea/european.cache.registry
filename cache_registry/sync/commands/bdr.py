import requests

from flask import current_app

from cache_registry.models import db
from cache_registry.sync import sync_manager
from cache_registry.sync.auth import InvalidResponse, Unauthorized
from cache_registry.sync.bdr import get_absolute_url
from cache_registry.sync.parsers import parse_company


def get_old_companies(obligation):
    token = current_app.config.get("BDR_API_KEY", "")
    if obligation.lower() == "fgas":
        obligation = "fgases"
    url = get_absolute_url("BDR_API_URL", f"/company/obligation/{obligation}/")
    headers = {"Authorization": token}
    ssl_verify = current_app.config["HTTPS_VERIFY"]
    response = requests.get(url, headers=headers, verify=ssl_verify)
    if response.status_code in (401, 403):
        raise Unauthorized()
    if response.status_code != 200:
        raise InvalidResponse()

    return response.json()


@sync_manager.command("bdr")
def bdr():
    return call_command_bdr()


def call_command_bdr():
    obligations = current_app.config.get("MANUAL_VERIFY_ALL_COMPANIES", [])
    for obl in obligations:
        if obl:
            print("Getting obligation: ", obl)
            companies = get_old_companies(obl.lower())
            print(len([parse_company(c, obl) for c in companies]), "values")
    db.session.commit()
    return True

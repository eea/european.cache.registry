import json
import logging
import requests
import os

from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from flask import current_app
from sqlalchemy import desc

from cache_registry.models import *
from cache_registry.sync import parsers
from cache_registry.sync.auth import get_auth, Unauthorized, InvalidResponse

from instance.settings import FGAS


def get_logger(module_name):
    """Generate a logger."""
    logger = logging.getLogger(module_name)
    log_file_updated = "ecr_updates_logging.log"
    logger.setLevel(logging.INFO)
    logger.propagate = False
    file_handler_updates = RotatingFileHandler(
        log_file_updated, maxBytes=20971520, backupCount=1
    )  # 20mb
    logger.handlers = [file_handler_updates]

    return logger


def get_response(url, params):
    auth = get_auth("API_USER", "API_PASSWORD")
    headers = dict(zip(("user", "password"), auth))
    ssl_verify = current_app.config["HTTPS_VERIFY"]

    response = requests.get(url, params=params, headers=headers, verify=ssl_verify)

    if response.status_code == 404:
        return []

    if response.status_code == 401:
        raise Unauthorized()

    if response.status_code != 200:
        raise InvalidResponse()

    if not params.get("pageSize"):
        return response.json()
    try:
        no_of_pages = int(response.headers["numberOfPages"])
    except (ValueError, KeyError):
        no_of_pages = 1
    response_json = response.json()

    for page_number in range(2, no_of_pages + 1):
        params["pageNumber"] = page_number
        response = requests.get(url, params=params, headers=headers, verify=ssl_verify)
        if response.status_code != 200:
            raise InvalidResponse()
        response_json += response.json()

    return response_json


def get_response_offset(url, params):
    """
    Docstring for get_response_offset

    :param url: URL to fetch data from
    :param params: Query parameters for the request. Manages pagination using 'offset' and 'pageSize'.
    :return: Description
    """
    auth = get_auth("API_USER", "API_PASSWORD")
    headers = dict(zip(("user", "password"), auth))
    ssl_verify = current_app.config["HTTPS_VERIFY"]

    response = requests.get(url, params=params, headers=headers, verify=ssl_verify)

    if response.status_code == 401:
        raise Unauthorized()

    if response.status_code == 404:
        return []

    if response.status_code != 200:
        raise InvalidResponse()

    if not params.get("pageSize", 100):
        return response.json()

    response_data = response.json()
    aggregated_response = response_data.get("rows", [])

    keep_fetching = response_data.get("rowCount", 0) > params.get(
        "offset", 0
    ) + params.get("pageSize", 100)

    while keep_fetching:
        params["offset"] = params.get("offset", 0) + params.get("pageSize", 100)
        response = requests.get(url, params=params, headers=headers, verify=ssl_verify)
        if response.status_code != 200:
            raise InvalidResponse()
        response_data = response.json()
        aggregated_response += response_data.get("rows", [])
        keep_fetching = response_data.get("rowCount", 0) > params.get(
            "offset", 0
        ) + params.get("pageSize", 100)

    return aggregated_response


def set_ecas_id(obj):
    """Set ecas_id for an object if it doesn't have one using the username."""
    if not obj.ecas_id:
        if "@" not in obj.username:
            obj.ecas_id = obj.username


def update_contact_persons(obj, contact_persons):
    unique_emails = set([cp.get("email") for cp in contact_persons])
    existing_persons = obj.contact_persons

    for contact_person in contact_persons:
        user = None
        username = contact_person["username"]
        # Check if we have a user with that username
        by_username = User.query.filter_by(username=username).first()
        if not by_username:
            email = contact_person["email"]
            # Check if we have a user with that email
            by_email = User.query.filter_by(email=email).first()
            # If we have an email as username, check for duplicate emails
            if "@" in username:
                if len(unique_emails) != len(contact_persons):
                    # If we have duplicate emails, don't match any
                    by_email = None

        user = by_username or by_email

        if user:
            do_update = False
            for key, value in contact_person.items():
                if value != getattr(user, key):
                    do_update = True
            if do_update:
                parsers.update_obj(user, contact_person)
                set_ecas_id(user)
        else:
            user = User(**contact_person)
            set_ecas_id(user)
            db.session.add(user)
        if user not in existing_persons:
            obj.contact_persons.append(user)

        current_emails = [p.get("email") for p in contact_persons]
        current_usernames = [p.get("username") for p in contact_persons]
        for person in obj.contact_persons:
            if (
                person.email not in current_emails
                or person.username not in current_usernames
            ):
                obj.contact_persons.remove(person)


def update_ms_accreditation_issuing_countries(obj, ms_accreditation):
    """Update issuing countries for ms_accreditation."""
    for country in ms_accreditation["ms_accreditation_issuing_countries"]:
        if country not in obj.ms_accreditation_issuing_countries:
            obj.ms_accreditation_issuing_countries.append(country)
    for country in obj.ms_accreditation_issuing_countries:
        if country not in ms_accreditation["ms_accreditation_issuing_countries"]:
            obj.ms_accreditation_issuing_countries.remove(country)


def loaddata(fixture, session=None):
    if not session:
        session = db.session
    if not os.path.isfile(fixture):
        print("Please provide a fixture file name")
    else:
        objects = get_fixture_objects(fixture)
    session.commit()
    for object in objects:
        database_object = (
            eval(object["model"]).query.filter_by(id=object["fields"]["id"]).first()
        )
        if not database_object:
            session.add(eval(object["model"])(**object["fields"]))
            session.commit()
        else:
            for key, value in object["fields"].items():
                setattr(database_object, key, value)
            session.add(database_object)
            session.commit()


def get_fixture_objects(file):
    with open(file) as f:
        return json.loads(f.read())


def get_last_update(days, updated_since, domain=FGAS, model_name=Undertaking):
    if updated_since:
        try:
            last_update = datetime.strptime(updated_since, "%d/%m/%Y")
        except ValueError:
            print("Invalid date format. Please use DD/MM/YYYY")
            return False
    else:
        days = int(days)
        if days > 0:
            last_update = datetime.now() - timedelta(days=days)
        else:
            queryset = model_name.query
            if hasattr(model_name, "domain"):
                queryset = queryset.filter_by(domain=domain)

            last = queryset.order_by(desc(model_name.date_updated)).first()
            last_update = last.date_updated - timedelta(days=1) if last else None

    print(f"Using last_update {last_update}")
    return last_update


def log_changes(last_update, undertakings_count, domain):
    if isinstance(last_update, datetime):
        last_update = last_update.date()
    log = OrganizationLog(
        organizations=undertakings_count, using_last_update=last_update, domain=domain
    )
    db.session.add(log)

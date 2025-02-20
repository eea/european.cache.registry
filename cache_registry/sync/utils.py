import logging
import requests
from flask import current_app
from logging.handlers import RotatingFileHandler

from cache_registry.models import db, User
from cache_registry.sync import parsers
from cache_registry.sync.auth import get_auth, Unauthorized, InvalidResponse


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

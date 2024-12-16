import requests
import json
import click
import urllib.parse

from io import BytesIO
from scrapy.selector import Selector
from zipfile import ZipFile
from urllib.request import urlopen

from datetime import datetime, timedelta

from cache_registry.sync.parsers import parse_company
from flask import current_app
from sqlalchemy import desc
from cache_registry.models import (
    Auditor,
    Undertaking,
    db,
    OrganizationLog,
    DeliveryLicence,
    Stock,
)
from instance.settings import FGAS, ODS
from cache_registry.sync import sync_manager
from cache_registry.sync.auditors import get_latest_auditors, update_auditor
from cache_registry.sync.auth import cleanup_unused_users, InvalidResponse, Unauthorized
from cache_registry.sync.bdr import (
    get_bdr_collections,
    update_bdr_col_name,
    get_absolute_url,
    call_bdr,
    check_if_company_folder_exists,
)
from cache_registry.sync.licences import (
    aggregate_licences_to_undertakings,
    aggregate_licence_to_substance,
    delete_all_substances_and_licences,
    get_licences,
    get_or_create_substance,
    get_or_create_delivery,
    parse_licence,
)
from cache_registry.sync.undertakings import get_latest_undertakings, update_undertaking

from cache_registry.sync.fgases import eea_double_check_fgases
from cache_registry.sync.ods import eea_double_check_ods


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


def patch_undertaking_old_gb_represent(external_id, data):
    external_id = str(external_id)
    patch = current_app.config.get("PATCH_GB_OLD_REPR", {})
    if external_id in patch:
        represent = data.get("euLegalRepresentativeCompany")
        if not represent:
            print(f"Patching old gb represent on undertaking: {external_id}")
            data.update(patch[external_id])
    return data


def update_undertakings(undertakings, check_function):
    undertakings_count = 0
    undertakings_for_call_bdr = []
    for undertaking in undertakings:
        undertaking_exists = Undertaking.query.filter_by(
            external_id=undertaking["id"]
        ).first()
        if not undertaking["domain"] == ODS:
            undertaking = patch_undertaking_old_gb_represent(
                undertaking["id"], undertaking
            )
        check_passed = check_function(undertaking)
        if undertaking_exists:
            if undertaking_exists.domain == "FGAS":
                if undertaking_exists.check_passed and not check_passed:
                    message = f"Company {undertaking_exists.external_id} has failed the checks"
                    current_app.logger.warning(message)
        if (
            (not undertaking["@type"] == "ODSUndertaking")
            or check_passed
            or undertaking_exists
        ):
            (_, represent_changed) = update_undertaking(
                undertaking, check_passed=check_passed
            )
            undertakings_count += 1
            if check_passed or represent_changed:
                undertakings_for_call_bdr.append(undertaking)
    return undertakings_for_call_bdr, undertakings_count


def log_changes(last_update, obj_count, domain):
    if isinstance(last_update, datetime):
        last_update = last_update.date()
    log = OrganizationLog(
        organizations=obj_count, using_last_update=last_update, domain=domain
    )
    db.session.add(log)


def print_all_undertakings(undertakings):
    """
    only used for FGAS as ODS has EU_TYPE countries only
    """
    undertakings_count = 0
    for undertaking in undertakings:
        if undertaking["euLegalRepresentativeCompany"] is None:
            undertaking_address = undertaking.get("address", None)
            if undertaking_address is not None:
                undertaking_country = undertaking_address.get("country", None)
                if undertaking_country is not None:
                    undertaking_country_type = undertaking_country.get("type", None)
                    if undertaking_country_type == "NONEU_TYPE":
                        undertakings_count += 1
                        print(undertaking)

    print(undertakings_count, "values")


@sync_manager.command("auditors")
@click.option("-d", "--days", "days", help="Number of days the update is done for.")
@click.option("-u", "--updated", "updated_since", help="Date in DD/MM/YYYY format")
@click.option("-p", "--page_size", "page_size", help="Page size")
@click.option("-i", "--auditor_uid", "uid", help="Auditor uid")
def auditors(days=7, updated_since=None, page_size=200, uid=""):
    return call_auditors(days, updated_since, page_size, uid)


def call_auditors(days=7, updated_since=None, page_size=200, uid=""):
    if not uid:
        last_update = get_last_update(days, updated_since, model_name=Auditor)
    else:
        last_update = None
        print(f"Fetching data for auditor {uid}")

    auditors_data = get_latest_auditors(
        updated_since=last_update, page_size=page_size, uid=uid
    )
    for auditor_dict in auditors_data:
        update_auditor(auditor_dict)

    cleanup_unused_users()

    if not uid:
        auditors_count = len(auditors_data)
        log_changes(last_update, auditors_count, domain=FGAS)
        print(auditors_count, "values")

    db.session.commit()
    return True


@sync_manager.command("fgases")
@click.option("-d", "--days", "days", help="Number of days the update is done for.")
@click.option("-u", "--updated", "updated_since", help="Date in DD/MM/YYYY format")
@click.option("-p", "--page_size", "page_size", help="Page size")
@click.option("-i", "--external_id", "id", help="External id of a company")
def fgases(days=7, updated_since=None, page_size=200, id=None):
    return call_fgases(days, updated_since, page_size, id)


def call_fgases(days=3, updated_since=None, page_size=200, id=None):
    if not id:
        last_update = get_last_update(days, updated_since, domain=FGAS)
    else:
        last_update = None
        print(f"Fetching data for company {id}")

    undertakings = get_latest_undertakings(
        type_url="/latest/fgasundertakings/",
        updated_since=last_update,
        page_size=page_size,
        id=id,
        domain=FGAS,
    )
    (undertakings_for_call_bdr, undertakings_count) = update_undertakings(
        undertakings, eea_double_check_fgases
    )
    cleanup_unused_users()
    if not id:
        log_changes(last_update, undertakings_count, domain=FGAS)
        print(undertakings_count, "values")
    db.session.commit()
    for undertaking in undertakings_for_call_bdr:
        undertaking_obj = Undertaking.query.filter_by(
            external_id=undertaking["external_id"], domain=FGAS
        ).first()
        if undertaking_obj.check_passed:
            if not check_if_company_folder_exists(undertaking_obj):
                call_bdr(undertaking_obj, undertaking_obj.oldcompany_account)
    return True


@sync_manager.command("undertaking_remove")
@click.option("-i", "--external_id", "external_id", help="External id of a company")
@click.option("-d", "--domain", "domain", help="Domain")
def undertaking_remove(external_id, domain):
    undertaking = Undertaking.query.filter_by(
        external_id=external_id, domain=domain
    ).first()
    if undertaking:
        msg = (
            f"Removing undertaking name: {undertaking.name}"
            " with id: {undertaking.id}"
        )
        undertaking.represent_history.clear()
        undertaking.types.clear()
        undertaking.businessprofiles.clear()
        db.session.commit()
        db.session.delete(undertaking)
        db.session.commit()
    else:
        msg = f"No company with id: {external_id} found in the db"
        current_app.logger.warning(msg)


@sync_manager.command("old_companies_sync")
@click.option("-u", "--updated", "updated_since", help="Date in dd-MM-YYYY format")
def old_companies_sync(updated_since=None):
    updated = datetime.strptime("01-01-2018", "%d-%m-%Y")
    undertakings = Undertaking.query.filter(
        Undertaking.date_updated <= updated, Undertaking.domain == "FGAS"
    )
    for undertaking in undertakings:
        call_fgases(id=undertaking.external_id)


@sync_manager.command("ods")
@click.option("-d", "--days", "days", help="Number of days the update is done for.")
@click.option("-u", "--updated", "updated_since", help="Date in DD/MM/YYYY format")
@click.option("-p", "--page_size", "page_size", help="Page size")
@click.option("-i", "--external_id", "id", help="External id of a company")
def ods(days=7, updated_since=None, page_size=200, id=None):
    return call_ods(days, updated_since, page_size, id)


def call_ods(days=3, updated_since=None, page_size=200, id=None):
    if not id:
        last_update = get_last_update(days, updated_since, domain=ODS)
    else:
        last_update = None
        print(f"Fetching data for company {id}")

    undertakings = get_latest_undertakings(
        type_url="/latest/odsundertakings/",
        updated_since=last_update,
        page_size=page_size,
        id=id,
        domain=ODS,
    )
    (undertakings_for_call_bdr, undertakings_count) = update_undertakings(
        undertakings, eea_double_check_ods
    )
    cleanup_unused_users()
    if not id:
        log_changes(last_update, undertakings_count, domain=ODS)
        print(undertakings_count, "values")
    db.session.commit()
    for undertaking in undertakings_for_call_bdr:
        undertaking_obj = Undertaking.query.filter_by(
            external_id=undertaking["external_id"], domain=ODS
        ).first()
        if undertaking_obj.check_passed:
            if not check_if_company_folder_exists(undertaking_obj):
                call_bdr(undertaking_obj, undertaking_obj.oldcompany_account)
    return True


@sync_manager.command("licences")
@click.option("-y", "--year", "year", help="Licences from year x")
@click.option("-p", "--page_size", "page_size", help="Page size")
def licences(year, page_size=200):
    return call_licences(year, page_size)


def call_licences(year, page_size=200):
    data = get_licences(year=year, page_size=page_size)
    companies = aggregate_licences_to_undertakings(data)
    for company, data in companies.items():
        undertaking = Undertaking.query.filter_by(
            external_id=company, domain="ODS"
        ).first()
        delivery_licence = get_or_create_delivery(year, undertaking)
        if (
            delivery_licence.updated_since is None
            or data["updated_since"] > delivery_licence.updated_since
        ):
            delete_all_substances_and_licences(delivery_licence)
            for licence in data["licences"]:
                substance = get_or_create_substance(delivery_licence, licence)
                if not substance:
                    sub_name = f"{licence['chemicalName']}({licence['mixtureNatureType'].lower()})"
                    message = f"Substance {sub_name} could not be translated or Country \
                               code {licence['organizationCountryName']} or Substance \
                               country code {licence['internationalPartyCountryName']} \
                               could not be translated or licence does not have an approved state."
                    current_app.logger.error(message)
                    continue
                parse_licence(licence, undertaking.id, substance)
            aggregate_licence_to_substance(delivery_licence, year)
            delivery_licence.updated_since = data["updated_since"]
            db.session.add(delivery_licence)
            db.session.commit()
    return True


@sync_manager.command("fgases_debug_noneu")
@click.option("-u", "--updated", "updated_since", help="Date in DD/MM/YYYY format")
@click.option("-p", "--page_size", "page_size", help="Page size")
def fgases_debug_noneu(days=7, updated_since=None, page_size=None):
    return call_fgases_debug_noneu(days, updated_since, page_size)


def call_fgases_debug_noneu(days=3, updated_since=None, page_size=None):
    # returns a list with all NON EU companies without a legal representative
    last_update = get_last_update(days, updated_since, domain=FGAS)
    undertakings = get_latest_undertakings(
        type_url="/latest/fgasundertakings/",
        updated_since=last_update,
        page_size=page_size,
        domain=FGAS,
    )
    print_all_undertakings(undertakings)
    return True


@sync_manager.command("sync_collections_title")
def sync_collections_title():
    return call_sync_collections_title()


def call_sync_collections_title():
    collections = get_bdr_collections()
    if collections:
        colls = {}
        for collection in collections:
            c_id = collection.get("company_id")
            if c_id:
                if not colls.get(c_id):
                    colls[c_id] = collection
                else:
                    print(
                        f"Duplicate collection for company_id: {c_id} have {colls[c_id]} \
                        and found {collection}"
                    )
        undertakings = Undertaking.query
        for undertaking in undertakings:
            ext_id = str(undertaking.external_id)
            title = undertaking.name
            coll = colls.get(ext_id)
            if coll and coll.get("title") != title:
                if update_bdr_col_name(undertaking):
                    print(f"Updated collection title for: {ext_id}")
    return True


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


@sync_manager.command("remove_all_licences_substances")
@click.option("-y", "--year", "year")
def remove_all_licences_substances(year=None):
    if year:
        deliveries = DeliveryLicence.query.filter_by(year=year)
    else:
        deliveries = DeliveryLicence.query.all()
    for delivery in deliveries:
        delete_all_substances_and_licences(delivery)
        delivery.updated_since = None
        db.session.add(delivery)
        db.session.commit()
    return True


@sync_manager.command("import_stocks_json")
@click.option("-f", "--file", "file", help="Json file with stocks")
def import_stocks_json(file):
    with open(file) as f:
        json_data = f.read()
        data = json.loads(json_data)

    for stock in data:
        code = stock["code"]
        try:
            int(code)
            undertaking = Undertaking.query.filter_by(external_id=code).first()
        except ValueError:
            undertaking = Undertaking.query.filter_by(oldcompany_account=code).first()
        if not undertaking:
            year = stock["year"]
            substance_name_form = stock["substance_name_form"]
            code = stock["code"]
            type = stock["type"]
            print(
                f"Stock {year} - {substance_name_form} - {code} - {type} \
                 was not imported as undertaking does not exist."
            )
            continue
        stock_object = Stock.query.filter_by(
            year=stock["year"],
            substance_name_form=stock["substance_name_form"],
            code=stock["code"],
            type=stock["type"],
        ).first()
        if not stock_object:
            stock_object = Stock(
                year=stock["year"],
                substance_name_form=stock["substance_name_form"],
                code=stock["code"],
                is_virgin=bool(stock["is_virgin"]),
                result=stock["result"],
                type=stock["type"],
                undertaking_id=undertaking.id,
                undertaking=undertaking,
            )
            db.session.add(stock_object)
            db.session.commit()
        else:
            stock_object.is_virgin = bool(stock["is_virgin"])
            stock_object.result = stock["result"]
            stock_object.type = stock["type"]
            db.session.add(stock_object)
            db.session.commit()


@sync_manager.command("import_oldcompany")
@click.option("-f", "--file", "file", help="Json file with stocks")
def import_oldcompany(file):
    import csv

    with open(file, newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in spamreader:
            undertaking = Undertaking.query.filter_by(external_id=row[1]).first()
            if undertaking:
                undertaking.oldcompany_account = row[0]
                db.session.add(undertaking)
                db.session.commit()


@sync_manager.command("stocks")
@click.option("-y", "--year", "year", help="Year to use")
def stocks(year=None):
    return call_stocks(year)


def _update_or_create_stocks(data, undertaking):
    created = False
    stock = Stock.query.filter_by(
        year=data["year"],
        type=data["type"],
        substance_name_form=data["substance_name_form"],
        undertaking=undertaking,
        code=str(undertaking.external_id),
        undertaking_id=undertaking.id,
    ).first()
    if stock:
        stock.is_virgin = data["is_virgin"]
        stock.result = data["result"]
    else:
        stock = Stock(
            year=data["year"],
            type=data["type"],
            substance_name_form=data["substance_name_form"],
            is_virgin=data["is_virgin"],
            result=data["result"],
            code=str(undertaking.external_id),
            undertaking=undertaking,
            undertaking_id=undertaking.id,
        )
        created = True
    db.session.add(stock)
    db.session.commit()
    return stock, created


def call_stocks(year=None):
    if year:
        year = int(year)
    else:
        year = datetime.now().year
    include_test_data = current_app.config.get("STOCKS_INCLUDE_TESTDATA", "No")
    params = urllib.parse.urlencode(
        {
            "opt_showresult": "false",
            "opt_servicemode": "sync",
            "Upper_limit": year,
            "Include_testdata": include_test_data,
        }
    )
    url = "?".join([current_app.config.get("STOCKS_API_URL", ""), params])
    headers = {"Authorization": current_app.config.get("STOCKS_API_TOKEN", "")}
    ssl_verify = current_app.config["HTTPS_VERIFY"]
    response = requests.get(url, headers=headers, verify=ssl_verify)
    a_href = Selector(response=response).xpath("//a/@href").get()
    resp_file = urlopen(a_href)
    data = resp_file.read()

    myzip = ZipFile(BytesIO(data))
    file_name = myzip.namelist()[0]
    res = myzip.open(file_name).read()
    json_data = json.loads(res)
    stocks = Stock.query.all()
    stocks_count = len(stocks)
    for stock in stocks:
        db.session.delete(stock)
    print(f"Deleted {stocks_count} stocks")
    stocks_count = 0
    for stock in json_data:
        if stock["company_id"].startswith("ods"):
            undertaking = Undertaking.query.filter_by(
                oldcompany_account=stock["company_id"], domain="ODS"
            ).first()
        else:
            undertaking = Undertaking.query.filter_by(
                external_id=stock["company_id"], domain="ODS"
            ).first()
        if undertaking:
            stock, created = _update_or_create_stocks(stock, undertaking)
            if created:
                stocks_count += 1
    print(f"Created {stocks_count} stocks")
    return True

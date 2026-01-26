from datetime import datetime, date
from math import ceil

from flask import current_app
from sqlalchemy import func

from cache_registry.models import (
    CountryCodesConversion,
    DeliveryLicence,
    LicenceDetailsConversion,
    Substance,
    SubstanceNameConversion,
    Undertaking,
    db,
)


CUSTOMS_PROCEDURE_TO_LIC_USE_KIND_CONVERSION = {
    "Release for free circulation": "free circulation",
    "Release for free circulation - VAT exempt": "free circulation",
    "Release for free circulation - no VAT paid": "free circulation",
    "Re-import - with release for free circulation": "free circulation",
    "Re-export": "re-export",
    "Permanent export": "permanent export",
    "Transit - non-community goods": "transit",
    "Release for free circulation - redispatched": "free circulation",
    "Inward processing - suspension system": "inward processing",
    "Inward processing - drawback procedure": "inward processing",
}


def translate_date(date_string):
    if not date_string:
        return date.today()
    date_with_time = datetime.strptime(date_string[0:10], "%Y-%m-%d")
    return date(
        year=date_with_time.year, month=date_with_time.month, day=date_with_time.day
    )


def delete_all_substances_and_licences(delivery_licence):
    substances = Substance.query.filter_by(deliverylicence=delivery_licence).all()
    for substance in substances:
        db.session.delete(substance)
        db.session.commit()


def get_or_create_delivery(year, undertaking):
    delivery = DeliveryLicence.query.filter_by(
        year=year, undertaking=undertaking
    ).first()
    if delivery:
        return delivery
    delivery = DeliveryLicence(year=year, undertaking=undertaking)
    db.session.add(delivery)
    db.session.commit()
    return delivery


def get_or_create_substance(delivery_licence, licence):
    if licence["licenceState"].lower() not in ["expired", "closed"]:
        return None
    if licence["mixtureNatureType"].lower() != "virgin":
        ec_substance_name = f"{licence['chemicalName']} (non-virgin)"
    else:
        ec_substance_name = (
            f"{licence['chemicalName']} ({licence['mixtureNatureType'].lower()})"
        )
    substance_conversion = SubstanceNameConversion.query.filter_by(
        ec_substance_name=ec_substance_name
    ).first()
    if not substance_conversion:
        return None
    country = CountryCodesConversion.query.filter(
        func.lower(CountryCodesConversion.country_name_short_en)
        == func.lower(licence["organizationCountryName"])
    ).first()
    if not country:
        return None
    s_country = CountryCodesConversion.query.filter(
        func.lower(CountryCodesConversion.country_name_short_en)
        == func.lower(licence["internationalPartyCountryName"])
    ).first()
    if not s_country:
        return None
    licence_details = LicenceDetailsConversion.query.filter_by(
        template_detailed_use_code=licence["templateDetailedUseCode"]
    ).first()
    if not licence_details:
        return None
    lic_use_kind = CUSTOMS_PROCEDURE_TO_LIC_USE_KIND_CONVERSION.get(
        licence["customProcedureName"], ""
    )
    substance = Substance.query.filter_by(
        substance=substance_conversion.corrected_name,
        organization_country_name=country.country_code_alpha2,
        lic_use_desc=licence_details.lic_use_desc,
        lic_use_kind=lic_use_kind,
        deliverylicence=delivery_licence,
        year=delivery_licence.year,
        lic_type=licence_details.lic_type,
        s_orig_country_name=s_country.country_code_alpha2,
    ).first()
    if not substance:
        substance = Substance(
            substance=substance_conversion.corrected_name,
            deliverylicence=delivery_licence,
            organization_country_name=country.country_code_alpha2,
            year=delivery_licence.year,
            lic_use_kind=lic_use_kind,
            lic_use_desc=licence_details.lic_use_desc,
            s_orig_country_name=s_country.country_code_alpha2,
            lic_type=licence_details.lic_type,
            quantity=0,
        )
        try:
            db.session.add(substance)
        except:
            db.session.expire_all()
            db.session.add(substance)
        db.session.commit()
    return substance


def aggregate_licence_to_substance(delivery_licence, year):
    substances = Substance.query.filter_by(year=year, deliverylicence=delivery_licence)
    for substance in substances:
        quantity = sum([licence.net_mass for licence in substance.licences.all()])
        if substance.lic_use_desc == "laboratory uses":
            substance.quantity = round(quantity, 7)
        else:
            substance.quantity = int(ceil(quantity))
        db.session.add(substance)
        db.session.commit()


def aggregate_licences_to_undertakings(data):
    undertakings = {}
    not_found_undertakings = []
    for licence in data:
        undertaking_obj = Undertaking.query.filter_by(
            external_id=licence["organizationId"], domain="ODS"
        ).first()
        if not undertaking_obj:
            if licence["organizationId"] not in not_found_undertakings:
                external_id = licence["organizationId"]
                message = (
                    f"Undertaking {external_id} is not present in the application."
                )
                current_app.logger.error(message)
                not_found_undertakings.append(licence["organizationId"])
            continue
        undertaking = undertakings.get(undertaking_obj.external_id, None)
        if not undertaking:
            updated_since = translate_date(licence["licenceUpdateDate"])
            undertakings[undertaking_obj.external_id] = {
                "updated_since": updated_since,
                "licences": [],
            }
            undertaking = undertakings[undertaking_obj.external_id]
        else:
            updated_since = translate_date(licence["licenceUpdateDate"])
            undertaking_updated_since = undertakings[undertaking_obj.external_id][
                "updated_since"
            ]
            undertakings[undertaking_obj.external_id]["updated_since"] = (
                updated_since
                if updated_since > undertaking_updated_since
                else undertaking_updated_since
            )
        undertaking["licences"].append(licence)
    return undertakings

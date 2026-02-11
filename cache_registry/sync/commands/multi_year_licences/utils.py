from flask import current_app

from cache_registry.models import (
    DetailedUse,
    SubstanceNomenclature,
)

CUSTOMS_PROCEDURE_NUMBER_TO_LIC_USE_KIND_CONVERSION = {
    40: "free circulation import",
    42: "VAT-exempt free circulation",
    51: "inward processing",
    53: "temporary admission",
    61: "end-use / outward processing",
    71: "warehousing",
    78: "free zones",
    10: "export",
    31: "re-export and transit",
}


def get_substances_from_cn_code(licence_object_id, cn_code, substances):
    if not substances:
        if not cn_code.substances:
            current_app.logger.warning(
                f"""No substances found on licence ID {licence_object_id} to match CN code {cn_code.code}."""
            )
            return None
        return cn_code.substances
    intersection_substances = set(cn_code.substances).intersection(set(substances))
    if not intersection_substances:
        current_app.logger.warning(
            f"""No intersection found between substances from 
                CN code {cn_code.code} and substances {[x.chemical_name for x in substances]} from 
                licence ID {licence_object_id}."""
        )
        return None
    return SubstanceNomenclature.query.filter(
        SubstanceNomenclature.id.in_(
            [substance.id for substance in intersection_substances]
        )
    )


def get_lic_use_desc_and_lic_type_from_detailed_uses(licence_object):
    detailes_uses_data = []
    for detail_use in licence_object.detailed_uses:
        if not (detail_use.lic_use_desc, detail_use.lic_type) in detailes_uses_data:
            detailes_uses_data.append((detail_use.lic_use_desc, detail_use.lic_type))
    if not detailes_uses_data:
        if licence_object.licence_type in ["EHCF", "EHCP", "EHCO"]:
            return [("", "export")]
        if licence_object.licence_type in ["IHCF"]:
            return [("", "import")]
        detailed_use = DetailedUse.query.filter_by(
            licence_type=licence_object.licence_type,
            obsolete=False,
        ).first()
        if detailed_use:
            detailes_uses_data.append(
                (detailed_use.lic_use_desc, detailed_use.lic_type)
            )
    return detailes_uses_data

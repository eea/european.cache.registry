from flask import current_app

from cache_registry.models import (
    SubstanceNomenclature,
)


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

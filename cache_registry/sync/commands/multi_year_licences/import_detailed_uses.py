import pandas

from cache_registry.models import (
    DetailedUse,
    db,
)
from cache_registry.sync import sync_manager


@sync_manager.command("import_detailed_uses")
def import_combined_nomenclature():
    file_path = "cache_registry/fixtures/multi_year_licenses/detailed_uses.xlsx"
    df = pandas.read_excel(file_path)

    for _, row in df.iterrows():
        detailed_use = DetailedUse.query.filter_by(
            short_code=row["short_code"],
            code=row["code"],
        ).first()
        if not detailed_use:
            detailed_use = DetailedUse(
                short_code=row["short_code"],
                code=row["code"],
                lic_use_desc=row["lic_use_desc"],
                lic_type=row["lic_type"],
            )
            db.session.add(detailed_use)
            db.session.commit()
        else:
            detailed_use.lic_use_desc = row["lic_use_desc"]
            detailed_use.lic_type = row["lic_type"]
            db.session.commit()
